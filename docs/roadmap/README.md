# barasseur roadmap

This roadmap takes barasseur from the current skeleton (v0.1.0) to a complete,
everyday coding agent. It is written for a first agent project: every task says
**what** to build, **why**, **which files** to touch, **the steps**, and **how to
know it is done**.

## How to use this roadmap

- Do the sprints **in order**. Each sprint builds on the previous one.
- Do the tasks inside a sprint in order too, unless a task says otherwise.
- One task = one branch = one or a few commits. Example:
  `git switch -c s1-search-tool`, work, `scripts/check.sh`, commit, push,
  open a pull request to `main`, merge it.
- Every task ends with a **Done when** list. Do not move on until every box is true.
- Every task that adds code also adds at least one test in `tests/`. The tests use
  the fake Gemini client already in `tests/test_agent.py`, so they cost nothing.
- Update `CHANGELOG.md` at the end of each sprint and bump the version in
  `pyproject.toml` and `barasseur/__init__.py`.

## The sprints

| Sprint | Theme | Result at the end | Version |
|---|---|---|---|
| [0](sprint-0-foundations.md) | Foundations | You can run the agent on a real project and you understand every line of it | 0.1.x |
| [1](sprint-1-tools.md) | Better tools | The agent can search code, see diffs and work on big projects | 0.2.0 |
| [2](sprint-2-context-and-cost.md) | Context and cost | Long sessions do not explode in cost; project rules and saved sessions | 0.3.0 |
| [3](sprint-3-user-experience.md) | User experience | Streaming answers, colors, slash commands, config file | 0.4.0 |
| [4](sprint-4-safety.md) | Safety | Permission modes, command allow/deny lists, undo with git checkpoints | 0.5.0 |
| [5](sprint-5-reliability-and-evals.md) | Reliability and evaluation | Retries, logs, and a benchmark that measures how good the agent is | 0.6.0 |
| [6](sprint-6-advanced-agent.md) | Advanced agent | Planning, sub-agents, web access, MCP tools | 0.7.0 |
| [7](sprint-7-release.md) | Release | Installable with one command, documented, version 1.0.0 | 1.0.0 |

## Vocabulary

- **Model**: Gemini, the AI that reads text and writes text.
- **Tool**: a Python function the model can ask barasseur to run (`read_file`, ...).
- **Function call**: the structured message the model sends to ask for a tool.
- **Turn / step**: one request to Gemini and its answer. One user question can take many steps.
- **History / context**: everything sent to the model at each step (your questions,
  its answers, tool results). Its size, in **tokens**, decides the cost.
- **Token**: a piece of a word. Roughly 1 token = 4 characters of English text.
- **System prompt**: the fixed instructions sent first at every step (`SYSTEM_PROMPT` in `agent.py`).

Read `COMMENT_CA_MARCHE.md` first if any of this is unclear.
