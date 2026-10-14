# Règles de push

Chaque push passe par les mêmes contrôles, en local puis sur GitHub.

## Les contrôles (`scripts/check.sh`)

1. **Secrets** : refuse le push si une clé Google (`AIza…`), une clé privée ou un
   fichier `.env` est suivi par git.
2. **Lint et format** : `ruff check` et `ruff format --check`.
3. **Tests** : `pytest` (avec un faux client Gemini, sans appel réseau ni clé).

## Où ils s'appliquent

| Endroit | Fichier | Effet |
|---|---|---|
| Ta machine, avant chaque `git push` | `.githooks/pre-push` | le push est bloqué si un contrôle échoue |
| GitHub, à chaque push et PR | `.github/workflows/checks.yml` | la CI passe au rouge si un contrôle échoue |

## Mise en place après un clone (une seule fois)

```bash
python -m pip install -e ".[dev]"
git config core.hooksPath .githooks
```

## Avant de pousser

- Lance `scripts/check.sh` ; corrige avec `ruff format .` et `ruff check --fix .`.
- Messages de commit courts, à l'impératif : `ajoute l'outil search`, `corrige la troncature`.
- Toute nouvelle fonctionnalité arrive avec au moins un test dans `tests/`.
- Mets à jour `CHANGELOG.md`.
