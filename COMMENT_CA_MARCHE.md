# Comment fonctionne un agent de code (et barasseur en particulier)

## 1. Le modèle ne fait que produire du texte

Gemini, GPT ou Llama ne « font » rien eux-mêmes : ils reçoivent du texte et
renvoient du texte. Ils ne peuvent ni lire ton disque ni lancer une commande.
Tout ce qui ressemble à une action est fait par **ton programme**, l'agent.

## 2. Les outils : un menu proposé au modèle

À chaque requête, barasseur envoie au modèle la liste de ses outils avec leur
description et leurs paramètres (`SCHEMAS` dans `tools.py`), par exemple :

> `read_file(path, start, end)` : lit un fichier texte avec numéros de ligne.

Quand le modèle juge qu'il a besoin d'un outil, au lieu d'écrire une phrase, il
répond par un **appel de fonction** structuré :

```json
{ "function_call": { "name": "read_file", "args": { "path": "app.py" } } }
```

C'est une demande, pas une exécution. Le modèle attend la réponse.

## 3. La boucle : le cœur de l'agent

Toute l'« intelligence agentique » tient dans une boucle (`Agent.ask` dans `agent.py`) :

```
historique = [ta question]
répéter (30 fois max) :
    réponse = Gemini(prompt système + outils + historique)
    si la réponse est du texte simple  -> c'est fini, on l'affiche
    sinon, pour chaque appel d'outil :
        exécuter l'outil en Python (après ta confirmation si c'est risqué)
        ajouter le résultat à l'historique
```

Exemple réel pour « corrige le test qui échoue » :

| Tour | Le modèle demande | barasseur renvoie |
|---|---|---|
| 1 | `run_command("pytest")` | `1 failed: test_total ... assert 9 == 10` |
| 2 | `read_file("calc.py")` | le code avec numéros de ligne |
| 3 | `edit_file("calc.py", old="range(n)", new="range(n+1)")` | `calc.py modifié.` |
| 4 | `run_command("pytest")` | `1 passed` |
| 5 | texte : « Corrigé : la boucle s'arrêtait un cran trop tôt. » | fin |

Le modèle ne voit que ce qu'on lui renvoie. Il « explore » le projet petit à
petit, exactement comme un développeur qui ouvre des fichiers.

## 4. La mémoire = l'historique renvoyé à chaque fois

Le modèle n'a aucune mémoire entre deux appels. barasseur renvoie **toute la
conversation** (questions, appels d'outils, résultats) à chaque tour
(`self.history`). D'où deux conséquences :

- **le coût augmente à chaque tour**, car on repaie les tokens de l'historique ;
- **la fenêtre de contexte a une limite** : une très longue session finit par
  déborder. La solution classique est de « compacter » : résumer les vieux
  échanges (c'est une des prochaines étapes du README).

## 5. Le prompt système : la personnalité et la méthode

`SYSTEM_PROMPT` dans `agent.py` dit au modèle qui il est et comment travailler :
explorer d'abord, modifier par petites touches, vérifier avec les tests. Changer
ce texte change beaucoup le comportement de l'agent : c'est le premier levier
d'optimisation, et il est entièrement à toi.

## 6. Où se trouve l'optimisation

| Levier | Dans barasseur |
|---|---|
| Moins de tokens envoyés | sorties d'outils tronquées, `read_file` par plages, `edit_file` au lieu de réécrire tout le fichier |
| Tokens moins chers | modèle `flash` par défaut ; prompt système et outils identiques à chaque appel, donc mis en cache par Gemini |
| Moins de tours | prompt système qui impose une méthode ; bonnes descriptions d'outils |
| Pas de catastrophe | dossier confiné, confirmation avant écriture et commande, 30 tours max |
| Auto-correction | une erreur d'outil est renvoyée au modèle au lieu de planter, il réessaie autrement |

## 7. Ce qui distingue les gros agents (Gemini CLI, Cursor, Aider…)

Ils reposent sur la même boucle. Ils ajoutent surtout :

- plus d'outils (recherche dans le code, web, navigateur) ;
- la compaction automatique de l'historique ;
- des sous-agents, c'est-à-dire un agent qui lance d'autres boucles pour des sous-tâches ;
- un fichier de consignes par projet (`GEMINI.md`, `AGENTS.md`) lu au démarrage ;
- une gestion fine des permissions et un affichage des diffs.

barasseur peut grandir dans cette direction pas à pas, sans changer son cœur.
