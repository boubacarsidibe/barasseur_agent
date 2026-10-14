#!/usr/bin/env bash
# Contrôles exécutés avant chaque push (hook pre-push) et dans la CI GitHub.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "▶ 1/3 Recherche de secrets"
# Clés Google (AIza…), clés privées, fichiers .env suivis par git.
if git grep -nIE 'AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----' -- . ':!scripts/check.sh'; then
  echo "✗ Secret détecté : retire-le avant de pousser." >&2; exit 1
fi
if git ls-files | grep -E '(^|/)\.env$'; then
  echo "✗ Un fichier .env est suivi par git." >&2; exit 1
fi

echo "▶ 2/3 Lint et format (ruff)"
ruff check .
ruff format --check .

echo "▶ 3/3 Tests (pytest)"
python -m pytest -q

echo "✓ Tous les contrôles sont passés."
