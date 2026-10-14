# Sécurité

- **Clé API** : uniquement dans la variable d'environnement `GEMINI_API_KEY` ou dans
  un fichier `.env` (ignoré par git, voir `.env.example`). Jamais dans le code.
  Le contrôle de push bloque les clés `AIza…` qui seraient commitées.
- **Clé exposée par erreur** : révoque-la tout de suite sur
  https://aistudio.google.com/apikey, puis crée-en une autre. Supprimer le commit
  ne suffit pas.
- **Ce que l'agent peut faire** : il est confiné au dossier passé avec `--dir` et
  demande confirmation avant toute écriture ou commande. L'option `--yes` retire
  ces confirmations : à réserver à un dossier jetable.
- **Données envoyées** : le contenu des fichiers lus par l'agent est envoyé à
  l'API Gemini de Google. Ne l'utilise pas sur des fichiers confidentiels.
