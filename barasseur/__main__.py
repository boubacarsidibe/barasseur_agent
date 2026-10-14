"""Point d'entrée : `python -m barasseur [--dir DOSSIER] [--model MODELE] [--yes]`."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .agent import Agent
from .tools import Toolbox

DEFAULT_MODEL = os.environ.get("BARASSEUR_MODEL", "gemini-2.5-flash")


def main() -> None:
    ap = argparse.ArgumentParser(prog="barasseur", description="Agent de code basé sur Gemini")
    ap.add_argument("--dir", default=".", help="dossier de travail (par défaut : courant)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--yes", action="store_true", help="ne pas demander de confirmation (prudence)")
    ap.add_argument("prompt", nargs="*", help="tâche unique ; sans argument, mode interactif")
    args = ap.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        sys.exit("Définis GEMINI_API_KEY (clé créée sur https://aistudio.google.com/apikey).")

    def confirm(question: str) -> bool:
        if args.yes:
            return True
        return input(f"\n{question}\n[o/N] ").strip().lower() in {"o", "oui", "y", "yes"}

    def on_tool(name: str, a: dict) -> None:
        preview = ", ".join(f"{k}={str(v)[:60]!r}" for k, v in a.items())
        print(f"  ⚙ {name}({preview})", file=sys.stderr)

    agent = Agent(Toolbox(Path(args.dir), confirm), model=args.model)

    if args.prompt:
        print(agent.ask(" ".join(args.prompt), on_tool))
        return

    print(f"barasseur · {args.model} · {Path(args.dir).resolve()}  (Ctrl-D pour quitter)")
    while True:
        try:
            prompt = input("\n› ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\nTokens utilisés : {agent.tokens_used}")
            return
        if prompt:
            print(agent.ask(prompt, on_tool))


if __name__ == "__main__":
    main()
