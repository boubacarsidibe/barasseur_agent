# Sprint 2: Context and cost

Goal: long sessions stay cheap and never overflow the model's context window,
the agent follows per-project rules, and you can stop and resume a session.

Reminder: at every step the **whole history** is sent again. A session of 40
steps with 20,000 tokens of history costs 40 × 20,000 = 800,000 input tokens.
This sprint attacks that number.

---

## Task 2.1: Measure tokens and cost precisely

**Why**: you cannot optimize what you do not measure.

**Files**: new `barasseur/usage.py`, `barasseur/agent.py`, `barasseur/__main__.py`.

**Steps**
1. Create a `Usage` dataclass with `input_tokens`, `cached_tokens`,
   `output_tokens`, `thinking_tokens`, `steps`.
2. After each `generate_content`, read `resp.usage_metadata`:
   `prompt_token_count`, `cached_content_token_count`,
   `candidates_token_count`, `thoughts_token_count`. Add them up.
3. Add a price table per model (USD per million tokens, input / cached input /
   output). Copy the current prices from https://ai.google.dev/gemini-api/docs/pricing
   and write the date next to them: prices change.
4. Print a one-line summary after each answer in `--debug` mode, and at exit:
   `steps=12 in=84k (cached 61k) out=3k ≈ $0.03`.

**Done when**
- [ ] The cost printed matches the Google AI Studio usage page within ~10 %.

---

## Task 2.2: Count tokens before sending

**Why**: you must know when the history approaches the model's limit
(about 1 million tokens for Gemini 2.5 Flash, but cost and quality degrade far earlier).

**Files**: `barasseur/agent.py`.

**Steps**
1. Use the last `prompt_token_count` as the current history size (free, no
   extra call). For an estimate before the first call, use
   `client.models.count_tokens(model=..., contents=...)`.
2. Add a setting `context_budget` (default 100,000 tokens).
3. When the history size passes 80 % of the budget, trigger compaction (task 2.3).

**Done when**
- [ ] `--debug` shows the history size at each step.

---

## Task 2.3: Compact the history automatically

**Why**: old tool results (a file read 30 steps ago) are rarely useful but are
paid for at every step.

**Files**: new `barasseur/compaction.py`, `barasseur/agent.py`.

**Steps**
1. **Cheap pass first**: replace the content of old tool results (all except
   the last 10 steps) with `"[old result removed, call the tool again if needed]"`.
   Keep the function calls themselves so the model knows what it did.
2. **Summary pass** if still too big: send the old part of the history to a
   cheap model (for example `gemini-2.5-flash-lite`) with the instruction
   "Summarize this coding session: goal, decisions, files changed, open
   problems." Replace that part with one user message containing the summary.
3. Never cut between a function call and its function response: the API
   rejects a response without its call. Cut only at a user question boundary.
4. Keep `thought_signature` parts in the recent history untouched.
5. Add a `/compact` command later in sprint 3 to trigger it by hand.

**Done when**
- [ ] A test builds a fake history of 200 steps and checks it shrinks below the budget.
- [ ] A real 30-step session keeps working after a compaction.

---

## Task 2.4: Project instructions file (`BARASSEUR.md`)

**Why**: each project has its own rules ("use pnpm, not npm", "tests are in
`spec/`"). Writing them once saves steps and mistakes in every session.

**Files**: `barasseur/prompts.py`.

**Steps**
1. At startup, look for `BARASSEUR.md` (also accept `AGENTS.md`) in the working
   directory and its parents up to the git root.
2. Also read a personal file `~/.config/barasseur/BARASSEUR.md` for your own
   preferences (language, style).
3. Append their content to the system prompt under a heading
   "Project instructions". Limit to 20,000 characters.
4. Add a `/init` command later (sprint 3) that asks the agent to explore the
   project and write a first `BARASSEUR.md`.

**Done when**
- [ ] A rule written in `BARASSEUR.md` is followed without being repeated in the question.

---

## Task 2.5: Save and resume sessions

**Why**: you close the terminal and lose everything. Saved sessions also let you
review what the agent did.

**Files**: new `barasseur/session.py`, `barasseur/__main__.py`.

**Steps**
1. Session folder: `~/.local/share/barasseur/sessions/` (Windows:
   `%LOCALAPPDATA%\barasseur\sessions`). Use `platformdirs` to get it right.
2. After each step, append the new messages as JSON lines to
   `<date>-<id>.jsonl`. Convert with `content.model_dump(mode="json", exclude_none=True)`
   and back with `types.Content.model_validate(data)`.
3. Add `--resume` (last session) and `--resume ID`.
4. Add `barasseur sessions` to list sessions with date, folder and first question.

**Done when**
- [ ] Quit in the middle, `barasseur --resume`, the agent remembers the task.

---

## Task 2.6: Use caching on purpose

**Why**: Gemini bills cached input tokens much cheaper. Implicit caching works
only if the **start** of each request is identical.

**Files**: `barasseur/agent.py`, `barasseur/prompts.py`.

**Steps**
1. Check nothing variable sits in the system prompt (no time with seconds, no
   random order of tools). Sort `SCHEMAS` by name.
2. Never modify old history messages except during compaction.
3. Measure `cached_content_token_count` over a session (task 2.1). Expect most
   input tokens to be cached after the first steps.
4. Optional: try explicit caching (`client.caches.create`) for a very large
   `BARASSEUR.md`, and compare costs.

**Done when**
- [ ] On a 20-step session more than half of the input tokens are cached.

---

**End of sprint**: changelog, version `0.3.0`, tag.
