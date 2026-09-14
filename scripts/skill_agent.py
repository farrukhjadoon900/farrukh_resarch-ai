#!/usr/bin/env python3
"""
scripts/skill_agent.py — Jarvis skill-sync agent (self-contained, cloud-friendly).

Runs entirely inside GitHub Actions (or locally if you ever want to).
One run:
  1. clones each repo in REPOS (shallow, temp dir, discarded after)
  2. finds every SKILL.md inside each one
  3. skips any skill slug that already exists under skills/
  4. reshapes new ones via Groq (free tier) into skills/_template's format
  5. writes result to skills/<slug>/SKILL.md

The workflow file (.github/workflows/skill-agent.yml) handles git commit + push
after this script runs — this script only ever writes local files.
"""

import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
TEMPLATE_PATH = SKILLS_DIR / "_template" / "SKILL.md"

# Add more (category, "owner/repo") lines here any time — next run picks them up.
REPOS = [
    ("trading", "alpacahq/alpaca-skills"),
    ("trading", "marian2js/trading-skills"),
    ("trading", "agiprolabs/claude-trading-skills"),
    ("trading", "mphinance/alpha-skills"),
    ("trading", "TradersPost/pinescript-agents"),
    ("automation", "zapier/agent-skills"),
    ("automation", "czlonkowski/n8n-skills"),
    ("coding", "anthropics/skills"),
    ("coding", "VoltAgent/awesome-agent-skills"),
]

BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
API_KEY = os.getenv("groq_api_key") or os.getenv("GROQ_API_KEY")

SKIP_SLUGS = {"_template", "example-skill"}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return s.strip("-")[:64] or "untitled-skill"


def existing_slugs() -> set[str]:
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}


def call_groq(system_prompt: str, user_prompt: str) -> str:
    if not API_KEY:
        print("ERROR: groq_api_key / GROQ_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def reshape(raw_text: str, template_text: str, source_repo: str) -> str:
    system_prompt = (
        "You reshape raw agent-skill documentation into a strict target template. "
        "Rules:\n"
        "1. Output ONLY the final markdown — no preamble, no code fences.\n"
        "2. Match the template's section headers and YAML frontmatter keys exactly: "
        "name, description, metadata.version (quoted string, start at \"1.0\"), "
        "metadata.last_updated (quoted YYYY-MM-DD), metadata.author (always 'jarvis').\n"
        "3. Preserve every genuinely useful instruction, workflow step, and warning "
        "from the source — condense wording, never invent new claims.\n"
        "4. If a section has no real source material, write '(not specified in source)'.\n"
        "5. In Sources, cite the origin repo and note if vendor-specific steps need replacing."
    )
    user_prompt = (
        f"TEMPLATE:\n{template_text}\n\n"
        f"ORIGIN REPO: {source_repo}\n\n"
        f"RAW SOURCE:\n{raw_text}\n\nReshape now."
    )
    out = call_groq(system_prompt, user_prompt)
    out = re.sub(r"^```(?:markdown|md)?\n", "", out.strip())
    out = re.sub(r"\n```$", "", out)
    return out.strip()


def main() -> None:
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: template missing at {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(1)
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    known = existing_slugs()

    added = 0
    for category, repo in REPOS:
        print(f"== {category}/{repo}")
        with tempfile.TemporaryDirectory() as tmp:
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", tmp],
                    check=True, capture_output=True, timeout=120,
                )
            except Exception as e:
                print(f"   [fail] clone error: {e}")
                continue

            for skill_file in Path(tmp).rglob("SKILL.md"):
                skill_folder = skill_file.parent.name
                slug = slugify(skill_folder)
                if slug in SKIP_SLUGS or slug in known:
                    continue

                raw_text = skill_file.read_text(encoding="utf-8", errors="ignore")
                print(f"   -> reshaping {slug}")
                try:
                    reshaped = reshape(raw_text, template_text, repo)
                except Exception as e:
                    print(f"      [fail] reshape error: {e}")
                    continue

                out_dir = SKILLS_DIR / slug
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "SKILL.md").write_text(reshaped + "\n", encoding="utf-8")
                known.add(slug)
                added += 1
                time.sleep(1)  # gentle on the free API tier

    print(f"\nDone. {added} new skill(s) added under skills/.")


if __name__ == "__main__":
    main()
