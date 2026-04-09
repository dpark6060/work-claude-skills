---
name: gear-repo-conventions
description: >
  Flywheel gear repository structure, pre-commit hooks, CI patterns, and
  common pipeline failure causes. Load this on first check to understand
  the repo you're babysitting.
---

# Flywheel Gear Repo Conventions

## Repo Structure

A typical Flywheel gear repo:

```
my-gear/
├── manifest.json            # Gear metadata, inputs, config, Docker image
├── pyproject.toml           # Python project config (poetry or uv)
├── requirements.txt         # Generated — DO NOT edit manually
├── Dockerfile               # Gear container build
├── run.py                   # Gear entry point
├── fw_gear_my_gear/         # Main Python package
│   ├── __init__.py
│   ├── main.py
│   └── ...
├── tests/
│   ├── conftest.py
│   └── ...
├── .pre-commit-config.yaml  # Pre-commit hook definitions
├── .gitlab-ci.yml           # CI pipeline config
└── README.md
```

---

## Package Management

Most gear repos use **uv** (some older ones use poetry). Always use
`uv run` to invoke tools within the project environment.

- `uv sync` — install/sync dependencies
- `uv run <command>` — run a command in the project venv
- `uv lock` — regenerate lock file

---

## Pre-Commit Hooks

**All linting and export generation is done via pre-commit hooks.**

Run with:
```bash
uv run pre-commit run --all-files
```

### What the hooks do

Pre-commit hooks in Flywheel gear repos typically handle:

1. **Code formatting** — black, isort, ruff, or similar formatters
2. **Linting** — ruff, flake8, or similar linters
3. **`requirements.txt` generation** — a hook that exports dependencies
   from `pyproject.toml` / `uv.lock` into `requirements.txt`. This file
   is committed and must stay in sync.
4. **`pyproject.toml` validation** — hooks that check consistency

### Critical: `requirements.txt` is generated, not hand-edited

`requirements.txt` is produced by a pre-commit hook that reads from
`pyproject.toml` (and/or the lock file). If you need to update it,
run pre-commit — do not edit the file directly.

When the pipeline fails on `pyproject_export` or requirements hash
mismatches, the fix is always: run pre-commit, commit the result, push.

---

## CI Pipeline

Gear repos use GitLab CI (`.gitlab-ci.yml`). Common pipeline stages:

1. **lint** — runs pre-commit hooks in CI. Fails if committed code doesn't
   match what pre-commit would produce.
2. **test** — runs pytest
3. **build** — builds the Docker image
4. **deploy** — pushes to registry (usually only on tagged releases)

### Common failure patterns

| Failure | Stage | Cause | Fix |
|---|---|---|---|
| Pre-commit formatting | lint | Code wasn't formatted before commit | Run pre-commit locally, commit result |
| `pyproject_export` mismatch | lint | `requirements.txt` out of sync with `pyproject.toml` | Run pre-commit locally (the export hook regenerates it) |
| Hash mismatch | lint | CI runner's package versions differ slightly | Run pre-commit locally, commit result |
| Merge conflict | any | Source and target branches diverged | Resolve conflicts, commit merge |
| Test failure | test | Actual code bug or missing test fixture | Report to user — do not auto-fix |
| Docker build failure | build | Missing dependency or broken Dockerfile | Report to user — do not auto-fix |

---

## Version Fields

Version is tracked in two places that must stay in sync:
- `manifest.json` → `version` field
- `pyproject.toml` → `version` under `[project]` or `[tool.poetry]`

When resolving merge conflicts on version fields, take the **source branch
(ours)** value — it represents the version being actively developed/pushed.

---

## Key Files for Pipeline Debugging

When diagnosing a pipeline failure, these files are most relevant:

| File | Why |
|---|---|
| `.gitlab-ci.yml` | Defines pipeline stages, jobs, and what commands they run |
| `.pre-commit-config.yaml` | Defines which hooks run and their versions |
| `pyproject.toml` | Project dependencies and metadata |
| `requirements.txt` | Generated export — check if it's in sync |
| `manifest.json` | Gear metadata — version conflicts happen here |
