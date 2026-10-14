# Sprint 1: Better tools

Goal: the agent works on real, big projects. It can search code instead of
reading every file, shows you clear diffs before changing anything, and each
tool is tested.

General rule for a new tool (repeat for each task):
1. Add a method to `Toolbox` in `barasseur/tools.py`.
2. Add its schema to `SCHEMAS` with a **clear description**: the model chooses
   tools only from their description.
3. Add a test in `tests/test_tools.py` that calls the method directly (no model needed).
4. Add a test in `tests/test_agent.py` where the fake model calls the tool.
5. Mention the tool in `SYSTEM_PROMPT` if the model should prefer it.

---

## Task 1.1: Split the tests and test every existing tool

**Why**: before changing tools, you need a safety net that tells you when you
break one.

**Files**: new `tests/test_tools.py`.

**Steps**
1. Create `tests/test_tools.py` with a fixture that builds a `Toolbox` on
   `tmp_path` (pytest gives a fresh temporary folder to each test).
2. Write at least one test per tool: `list_files` skips `.git`, `read_file`
   respects `start`/`end`, `edit_file` refuses when `old` appears twice,
   `write_file` creates parent folders, `run_command` returns the exit code.
3. Test `_truncate` with a 50,000-character string.

**Done when**
- [ ] `pytest -q` shows at least 10 passing tests.

---

## Task 1.2: `search` tool (find text in the code)

**Why**: on a project with 500 files, reading files one by one is slow and
expensive. Searching is how human developers find code, and the model too.

**Files**: `barasseur/tools.py`, `tests/test_tools.py`.

**Steps**
1. Add `search(pattern: str, path: str = ".", glob: str | None = None)`.
2. If `rg` (ripgrep) is installed (`shutil.which("rg")`), run
   `rg --line-number --max-count 50 -e PATTERN [--glob GLOB] PATH` with
   `subprocess.run([...], shell=False)`. Passing a list (not a string) avoids
   shell injection.
3. Otherwise fall back to Python: walk files with `Path.rglob`, skip the same
   folders as `list_files`, use `re.search` line by line.
4. Return `file:line: text`, at most 200 matches, then `_truncate`.
5. Description for the model: "Search a regex in the project files. Use it
   before read_file to find where something is defined or used."

**Done when**
- [ ] Searching a function name returns its definition line.
- [ ] Works with and without ripgrep (test the fallback by mocking `shutil.which`).

---

## Task 1.3: `glob` tool and a smarter `list_files`

**Why**: `list_files` on a big project returns 500 lines of noise. The model
needs to ask "all `*.py` files under `src/`".

**Files**: `barasseur/tools.py`.

**Steps**
1. Add `glob(pattern: str)` that returns `sorted(self.workdir.glob(pattern))`
   relative paths, files only, max 300.
2. Make `list_files` respect `.gitignore`: if the folder is a git repo, use
   `git ls-files --cached --others --exclude-standard`.
3. Add `max_depth` to `list_files` (default 3).

**Done when**
- [ ] `glob("**/*.py")` works; ignored files (like `.venv`) never appear.

---

## Task 1.4: Show a real diff before every edit

**Why**: today the confirmation shows "before/after" text. A unified diff, like
`git diff`, is easier to review and shows the line numbers.

**Files**: `barasseur/tools.py`.

**Steps**
1. Use `difflib.unified_diff(old_text.splitlines(True), new_text.splitlines(True), fromfile=path, tofile=path)`.
2. In `edit_file` and `write_file` (when the file exists), build the full new
   content, compute the diff, and pass it to `confirm`.
3. Return a short summary to the model: `"a.py modified (+3 -1 lines)"`.

**Done when**
- [ ] Confirmations show `---`, `+++`, `@@` diff blocks.

---

## Task 1.5: Multiple edits in one call

**Why**: renaming a variable used 5 times takes 5 steps today, each step resends
the whole history. One call with 5 edits is ~5x cheaper.

**Files**: `barasseur/tools.py`.

**Steps**
1. Add `multi_edit(path: str, edits: list[{old, new}])`. Apply edits in order on
   an in-memory copy; if any `old` is not found exactly once, change nothing and
   return the error with the edit index.
2. One confirmation with the full diff.
3. JSON schema: `"edits": {"type": "array", "items": {"type": "object", "properties": {"old": ..., "new": ...}, "required": ["old", "new"]}}`.

**Done when**
- [ ] A failing 3rd edit leaves the file untouched.

---

## Task 1.6: Safer `run_command`

**Why**: commands can hang (a server that never stops) or print megabytes.

**Files**: `barasseur/tools.py`.

**Steps**
1. Catch `subprocess.TimeoutExpired` and return "Command stopped after N s" plus
   the partial output instead of crashing.
2. Cap `timeout` at 600 seconds whatever the model asks.
3. Set `stdin=subprocess.DEVNULL` so a command waiting for input fails fast.
4. Merge stdout and stderr in order: `stderr=subprocess.STDOUT`.

**Done when**
- [ ] `run_command("sleep 5", timeout=1)` returns a clear message.
- [ ] `run_command("python -c 'input()'")` returns immediately.

---

## Task 1.7: Better system prompt

**Why**: the system prompt is the biggest lever on quality, and it is free.

**Files**: `barasseur/agent.py` (move the prompt to `barasseur/prompts.py`).

**Steps**
1. Move `SYSTEM_PROMPT` to its own file.
2. Add: the current date, the OS (`platform.system()`), the working directory,
   and whether it is a git repo. Build it once at startup so it stays identical
   during the session (needed for caching).
3. Add rules: search before reading; read before editing; run tests after
   editing; never invent file contents; ask the user when the task is unclear;
   final answer = short summary of what changed.
4. Compare on the same 3 tasks before and after (count steps with `--debug`).

**Done when**
- [ ] The agent uses `search` first on a "where is X" question.
- [ ] Average steps on your 3 tasks went down or stayed equal.

---

**End of sprint**: update `CHANGELOG.md`, version `0.2.0`, tag `git tag v0.2.0 && git push --tags`.
