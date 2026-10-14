# Sprint 7: Release 1.0

Goal: barasseur installs with one command on any of your machines, is
documented, and has a clean release process.

---

## Task 7.1: Clean up and review the whole code

**Why**: after 6 sprints, some code is duplicated or outdated.

**Steps**
1. Run `ruff check --select ALL .` once to see extra suggestions; fix the useful ones.
2. Add type checking: `mypy barasseur` (add `mypy` to dev dependencies and to
   `scripts/check.sh`).
3. Measure test coverage: `pytest --cov=barasseur`; aim for 80 %.
4. Remove unused code and settings.

**Done when**
- [ ] `scripts/check.sh` includes mypy and passes; coverage ≥ 80 %.

---

## Task 7.2: Test on Windows, macOS and Linux

**Why**: paths, shells and colors differ between systems.

**Steps**
1. In `checks.yml`, use a matrix: `os: [ubuntu-latest, windows-latest, macos-latest]`
   and `python-version: ["3.11", "3.13"]`. Note: Windows and macOS minutes cost
   more on private repositories; you can run the matrix only on tags.
2. Replace any `shell=True` assumption that only works on Linux; on Windows
   `run_command` should use PowerShell or `cmd`.

**Done when**
- [ ] The matrix is green.

---

## Task 7.3: Install with one command

**Why**: you want barasseur on every machine without cloning the repo.

**Steps**
1. Check `pyproject.toml` metadata (name, version, description, entry point).
2. Build: `python -m build` produces `dist/*.whl`.
3. Install from the private repo with pipx:
   `pipx install git+https://github.com/boubacarsidibe/barasseur_agent@v1.0.0`
   (or `uv tool install` with the same URL).
4. Optional: publish to PyPI later if you make the project public.

**Done when**
- [ ] On a fresh machine, one command installs a working `barasseur`.

---

## Task 7.4: Release workflow

**Why**: releases should be automatic and identical every time.

**Steps**
1. New workflow `release.yml` triggered on tags `v*`: run checks, build the
   wheel, create a GitHub Release with the wheel attached and the changelog
   section as notes.
2. Document the release steps in `CONTRIBUTING.md`: update changelog, bump
   version, `git tag vX.Y.Z`, `git push --tags`.

**Done when**
- [ ] Pushing tag `v1.0.0` creates a GitHub Release automatically.

---

## Task 7.5: Final documentation

**Steps**
1. `README.md`: what barasseur is, install, first run, a short GIF or screenshot.
2. `docs/usage.md`: all flags, slash commands, config keys, permission modes.
3. `docs/architecture.md`: update the diagram with all the modules you added.
4. `docs/decisions.md`: why each important choice was made (from sprint 5).
5. Translate or keep docs in one language consistently.

**Done when**
- [ ] Someone who never saw the project can install and use it with the README only.

---

## After 1.0: ideas

- An editor extension (VS Code) using the event layer from task 3.1.
- A web interface.
- Support for other model providers behind one interface, to compare them in the benchmark.
- Scheduled background tasks (for example "every morning, update dependencies and run tests").
