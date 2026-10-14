# Sprint 0: Foundations

Goal: run barasseur for real, understand every file, and have a working
development setup (tests, push checks, CI) before adding features.

---

## Task 0.1: Set up your development environment

**Why**: you need an isolated Python environment so barasseur's packages do not
mix with the rest of your computer, and the push checks must run on your machine.

**Files**: none changed.

**Steps**
1. Install Python 3.11 or newer. Check with `python3 --version`.
2. Clone the repository and enter it:
   `git clone https://github.com/boubacarsidibe/barasseur_agent && cd barasseur_agent`
3. Create and activate a virtual environment:
   - Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `py -m venv .venv; .venv\Scripts\Activate.ps1`
4. Install barasseur in editable mode with the dev tools:
   `python -m pip install -e ".[dev]"`. Editable (`-e`) means your code changes
   are used immediately, no reinstall needed.
5. Activate the push checks: `git config core.hooksPath .githooks`
6. Run the checks once: `scripts/check.sh` (on Windows, run it from Git Bash).

**Done when**
- [ ] `scripts/check.sh` prints "Tous les contrôles sont passés".
- [ ] `barasseur --help` prints the usage.

---

## Task 0.2: Get a Gemini API key and run your first task

**Why**: until now the agent was only tested with a fake model. You need to see
the real loop work.

**Files**: `.env` (local only, never committed).

**Steps**
1. With a **personal** Google account (school accounts often get error 403), open
   https://aistudio.google.com/apikey and click "Create API key".
2. Put it in your shell: `export GEMINI_API_KEY=your_key` (PowerShell:
   `$env:GEMINI_API_KEY="your_key"`). Never paste it in a file that git tracks.
3. Make a playground folder: `mkdir ~/playground && cd ~/playground`, and create a
   file `calc.py` with a small bug, for example:
   ```python
   def total(n):
       return sum(range(n))  # bug: should include n
   ```
4. Run: `barasseur --dir ~/playground "total(4) should return 10, fix calc.py"`
5. Watch the `⚙` lines: they are the tool calls. Accept the edit with `o`.

**Done when**
- [ ] The agent read the file, proposed an edit, and `calc.py` is fixed.
- [ ] You can explain each `⚙` line you saw (which tool, why the model asked for it).

---

## Task 0.3: Read and annotate the code

**Why**: you will modify these files in every sprint. Understanding them now
saves hours later.

**Files**: `barasseur/agent.py`, `barasseur/tools.py`, `barasseur/__main__.py`,
`tests/test_agent.py`.

**Steps**
1. Read `COMMENT_CA_MARCHE.md` again.
2. Read `__main__.py`: find where the command-line arguments are parsed, where
   `confirm` is defined, and the interactive `while True` loop.
3. Read `agent.py`: follow `Agent.ask` line by line. Answer in your own notes:
   - Where is the user question added to the history?
   - What happens when the answer has no function call?
   - Why are tool results added with `role="user"`?
4. Read `tools.py`: understand `_path` (why it protects you), `_truncate` (why it
   saves money), and the `SCHEMAS` list (what the model sees).
5. Read `tests/test_agent.py`: understand how `FakeModels` replaces Gemini.
6. Add a debug flag to see the raw requests: in `__main__.py` add
   `--debug` that prints `len(agent.history)` and `agent.tokens_used` after each
   answer. Commit it.

**Done when**
- [ ] You can draw the loop on paper without looking at the code.
- [ ] `--debug` works and the change is merged to `main`.

---

## Task 0.4: Fix the GitHub CI

**Why**: the CI runs the same checks as your computer on every push. It protects
`main` when you forget to run them.

**Files**: `.github/workflows/checks.yml` (only if the cause is in the file).

**Steps**
1. Open the Actions tab of the repository and the failed run "checks".
2. If a yellow banner says the job was not started because of **billing** or a
   **spending limit**: go to GitHub Settings > Billing and plans, and check
   "Actions" usage. Private repositories on the free plan get 2,000 minutes per
   month; a failed payment method or a $0 spending limit with exhausted minutes
   blocks every job. Fix the payment method or wait for the monthly reset.
3. If the banner says Actions are **disabled**: repository Settings > Actions >
   General > "Allow all actions".
4. Re-run the job ("Re-run all jobs").

**Done when**
- [ ] The "checks" run on `main` is green.

---

## Task 0.5: Protect the main branch

**Why**: from now on every change goes through a pull request, so the CI must be
green before anything lands on `main`.

**Note**: on a free GitHub account, branch rules are only enforced on public
repositories. On a private repository you need GitHub Pro (free for students
through the GitHub Student Developer Pack). Without it, keep the habit anyway:
never push to `main` directly, always use a pull request.

**Steps**
1. Repository Settings > Branches > Add branch ruleset (or "Add rule").
2. Target `main`. Enable "Require a pull request before merging" and "Require
   status checks to pass", and select the `checks` job.
3. Try it: create a branch, change a comment, push, open a pull request, wait for
   green, merge.

**Done when**
- [ ] A direct `git push origin main` is refused.
- [ ] You merged your first pull request.
