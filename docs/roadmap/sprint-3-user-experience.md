# Sprint 3: User experience

Goal: barasseur is pleasant to use every day: you see the answer as it is
written, outputs are colored, you control it with commands, and settings live
in a config file.

---

## Task 3.1: Split the code into layers

**Why**: the terminal display is mixed into `__main__.py`. Separating "agent
logic" from "display" lets you later add other interfaces (web, editor) without
touching the agent.

**Files**: new `barasseur/ui.py`, `barasseur/events.py`; `agent.py`, `__main__.py`.

**Steps**
1. Define events in `events.py` as dataclasses: `TextDelta(text)`,
   `ToolStart(name, args)`, `ToolEnd(name, result, error)`, `TurnEnd(usage)`.
2. Make `Agent.ask` a generator that `yield`s events instead of returning a string.
3. `ui.py` consumes events and prints. `confirm` stays a callback given to `Toolbox`.
4. Update tests to collect events from the generator.

**Done when**
- [ ] `agent.py` contains no `print` and no `input`.

---

## Task 3.2: Streaming answers

**Why**: waiting 20 seconds for a full answer feels broken. Streaming prints text
as it arrives.

**Files**: `barasseur/agent.py`.

**Steps**
1. Replace `generate_content` with `generate_content_stream`. Iterate on chunks.
2. For each chunk, `yield TextDelta` for text parts; collect function-call parts.
3. Rebuild the full model `Content` from all chunks (text joined, function calls
   kept, `thought_signature` kept) and append it to history once the stream ends.
4. Usage metadata comes on the last chunk.

**Done when**
- [ ] Text appears word by word; tool calls still work; tests pass.

---

## Task 3.3: Rich terminal output

**Why**: colors and markdown make long answers readable.

**Files**: `barasseur/ui.py`, `pyproject.toml` (add `rich`).

**Steps**
1. Add `rich` to dependencies.
2. Render the final answer as Markdown (`rich.markdown.Markdown`).
3. Show tool calls as dim one-liners, errors in red, diffs with green/red lines
   (`rich.syntax.Syntax(diff, "diff")`).
4. Show a spinner ("thinking…") while waiting for the first chunk.

**Done when**
- [ ] Diffs are colored; code blocks in answers are highlighted.

---

## Task 3.4: Better input line

**Why**: `input()` has no history (arrow up), no multi-line paste, no completion.

**Files**: `barasseur/ui.py`, `pyproject.toml` (add `prompt_toolkit`).

**Steps**
1. Use `prompt_toolkit.PromptSession` with `FileHistory` in the data folder.
2. Multi-line: Enter sends, Alt+Enter (or Esc then Enter) adds a new line.
3. Autocomplete slash commands and file paths after `@`.

**Done when**
- [ ] Arrow up recalls the previous question, even after a restart.

---

## Task 3.5: Slash commands

**Why**: common actions should not cost a model call.

**Files**: new `barasseur/commands.py`.

**Steps**
1. Parse lines starting with `/` before sending to the model.
2. Implement: `/help`, `/clear` (empty history), `/cost` (usage of task 2.1),
   `/model NAME`, `/compact`, `/init` (task 2.4), `/undo` (sprint 4), `/exit`.
3. A dict `name -> function(agent, args)` keeps it simple to extend.

**Done when**
- [ ] Each command has a test.

---

## Task 3.6: `@file` mentions

**Why**: "explain @src/app.py" saves a `read_file` step.

**Steps**
1. Before sending, find `@path` tokens that point to existing files.
2. Attach their content (truncated) to the user message in a block
   `<file path="...">...</file>`.

**Done when**
- [ ] A question with `@file` takes one step less (check with `--debug`).

---

## Task 3.7: Ctrl-C interrupts the current task, not the program

**Why**: you will often see the agent go the wrong way and want to stop it.

**Steps**
1. Catch `KeyboardInterrupt` inside the step loop; stop streaming; kill a running
   subprocess (`Popen` + `terminate()`).
2. Keep the history valid: if a function call has no response yet, add a
   response `{"error": "interrupted by the user"}`.
3. Back to the prompt; a second Ctrl-C on an empty prompt quits.

**Done when**
- [ ] Ctrl-C during a long `run_command` returns to the prompt, and the next question works.

---

## Task 3.8: Configuration file

**Why**: you should not retype `--model` every time.

**Files**: new `barasseur/config.py`.

**Steps**
1. Read `~/.config/barasseur/config.toml` with `tomllib` (built into Python 3.11).
2. Keys: `model`, `cheap_model`, `context_budget`, `permission_mode`,
   `allowed_commands`, `denied_commands`, `theme`.
3. Priority: command-line flag > environment variable > project
   `.barasseur/config.toml` > user config > default.

**Done when**
- [ ] Changing `model` in the file changes the model used, and `--model` still wins.

---

**End of sprint**: changelog, version `0.4.0`, tag.
