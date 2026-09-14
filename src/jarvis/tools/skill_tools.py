"""Tools for listing, reading, and writing skill packages under skills/."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from crewai.tools import tool

from jarvis.config import SKILLS_DIR


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:64] or "untitled-skill"


def _skill_path(slug: str) -> Path:
    return SKILLS_DIR / slug / "SKILL.md"


@tool("list_skills")
def list_skills() -> str:
    """List all learned skills (directory name + description from frontmatter)."""
    if not SKILLS_DIR.exists():
        return "No skills directory yet."
    rows: list[str] = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        skill_md = d / "SKILL.md"
        desc = "(no SKILL.md)"
        if skill_md.exists():
            text = skill_md.read_text(encoding="utf-8")
            m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            if m:
                desc = m.group(1).strip().strip("\"'")
        rows.append(f"- {d.name}: {desc}")
    return "\n".join(rows) if rows else "No skills learned yet."


@tool("read_skill")
def read_skill(skill_name: str) -> str:
    """Read the full SKILL.md for a skill by name/slug."""
    slug = _slugify(skill_name)
    path = _skill_path(slug)
    if not path.exists():
        for d in SKILLS_DIR.iterdir():
            if d.is_dir() and skill_name.lower() in d.name:
                path = d / "SKILL.md"
                break
    if not path.exists():
        return f"Skill not found: {skill_name}. Use list_skills first."
    return path.read_text(encoding="utf-8")


@tool("write_skill")
def write_skill(skill_name: str, content: str) -> str:
    """
    Create or overwrite a skill package.
    skill_name: short name e.g. 'react-performance'
    content: full SKILL.md body INCLUDING YAML frontmatter (--- ... ---).
    """
    slug = _slugify(skill_name)
    dir_path = SKILLS_DIR / slug
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / "references").mkdir(exist_ok=True)

    body = content.strip()
    if not body.startswith("---"):
        body = (
            f"---\nname: {slug}\n"
            f"description: Expert guidance for {skill_name}.\n"
            f"metadata:\n  version: \"1.0\"\n  last_updated: \"{date.today().isoformat()}\"\n"
            f"  author: jarvis\n---\n\n{body}"
        )
    else:
        if "last_updated" not in body.split("---", 2)[1]:
            body = body.replace(
                "---\n",
                f"---\nmetadata:\n  last_updated: \"{date.today().isoformat()}\"\n",
                1,
            )

    path = dir_path / "SKILL.md"
    path.write_text(body + "\n", encoding="utf-8")
    return f"Wrote skill: {path.relative_to(SKILLS_DIR.parent)} ({len(body)} chars)"


@tool("append_skill_reference")
def append_skill_reference(skill_name: str, filename: str, content: str) -> str:
    """Append a reference note under skills/<slug>/references/<filename>."""
    slug = _slugify(skill_name)
    ref_dir = SKILLS_DIR / slug / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    if not safe.endswith(".md"):
        safe += ".md"
    path = ref_dir / safe
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return f"Wrote reference: {path}"
