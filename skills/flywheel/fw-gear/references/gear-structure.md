---
type: Library Reference
title: Gear Structure
description: The skeleton gear's sanctioned file and module names (never rename run.py, main.py, parser.py), the reject table for common renames, and how to decouple main.py from Flywheel via run.py.
tags: [fw-gear, gears, structure, decoupling, skeleton]
timestamp: 2026-09-16T00:00:00Z
---

# Gear Structure

## Sanctioned File Names

Gears start from the skeleton gear template. **The file and module names the skeleton ships with
are the standard. Never rename them.** Renaming breaks the convention every other gear follows
and makes cross-gear navigation and code reuse worse for no gain.

This applies to design docs and architecture plans too — not just code. If a plan, module tree,
or ticket names a different file, the plan is wrong. Keep the sanctioned name and say so.

Files that ship with the skeleton and keep their names:

```
run.py                        # entrypoint, stays at repo root
manifest.json
pyproject.toml
Dockerfile
requirements.txt
requirements-dev.txt
.gitlab-ci.yml
.pre-commit-config.yaml
README.md
CONTRIBUTING.md
FAQ.md
LICENSE
docs/release_notes.md
fw_gear_<name>/
    __init__.py
    main.py                   # the gear's work; run(...) lives here
    parser.py                 # gear config/inputs -> plain values for main.py
tests/
```

Common renames to reject:

| Wrong | Right |
|---|---|
| `gear_config.py`, `config.py`, `configuration.py`, `context.py` | `parser.py` |
| `pipeline.py`, `gear.py`, `core.py` | `main.py` |
| `__main__.py`, `entrypoint.py`, `fw_gear_<name>/run.py` | `run.py` at repo root |

**Adding modules is fine.** The rule is don't rename what ships, not don't add. A gear that needs
`models.py`, `fw_ops.py`, `verdict.py` and so on should have them — alongside `main.py` and
`parser.py`, not instead of them.

**Entry-point functions**: the skeleton's are `parse_config(gear_context)` in `parser.py` and
`run(...)` in `main.py`. A `get_`-prefixed name (`get_run_config`) is acceptable if you prefer
Functions.md prefix consistency, but the *module* name `parser.py` is not negotiable.

## Flywheel Decoupling

Decouple gear logic from Flywheel. Keeps `main.py` testable — no client, context, or config needed.

### The Core Principle

`run.py` owns all Flywheel interactions. `main.py` receives only the data it needs to do its job.

**Config parsing**: Parse the full gear config in `run.py`. Pass individual values to `main.py` — not the config object.

```python
# Good — run.py extracts what main.py needs
subject_label = gear_context.config.get("subject_label")
threshold = gear_context.config.get("threshold", 0.5)
result = main(subject_label=subject_label, threshold=threshold)

# Bad — main.py is now coupled to gear config shape
result = main(config=gear_context.config)
```

**Flywheel SDK client**: Pass only if `main.py` needs SDK calls. Otherwise omit.

**Metadata / QC results**: If only writing QC at end, return data from `main.py`, call `add_qc_result()` in `run.py`.

```python
# Good — main.py returns data, run.py writes it
qc_data = main(input_file=input_path, threshold=threshold)
gear_context.config.metadata.add_qc_result(**qc_data)

# If metadata needed mid-run or return gets unwieldy: pass config.metadata, not full config
result = main(input_file=input_path, metadata=gear_context.config.metadata)
```

### When Flywheel Coupling Is Acceptable

Some gears are inherently Flywheel-heavy: they traverse containers, resolve subject/session relationships, or act as orchestrators.

**Acceptable coupling:**
- Passing `fw` (the SDK client) when `main.py` needs to query or modify containers
- Passing container IDs when the gear's core logic involves container relationships
- Passing `config.metadata` when metadata must be written incrementally

**Over-engineering to avoid:**
- Passing enormous data structures just to avoid passing `fw` — just pass `fw`
- Complex return types to avoid passing metadata — pass `config.metadata` instead
