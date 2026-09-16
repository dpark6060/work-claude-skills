---
type: Procedure Reference
title: Mode 1 — direct SDK/core validation
description: Test client-observable claims with a scratch SDK script plus a cross-check of the installed SDK source, recording versions in the evidence.
tags: [fw-verify, sdk, validation]
timestamp: 2026-08-06T00:00:00Z
---

# Mode 1 — direct SDK/core validation

Use for claims observable from a client-side script: finder behavior, return types,
endpoint semantics, quoting rules. Cheapest mode — no instance artifacts beyond an
optional dummy project.

## Script scaffold

Write each claim's probe as its own script in the report directory
(`./claude-work/fw-verify/<run-id>/claimN_<slug>.py`) so verdicts stay re-runnable:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["flywheel-sdk"]
# ///
"""Claim N: <the falsifiable statement>."""

import importlib.metadata
import os

import flywheel

# The env var name is not a convention — it comes from the skill's cache/config.json
# (`get_site_config().api_key_env`). This standalone script reads it literally, so
# substitute the name your config actually carries.
fw = flywheel.Client(os.environ["FW_DEV_API"])
print(f"sdk={importlib.metadata.version('flywheel-sdk')}")
print(f"site={fw.get_config().site.api_url}")

# --- probe ---
result = fw.sessions.find('label="20201224"')
print(f"observed: n={len(result)} type={type(result).__name__}")
print(f"first={result[0].label if result else None!r}")   # repr, so '' vs None is visible
```

Rules:
- Print `repr()` of values so types are unambiguous (`'None'` vs `None`).
- Record the SDK version and site in every script's output — verdicts without
  versions are worthless later.
- Read `~/.claude/skills/shared/flywheel/finder-behaviors.md` before writing any
  finder query.
- **`.reload()` before asserting on `info` or `classification`.** Finder/list
  results are a projection that omits both (`info == {}`, file `info == None`) —
  reading one straight off looks exactly like "the write never stuck" and has
  cost a whole wrong diagnosis. `fw.get_<container>(id)` also works.
- **Do not trust `iter_find` on an unproven container type.** The generic Finder
  pages with `after_id`, and `/gears` ignores it: `fw.gears.iter_find` re-serves
  the same page forever (measured: 3000 results, 250 unique, no end). Use
  `fw.get_all_gears(all_versions=True, ...)` for gears, and prove termination on
  any new container type before putting a Finder in a loop or delete path.

## Source cross-check

Observed behavior is half the evidence; the other half is what the installed code
says (per `~/.claude/skills/shared/flywheel/sdk-investigation.md`):

```bash
python -c "import flywheel, pathlib; print(pathlib.Path(flywheel.__file__).parent)"
rg "call_api\('/bulk/move" <that-path>   # is the endpoint wrapped at all?
```

- Grep endpoint paths, not method names — dynamic delegation hides methods.
- The observed behavior wins over docstrings and annotations. Note disagreements
  in the verdict's Notes.

## When mode 1 is NOT enough

Escalate to mode 2/3 when the claim depends on the gear runtime (staged files,
gear context, exit handling) — a client-side probe can only see the API surface.
See [mode-file-curator.md](mode-file-curator.md) for mode 2 and
[mode-scratch-gear.md](mode-scratch-gear.md) for mode 3.
