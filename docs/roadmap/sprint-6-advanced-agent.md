# Sprint 6: Advanced agent

Goal: barasseur handles big, multi-step tasks: it plans, delegates research to
sub-agents, reads the web, and can use external tools through MCP.

Measure each task of this sprint with the benchmark of sprint 5: add 3 to 5
larger tasks to `evals/` first, so you know if these features really help.

---

## Task 6.1: Task list tool (planning)

**Why**: on a 10-step job, the model forgets steps. A visible to-do list keeps it
on track and shows you the plan.

**Files**: `barasseur/tools.py`, `barasseur/ui.py`.

**Steps**
1. Add `todo_write(items: list[{text, status}])` where status is `pending`,
   `in_progress` or `done`. It replaces the whole list each time (simple and robust).
2. Store the list on the agent; show it in the UI each time it changes.
3. System prompt: "For tasks with more than 3 steps, write a todo list first and
   update it as you go."

**Done when**
- [ ] On a multi-file task you see the list appear and get checked off.

---

## Task 6.2: Sub-agents

**Why**: searching a big codebase fills the history with file contents. A
sub-agent does the search in its **own** fresh history and returns only a short
report, so the main history stays small.

**Files**: `barasseur/agent.py`, `barasseur/tools.py`.

**Steps**
1. Add a tool `delegate(task: str)` that creates a new `Agent` with read-only
   tools (`read_file`, `search`, `glob`, `list_files`), a cheaper model, and a
   step limit (for example 15).
2. Its system prompt: "You are a research helper. Answer the task with a short
   report: relevant files, line numbers, findings. Do not modify anything."
3. Return only its final text to the main agent; add its usage to the session usage.
4. Optional: allow several `delegate` calls in one step to run in parallel with
   `concurrent.futures.ThreadPoolExecutor`.

**Done when**
- [ ] "Where is authentication handled?" on a big repo uses `delegate`, and the
      main history grows by a few hundred tokens instead of tens of thousands.

---

## Task 6.3: Web tools

**Why**: the agent needs documentation it was not trained on (new library versions).

**Steps**
1. `web_fetch(url)`: download with `httpx`, convert HTML to text or markdown
   (`markdownify` or `trafilatura`), truncate. Ask permission for new domains.
2. `web_search(query)`: the simplest path is Gemini's built-in Google Search
   grounding. Note: built-in tools and your own function tools may not be
   combinable in the same request depending on the model; if not, run the search
   in a separate small request (a sub-agent with only the `google_search` tool)
   and return the result as text.

**Done when**
- [ ] "What is the latest version of FastAPI and what changed?" returns a sourced answer.

---

## Task 6.4: MCP client

**Why**: MCP (Model Context Protocol) is a standard way to plug external tools
(GitHub, databases, Figma, ...) into an agent. Supporting it gives barasseur
hundreds of tools without writing them.

**Files**: new `barasseur/mcp_client.py`, `config.py`.

**Steps**
1. Add the `mcp` Python package.
2. Config: a list of servers, each with `command` + `args` (local, stdio) or a `url`.
3. At startup, connect to each server, call `list_tools()`, and convert each tool
   to a Gemini `FunctionDeclaration` (MCP tools already have a JSON schema).
   Prefix names: `servername__toolname`.
4. When the model calls one, forward it with `session.call_tool(name, args)` and
   return the text content.
5. MCP tools use the `exec` permission level by default.

**Done when**
- [ ] With the official filesystem or GitHub MCP server configured, the agent can use its tools.

---

## Task 6.5: Images as input

**Why**: "make the page look like this screenshot" or "what's wrong in this error
screenshot" are common requests. Gemini reads images natively.

**Steps**
1. `@image.png` in the prompt or a `read_image(path)` tool attaches
   `types.Part.from_bytes(data=..., mime_type="image/png")`.
2. Limit size (resize big images with Pillow).

**Done when**
- [ ] The agent describes a screenshot you give it.

---

## Task 6.6: Hooks

**Why**: run your own scripts automatically, for example format the code after
every edit, or block edits to a folder.

**Steps**
1. Config: `hooks.after_edit = "ruff format {path}"`, `hooks.before_command = "..."`.
2. Run them with the same permission and timeout rules as `run_command`.
3. A non-zero exit of a `before_*` hook cancels the action and tells the model why.

**Done when**
- [ ] Every file the agent edits is formatted automatically.

---

**End of sprint**: changelog, version `0.7.0`, tag.
