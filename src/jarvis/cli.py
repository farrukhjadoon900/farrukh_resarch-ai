from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from jarvis.config import MODEL, ROOT, SKILLS_DIR, require_api_key
from jarvis.crews import run_jarvis
from jarvis.tools.skill_tools import list_skills

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="Jarvis — Groq-powered multi-agent assistant with skill learning",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ask = sub.add_parser("ask", help="Ask Jarvis anything")
    p_ask.add_argument("prompt", nargs="+", help="Your command / question")
    p_ask.add_argument(
        "--mode",
        choices=["auto", "learn", "answer", "research"],
        default="auto",
        help="Force intent (default: auto)",
    )

    p_learn = sub.add_parser("learn", help="Research a topic and save as skill")
    p_learn.add_argument("topic", nargs="+", help="Skill / domain to learn")

    sub.add_parser("skills", help="List learned skills")

    p_repl = sub.add_parser("chat", help="Interactive REPL")
    p_repl.add_argument(
        "--mode",
        choices=["auto", "learn", "answer", "research"],
        default="auto",
    )

    args = parser.parse_args(argv)

    try:
        require_api_key()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        return 1

    if args.cmd == "skills":
        console.print(Panel(list_skills.run(), title="Skills", border_style="cyan"))
        return 0

    if args.cmd == "learn":
        topic = " ".join(args.topic)
        prompt = (
            f"Learn the skill/domain: {topic}. "
            "Research thoroughly and write/update SKILL.md so future answers "
            "are expert-level (senior practitioner quality)."
        )
        console.print(f"[bold]Learning:[/bold] {topic}  [dim](model={MODEL})[/dim]")
        out = run_jarvis(prompt, mode="learn")
        console.print(Markdown(out))
        return 0

    if args.cmd == "ask":
        prompt = " ".join(args.prompt)
        console.print(f"[bold]Jarvis[/bold] [dim]({MODEL})[/dim]")
        out = run_jarvis(prompt, mode=args.mode)
        console.print(Markdown(out))
        return 0

    if args.cmd == "chat":
        console.print(
            Panel(
                f"Jarvis REPL — model={MODEL}\nskills={SKILLS_DIR}\n"
                "Commands: /skills  /learn <topic>  /quit",
                title="Jarvis",
                border_style="magenta",
            )
        )
        while True:
            try:
                line = console.input("[bold cyan]you>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\nBye.")
                return 0
            if not line:
                continue
            if line in {"/quit", "/exit", "quit", "exit"}:
                console.print("Bye.")
                return 0
            if line == "/skills":
                console.print(list_skills.run())
                continue
            if line.startswith("/learn "):
                topic = line[len("/learn ") :].strip()
                prompt = (
                    f"Learn the skill/domain: {topic}. "
                    "Research and persist SKILL.md at senior level."
                )
                out = run_jarvis(prompt, mode="learn")
            else:
                out = run_jarvis(line, mode=args.mode)
            console.print(Markdown(out))
            console.print()
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
