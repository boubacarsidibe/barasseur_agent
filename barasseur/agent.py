"""Boucle d'agent : le modèle propose des appels d'outils, on les exécute, on renvoie
les résultats, jusqu'à ce qu'il réponde en texte."""

from __future__ import annotations

from google import genai
from google.genai import types

from .tools import SCHEMAS, Toolbox, ToolError

SYSTEM_PROMPT = """Tu es barasseur, un agent de code. Tu travailles dans le dossier de \
l'utilisateur avec tes outils. Méthode : explore d'abord (list_files, read_file), \
puis modifie avec edit_file plutôt que write_file, puis vérifie avec run_command \
(tests, lint). Sois bref dans tes réponses. Réponds dans la langue de l'utilisateur."""

MAX_STEPS = 30  # garde-fou contre les boucles infinies


class Agent:
    def __init__(self, toolbox: Toolbox, model: str, api_key: str | None = None):
        self.client = genai.Client(api_key=api_key)  # sinon lit GEMINI_API_KEY
        self.toolbox = toolbox
        self.model = model
        self.history: list[types.Content] = []
        # Prompt système et outils constants -> préfixe stable, éligible au cache implicite.
        self.config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(function_declarations=[types.FunctionDeclaration(**s) for s in SCHEMAS])],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        self.tokens_used = 0

    def _call_tool(self, name: str, args: dict) -> dict:
        fn = getattr(self.toolbox, name, None)
        if fn is None or name.startswith("_"):
            return {"error": f"Outil inconnu : {name}"}
        try:
            return {"result": fn(**args)}
        except ToolError as e:
            return {"error": str(e)}
        except Exception as e:  # noqa: BLE001 - le modèle doit voir l'erreur pour se corriger
            return {"error": f"{type(e).__name__}: {e}"}

    def ask(self, prompt: str, on_tool=None) -> str:
        self.history.append(types.Content(role="user", parts=[types.Part(text=prompt)]))
        for _ in range(MAX_STEPS):
            resp = self.client.models.generate_content(
                model=self.model, contents=self.history, config=self.config
            )
            if resp.usage_metadata:
                self.tokens_used += resp.usage_metadata.total_token_count or 0
            content = resp.candidates[0].content
            self.history.append(content)  # garde aussi les thought_signature
            calls = [p.function_call for p in content.parts or [] if p.function_call]
            if not calls:
                return resp.text or ""
            parts = []
            for call in calls:
                args = dict(call.args or {})
                if on_tool:
                    on_tool(call.name, args)
                parts.append(
                    types.Part.from_function_response(
                        name=call.name, response=self._call_tool(call.name, args)
                    )
                )
            self.history.append(types.Content(role="user", parts=parts))
        return f"Arrêt après {MAX_STEPS} étapes sans réponse finale."
