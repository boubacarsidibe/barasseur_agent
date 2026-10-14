# barasseur_agent

Agent de code personnel en ligne de commande, basé sur l'API Gemini de Google.
Le code est à toi (aucune dépendance à part le SDK officiel `google-genai`), le
modèle est appelé avec ta propre clé API.

## « Gemini edu » : ce que ça veut dire ici

« Gemini for Education » est l'application Gemini incluse dans Google Workspace
for Education (comptes d'école/université). Ce n'est pas une API : un agent ne
peut pas s'y brancher. Pour un agent, on utilise **l'API Gemini** (Google AI
Studio). Attention : les comptes Workspace for Education reçoivent souvent des
erreurs 403 sur l'API ; crée la clé avec un compte Google personnel.

## Architecture

```
 terminal (__main__.py)
   │  question de l'utilisateur, confirmations o/N
   ▼
 Agent (agent.py) ── boucle : modèle → appels d'outils → résultats → modèle …
   │                         (s'arrête quand le modèle répond en texte, max 30 étapes)
   ├──► API Gemini (google-genai)
   ▼
 Toolbox (tools.py) : list_files · read_file · edit_file · write_file · run_command
   confiné au dossier de travail, sorties tronquées
```

Choix d'optimisation déjà en place :

- **Coût** : modèle `gemini-2.5-flash` par défaut (changeable avec `--model` ou
  `BARASSEUR_MODEL`) ; prompt système et outils constants pour profiter du cache
  implicite de Gemini ; sorties d'outils tronquées à 12 000 caractères ;
  `read_file` par plage de lignes ; `edit_file` (remplacement ciblé) préféré à
  la réécriture complète.
- **Sécurité** : chemins confinés au dossier de travail ; confirmation avant
  chaque écriture et chaque commande (désactivable avec `--yes`).
- **Fiabilité** : les erreurs d'outils sont renvoyées au modèle pour qu'il se
  corrige ; nombre d'étapes plafonné.

## Installation et usage

```bash
cd barasseur_agent
python -m pip install -e .
export GEMINI_API_KEY=...        # https://aistudio.google.com/apikey
barasseur --dir ~/mon-projet     # mode interactif
barasseur --dir ~/mon-projet "ajoute des tests pour utils.py"
```

## Documentation

- [COMMENT_CA_MARCHE.md](COMMENT_CA_MARCHE.md) : fonctionnement interne d'un agent de code
- [CONTRIBUTING.md](CONTRIBUTING.md) : règles et contrôles appliqués à chaque push
- [SECURITY.md](SECURITY.md) : clé API et précautions
- [CHANGELOG.md](CHANGELOG.md) : historique des versions

## Développement

```bash
python -m pip install -e ".[dev]"
git config core.hooksPath .githooks   # active les contrôles avant chaque push
scripts/check.sh                      # secrets, ruff, tests
```

## Prochaines étapes possibles

1. Compactage de l'historique quand la conversation devient longue.
2. Outil `search` (ripgrep) pour chercher dans le code sans tout lire.
3. Fichier `BARASSEUR.md` dans le projet cible, lu au démarrage comme consignes.
4. Streaming des réponses et affichage des diffs en couleur.
