"""Tests de la boucle d'agent avec un faux client Gemini (aucun appel réseau)."""

from types import SimpleNamespace

from google.genai import types

from barasseur.agent import Agent
from barasseur.tools import Toolbox


def call(name, **args):
    return types.Content(
        role="model", parts=[types.Part(function_call=types.FunctionCall(name=name, args=args))]
    )


def text(t):
    return types.Content(role="model", parts=[types.Part(text=t)])


def make_agent(tmp_path, replies, confirm=lambda q: True):
    class FakeModels:
        def generate_content(self, **kw):
            return types.GenerateContentResponse(candidates=[types.Candidate(content=replies.pop(0))])

    agent = Agent(Toolbox(tmp_path, confirm), model="fake", api_key="fake")
    agent.client = SimpleNamespace(models=FakeModels())
    return agent


def tool_results(agent):
    return [p.function_response.response for c in agent.history for p in c.parts or [] if p.function_response]


def test_lit_puis_modifie(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n")
    agent = make_agent(
        tmp_path,
        [
            call("read_file", path="a.py"),
            call("edit_file", path="a.py", old="x = 1", new="x = 2"),
            text("Fini."),
        ],
    )
    assert agent.ask("change x") == "Fini."
    assert (tmp_path / "a.py").read_text() == "x = 2\n"


def test_refuse_chemin_hors_dossier(tmp_path):
    agent = make_agent(tmp_path, [call("read_file", path="../../etc/passwd"), text("ok")])
    agent.ask("lis")
    assert "hors du dossier" in tool_results(agent)[0]["error"]


def test_respecte_le_refus_utilisateur(tmp_path):
    agent = make_agent(
        tmp_path, [call("write_file", path="b.txt", content="hi"), text("ok")], confirm=lambda q: False
    )
    agent.ask("écris")
    assert not (tmp_path / "b.txt").exists()
    assert tool_results(agent)[0]["result"] == "Refusé par l'utilisateur."


def test_outil_inconnu(tmp_path):
    agent = make_agent(tmp_path, [call("_path", rel="x"), text("ok")])
    agent.ask("x")
    assert "inconnu" in tool_results(agent)[0]["error"]
