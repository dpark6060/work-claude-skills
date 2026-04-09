---
name: bootstrap-validator
description: >
  Validates and bootstraps the project development environment. Checks Python
  version, uv sync, venv, pre-commit hooks, MCP server configs, credential file
  JSON validity, and git state. Attempts automatic fixes for each failure and
  produces a final health report. Run at the start of a session on an unfamiliar
  project or after pulling changes.
version: 1.0.0
tags:
  - environment
  - bootstrap
  - validation
---

# Bootstrap Validator

## Purpose

Validate the project's development environment end-to-end, fix what can be fixed
automatically, and produce a health report. Run this at the start of a session when
something feels off, after a fresh clone, or after pulling significant changes.

---

## Before You Start

1. **Read `pyproject.toml`** if it exists — note `requires-python`, the build backend
   (`[build-system]`), and the project name.
2. **Read `.pre-commit-config.yaml`** if it exists.
3. **Read MCP config** — check `~/.claude/settings.json` and any project-level
   `.mcp.json` for `mcpServers` entries. Note any `env` values that reference
   credential files.
4. **Announce your fix plan** before running any modifying command. Since the user
   invoked this skill, you may proceed with standard dev-environment fixes (`uv sync`,
   `pre-commit install`, JSON repairs). Ask before anything that modifies source files
   or installs system-level tools.

Initialize the log file: append a session header to `.bootstrap_log.md` in the
project root:

```
## Bootstrap Run — <ISO timestamp>
```

---

## Checks

Run each check in order. For every failure: attempt the automatic fix described,
re-run the check once, then record the result. Never attempt the same fix more
than once.

---

### Check 1 — Git State

```bash
git config user.name
git config user.email
git status --short
```

**Pass:** Both name and email are set; working tree is clean or has only expected
untracked files.

**Failures and fixes:**
- `user.name` or `user.email` not set → report as ❌, do not auto-fix (requires user
  input). Log the missing values and advise: `git config --global user.name "Your Name"`
- Uncommitted changes → report as 🔧 (informational warning, not a blocker). List the
  changed files in the log.

---

### Check 2 — uv Available

```bash
which uv && uv --version
```

**Pass:** `uv` is found and prints a version.

**Fix:** If missing, do not auto-install. Report ❌ and instruct the user:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# then restart your shell
```
Log as ❌ and stop — subsequent checks depend on `uv`.

---

### Check 3 — Python Version vs. pyproject.toml

Read `requires-python` from `pyproject.toml`. Get the current Python version:
```bash
uv run python --version 2>&1
```

**Pass:** Installed Python satisfies the constraint (e.g., `>=3.11` with Python 3.12
is a pass).

**Fix:** If unsatisfied:
```bash
# Install the required version (e.g., for >=3.11):
uv python install 3.11
uv sync
```
Re-check after fix.

---

### Check 4 — uv sync

```bash
uv sync 2>&1
```

**Pass:** Exits 0 with no errors.

**Common failures and fixes:**

*Build backend not found* (e.g., `hatchling`, `setuptools`, `flit-core` not installed):
```bash
# Identify backend from pyproject.toml [build-system] requires
uv pip install hatchling        # or setuptools, flit-core, etc.
uv sync
```

*No module named pip / pip not available*:
```bash
uv pip install pip
uv sync
```

*Lock file out of date*:
```bash
uv lock
uv sync
```

*Dependency conflict* → report ❌ with the full error, do not attempt to resolve
automatically. Log the full error text.

---

### Check 5 — Venv Active and Package Importable

```bash
uv run python -c "import sys; print(sys.executable)"
```

Verify the path points to `.venv/` inside the project directory.

Then import the project package by name (read from `pyproject.toml` `[project] name`,
replacing hyphens with underscores):
```bash
uv run python -c "import <package_name>; print('ok')"
```

**Pass:** Executable is inside `.venv/`, import succeeds.

**Fix:** If `.venv/` doesn't exist or import fails after a successful `uv sync`,
recreate the environment:
```bash
uv venv
uv sync
```
Re-check import.

**Note:** Do not try to `source .venv/bin/activate` — Claude Code bash commands don't
persist shell state between invocations. Always use `uv run` to execute in the venv.

---

### Check 6 — Pre-commit Hooks

Only run this check if `.pre-commit-config.yaml` exists.

**Step 1 — Check installation:**
```bash
uv run pre-commit --version 2>&1
```
If missing: `uv pip install pre-commit`

**Step 2 — Install hooks:**
```bash
uv run pre-commit install 2>&1
```
This is idempotent — safe to run every time.

**Step 3 — Run against staged files only (no-op if nothing staged):**
```bash
uv run pre-commit run 2>&1
```

**Pass:** Exits 0.

**Failure:** If hooks fail on a no-op run (no staged files), something is misconfigured.
Log the full output as ❌. Do **not** run `--all-files` automatically — that may
auto-modify source files. Report the failure and advise the user to run
`uv run pre-commit run --all-files` manually to see what needs fixing.

---

### Check 7 — MCP Config JSON Validity

Read MCP configuration from:
1. `~/.claude/settings.json` — look for the `mcpServers` key
2. Any project-level `.mcp.json`

For each MCP server entry:

**Step 1 — Validate the config file itself:**
```bash
python -m json.tool ~/.claude/settings.json > /dev/null 2>&1 && echo "valid" || echo "invalid"
```

**Step 2 — Find and validate referenced credential files.** Look in each server's
`env` block for values that look like file paths (start with `/` or `~/`). For each:
```bash
python -m json.tool <credential_file_path> > /dev/null 2>&1 && echo "valid" || echo "invalid"
```

**Pass:** All files parse as valid JSON.

**Fix for JSON syntax errors (e.g., trailing commas):**

Read the file, identify the offending lines, and rewrite it with the fix applied.
The most common issue is trailing commas before `}` or `]`. Use Python to do a
round-trip parse-and-rewrite only after confirming the structure is otherwise correct:

```bash
python3 -c "
import json, re, sys
path = '<credential_file>'
with open(path) as f:
    raw = f.read()
# Strip trailing commas before } or ]
fixed = re.sub(r',(\s*[}\]])', r'\1', raw)
try:
    parsed = json.loads(fixed)
except json.JSONDecodeError as e:
    print(f'Cannot auto-fix: {e}')
    sys.exit(1)
with open(path, 'w') as f:
    json.dump(parsed, f, indent=2)
print('Fixed and written.')
"
```

After fixing any config file, log: **Restart Claude Code for MCP changes to take effect.**

**Step 3 — Check that each server's command binary exists:**
```bash
# e.g., for a server using npx:
which npx
# or for a uvx-based server:
which uvx
```

Report ❌ with instructions if a required binary is missing.

---

### Check 8 — Project Test Suite (Optional)

If a test suite exists (`tests/` directory or `pytest.ini` / `pyproject.toml`
`[tool.pytest]` section), run a quick check:

```bash
uv run pytest --co -q 2>&1 | tail -5
```

This collects tests without running them — a fast check that imports work and
pytest configuration is valid.

**Pass:** Collection succeeds with no errors.

**Failure:** Log the error. If it's an import error, it likely means Check 5 didn't
fully catch a missing dependency. Report ❌ with the specific import that failed.

Do not run the full test suite as part of bootstrap — that is the user's decision.

---

## Logging

After each check, append to `.bootstrap_log.md`:

```markdown
### <Check Name> — <✅ PASS | ❌ FAIL | 🔧 FIXED>
- **Time:** <timestamp>
- **Command:** `<command run>`
- **Result:** <one-line summary>
- **Fix applied:** <what was done, or "none">
- **Re-check result:** <pass/fail after fix, or "N/A">
```

Add `.bootstrap_log.md` to `.gitignore` if not already present.

---

## Final Report

After all checks complete, output a markdown table:

```markdown
## Environment Health Report

| Check | Status | Details |
|---|---|---|
| Git state | ✅ | Clean. user.name and user.email set. |
| uv available | ✅ | uv 0.4.x |
| Python version | ✅ | 3.12.1 satisfies >=3.11 |
| uv sync | 🔧 Fixed | hatchling missing — installed and re-synced |
| Venv / imports | ✅ | .venv active, `my_package` imports ok |
| Pre-commit hooks | ✅ | Hooks installed, no-op run passed |
| MCP config JSON | 🔧 Fixed | Trailing comma removed from gitlab_creds.json — **restart Claude Code** |
| MCP binaries | ✅ | npx found |
| Test collection | ✅ | 47 tests collected |

**Summary:** 2 issues found, 2 auto-fixed. Environment is ready.
```

If any ❌ remain, list them with the specific action needed from the user before the
environment can be considered healthy.

---

## Idempotency Notes

This skill is safe to run multiple times:
- `uv sync` is idempotent
- `pre-commit install` is idempotent
- JSON fixes check for validity before writing
- Log entries append, never overwrite
- `.gitignore` entry is only added if missing
