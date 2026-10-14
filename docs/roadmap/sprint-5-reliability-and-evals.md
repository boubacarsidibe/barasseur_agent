# Sprint 5: Reliability and evaluation

Goal: the agent survives network and API errors, you can see what happened in a
session, and you have a **benchmark** that tells you, with a number, whether a
change made the agent better or worse.

---

## Task 5.1: Retries with backoff

**Why**: the API sometimes answers 429 (too many requests) or 500/503 (server
busy). Today one such error crashes the session.

**Files**: `barasseur/agent.py`.

**Steps**
1. Wrap the model call. Catch `google.genai.errors.APIError` and check `e.code`.
2. Retry on 429, 500, 503 and network errors: wait 2, 4, 8, 16, 32 seconds
   (exponential backoff) plus a small random delay. Stop after 5 tries.
3. Do not retry on 400 (bad request) or 403 (key problem): show a clear message
   ("Your API key is refused: check GEMINI_API_KEY").
4. On repeated 429 with the main model, offer to switch to the fallback model.

**Done when**
- [ ] A test with a fake client that fails twice then succeeds passes, without real waiting (patch `time.sleep`).

---

## Task 5.2: Handle empty and blocked answers

**Why**: Gemini can return no candidate, a `SAFETY` finish reason, or
`MAX_TOKENS` in the middle of a function call.

**Steps**
1. Check `resp.candidates` is not empty and read `candidate.finish_reason`.
2. `MAX_TOKENS`: ask the model to continue, or raise `max_output_tokens`.
3. `SAFETY` / `RECITATION`: show the reason to the user, keep the session alive.
4. Malformed function call (unknown tool, wrong arguments): already returned as
   an error to the model; add a test with wrong argument types.

**Done when**
- [ ] Each finish reason has a test and a readable message.

---

## Task 5.3: Logs

**Why**: when something goes wrong in a session, you need to see what the model
received and answered.

**Files**: new `barasseur/log.py`.

**Steps**
1. Use Python `logging` writing to `~/.local/share/barasseur/logs/barasseur.log`
   with rotation (`RotatingFileHandler`, 5 files × 5 MB).
2. Log each step: model, token counts, tool name, tool duration, errors. Do not
   log file contents at INFO level, only at DEBUG.
3. `--debug` sets level DEBUG.

**Done when**
- [ ] After a session, the log tells the full story without the console.

---

## Task 5.4: Build an evaluation benchmark

**Why**: "it feels better" is not a measure. With 20 small tasks and automatic
checks, you can compare prompts, models and tools objectively. This is how
professional agents are improved.

**Files**: new folder `evals/` with `evals/tasks/<name>/` and `evals/run.py`.

**Steps**
1. Each task folder contains:
   - `repo/`: a tiny project (a few files) in its starting state;
   - `prompt.txt`: what you ask the agent;
   - `check.sh`: a script that exits 0 if the task is solved (usually runs tests).
2. Write 20 tasks of growing difficulty: fix a bug, add a function and its test,
   rename across files, fix a failing test, add a CLI flag, find and fix a
   security bug, refactor a long function, etc.
3. `evals/run.py`: for each task, copy `repo/` to a temp folder, run the agent
   with `--mode yolo` and a step limit, run `check.sh`, record pass/fail, steps,
   tokens, cost, time.
4. Print a table and save results as JSON in `evals/results/<date>-<model>.json`.
5. Run with `--repeat 3`: model answers vary, so one run is not enough.

**Done when**
- [ ] `python evals/run.py` gives a success rate and a total cost.
- [ ] You have a baseline result committed.

---

## Task 5.5: Use the benchmark to choose settings

**Why**: now you can optimize with data.

**Steps**
1. Compare `gemini-2.5-flash` and `gemini-2.5-pro` (and newer models when they
   appear): success rate vs cost.
2. Compare thinking budgets: `types.ThinkingConfig(thinking_budget=0 | 1024 | 8192)`.
3. Compare two versions of the system prompt.
4. Write the results and your choice in `docs/decisions.md`.

**Done when**
- [ ] Defaults in `config.py` are justified by benchmark numbers.

---

## Task 5.6: Run a small benchmark in CI (optional)

**Why**: catch quality regressions automatically.

**Steps**
1. Store `GEMINI_API_KEY` as a repository secret (Settings > Secrets > Actions).
2. New workflow `evals.yml`, triggered manually (`workflow_dispatch`) to control
   cost, running 5 fast tasks.

**Done when**
- [ ] You can launch the eval from the Actions tab and read the table in the job summary.

---

**End of sprint**: changelog, version `0.6.0`, tag.
