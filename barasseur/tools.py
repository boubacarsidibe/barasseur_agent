"""Outils exposés au modèle. Chaque outil = un schéma JSON + une fonction Python.

Toutes les opérations sont confinées au dossier de travail (WORKDIR) et les
sorties sont tronquées pour économiser des tokens.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

MAX_OUTPUT = 12_000  # caractères renvoyés au modèle par appel d'outil


class ToolError(Exception):
    pass


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text
    half = MAX_OUTPUT // 2
    return f"{text[:half]}\n… [{len(text) - MAX_OUTPUT} caractères coupés] …\n{text[-half:]}"


class Toolbox:
    def __init__(self, workdir: Path, confirm):
        self.workdir = workdir.resolve()
        self.confirm = confirm  # fonction(str) -> bool, demande l'accord de l'utilisateur

    def _path(self, rel: str) -> Path:
        p = (self.workdir / rel).resolve()
        if not p.is_relative_to(self.workdir):
            raise ToolError(f"Chemin hors du dossier de travail : {rel}")
        return p

    # --- outils -----------------------------------------------------------

    def list_files(self, path: str = ".") -> str:
        root = self._path(path)
        skip = {".git", "node_modules", "__pycache__", ".venv", "venv"}
        out = []
        for p in sorted(root.rglob("*")):
            if any(part in skip for part in p.relative_to(root).parts):
                continue
            if p.is_file():
                out.append(str(p.relative_to(self.workdir)))
            if len(out) >= 500:
                out.append("… (liste tronquée à 500 fichiers)")
                break
        return "\n".join(out) or "(vide)"

    def read_file(self, path: str, start: int = 1, end: int | None = None) -> str:
        lines = self._path(path).read_text(errors="replace").splitlines()
        end = end or len(lines)
        body = "\n".join(f"{i:>5}  {line}" for i, line in enumerate(lines[start - 1 : end], start))
        return _truncate(body)

    def write_file(self, path: str, content: str) -> str:
        p = self._path(path)
        if not self.confirm(f"Écrire {path} ({len(content)} caractères) ?"):
            return "Refusé par l'utilisateur."
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return f"{path} écrit."

    def edit_file(self, path: str, old: str, new: str) -> str:
        p = self._path(path)
        text = p.read_text()
        n = text.count(old)
        if n != 1:
            raise ToolError(f"`old` doit apparaître exactement une fois (trouvé {n} fois).")
        if not self.confirm(f"Modifier {path} ?\n--- avant\n{old}\n--- après\n{new}"):
            return "Refusé par l'utilisateur."
        p.write_text(text.replace(old, new))
        return f"{path} modifié."

    def run_command(self, command: str, timeout: int = 120) -> str:
        if not self.confirm(f"Exécuter : {command}"):
            return "Refusé par l'utilisateur."
        r = subprocess.run(
            command,
            shell=True,
            cwd=self.workdir,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return _truncate(f"code de sortie {r.returncode}\n{r.stdout}{r.stderr}")


SCHEMAS = [
    {
        "name": "list_files",
        "description": "Liste les fichiers sous un dossier (récursif).",
        "parameters_json_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Dossier relatif, '.' par défaut"}},
        },
    },
    {
        "name": "read_file",
        "description": "Lit un fichier texte avec numéros de ligne. Utilise start/end pour les gros fichiers.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start": {"type": "integer"},
                "end": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Crée ou remplace entièrement un fichier.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Remplace un extrait exact (unique) d'un fichier. Préférer à write_file pour les petites modifications.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old": {"type": "string"},
                "new": {"type": "string"},
            },
            "required": ["path", "old", "new"],
        },
    },
    {
        "name": "run_command",
        "description": "Exécute une commande shell dans le dossier de travail (tests, build, git…).",
        "parameters_json_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}, "timeout": {"type": "integer"}},
            "required": ["command"],
        },
    },
]
