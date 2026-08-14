---
type: Procedure Reference
title: Mode 3 — from-scratch probe gear
description: Copy the bundled probe-gear template, inject a payload and manifest tweaks, then build/upload/run it to test manifest, exit-code, and engine semantics.
tags: [fw-verify, gear, probe, flyw-cli]
timestamp: 2026-08-06T00:00:00Z
---

# Mode 3 — from-scratch probe gear

Use when the manifest, exit code, or engine handling IS the subject — file-curator
can't fake those because its own manifest is fixed. For runtime-observation claims
that don't need a custom manifest, prefer
[mode-file-curator.md](mode-file-curator.md); it skips the build/upload cost.

## One gear, many versions

The gear name is **always `claude-test-gear`** — never a per-run name. Every run
uploads a new *version* of that one gear and deactivates that version afterwards.
Manifest names allow only lowercase letters, numbers and hyphens, so it is
`claude-test-gear`, not `claude_test_gear`.

The run id no longer lives in the gear name. It goes in the `run_id` **config
value at job time**, which is what ties a job's logs back to the run.

- `name` — leave it as `claude-test-gear`.
- `version` — the one field you must change per run: the next unused version (see
  step 2). `0.1.N` is fine.
- `custom.gear-builder.image` — track name and version: `claude-test-gear:0.1.N`.
- `inputs` / `config` — shape them to the claim (e.g. add a required input to test
  required-input semantics).
- `config.exit_code` — the exit-semantics lever; one config flip per exit code, no
  rebuild needed.

## Workflow

1. Copy the template to a scratch dir:

```bash
cp -r "${CLAUDE_SKILL_DIR}/assets/probe-gear" "${CLAUDE_SKILL_DIR}/cache/<run-id>-probe"
cd "${CLAUDE_SKILL_DIR}/cache/<run-id>-probe"
```

2. **Find the next unused version.** Quick look from the shell first — this is the
   canonical discovery step, and `-a -d` (all versions, disabled included) is the
   CLI spelling of `include_invalid`:

```bash
flyw --profile <site> gear list --filter gear.name=claude-test-gear -a -d
```

   Then compute the next version in Python. `include_invalid=True` is mandatory: without
   it the endpoint hides deactivated versions, and since every previous run
   deactivates the version it used, the visible list is exactly the wrong list to
   compute from — you would re-mint a version that already exists and the upload
   fails. Verified live on 22.3.9: `dicom-qc` reports 11 versions plain and 16
   with the flag; site-wide the counts are 1081 and 1124.

```python
import sys, os
sys.path.insert(0, f"{os.environ['CLAUDE_SKILL_DIR']}/scripts")
from cleanup import PROBE_GEAR_NAME, get_gear_versions   # the verified call

existing = get_gear_versions(fw, PROBE_GEAR_NAME)        # includes deactivated
patches = [
    int(g.gear.version.split(".")[2])
    for g in existing
    if g.gear.version.startswith("0.1.") and g.gear.version.split(".")[2].isdigit()
]
next_version = f"0.1.{max(patches) + 1 if patches else 0}"
print(next_version, "| existing:", sorted(g.gear.version for g in existing))
```

   `get_gear_versions` is `fw.get_all_gears(all_versions=True,
   include_invalid=True, filter=f"gear.name={name}")` — server-side filtered, so
   it returns only this gear's versions rather than all 1124. It returns `[]`
   before the first upload, which yields `0.1.0`.

3. Edit `manifest.json` (version/image per above) and inject the payload into
   `run.py` between the FWV-PAYLOAD markers. The markers live inside `main()`, so
   the exact lines in the template are indented four spaces:

```python
    # >>> FWV-PAYLOAD-START  (fw-verify injects test code below this line)
    # <<< FWV-PAYLOAD-END
```

   Every injected line must carry that same four-space indent to sit inside
   `main()` — otherwise `run.py` is a syntax error and the job fails during build
   or on first execution, which looks like a verdict but isn't. If the payload
   needs its own helpers or imports, define them at module level above `main()`
   and call them from the marker block, which stays a one-line call at four-space
   indent.

   Payload prints go through `print("[fwv] ...")` so evidence greps cleanly. The
   template's own plumbing prints under the distinct `[fwv-probe]` prefix, so
   `[fwv]` selects payload lines only, `[fwv-probe]` the fixed echo lines only,
   and `[fwv` both. **Match these as fixed strings, not regexes** — `rg '[fwv]'`
   is a bracket character class that matches any `f`, `w`, or `v` in the log. Use
   `rg -F '[fwv]'`, or extract in Python the way
   [mode-file-curator.md](mode-file-curator.md) step 5 does
   (`[ln for ln in logs.splitlines() if "[fwv]" in ln]`), which is the canonical
   form since you're already holding the log text there.

4. Build and upload (requires Docker running and `flyw` logged in to the target
   site):

```bash
flyw gear build .
flyw gear upload .
```

5. Run against the dummy project and observe. The run id travels in the config,
   not the gear name:

```python
gear = fw.lookup("gears/claude-test-gear")   # resolves the latest active version
job_id = gear.run(
    destination=project,
    config={"exit_code": 1, "run_id": "<run-id>"},
    tags=["static"],   # ALWAYS: routes the job to the static engine
)
# poll fw.get_job(job_id).state; then pull logs with fw.get_job_logs(job_id)
# setup, poll, and log-pull snippets: see [mode-file-curator.md](mode-file-curator.md) steps 2, 4, and 5.
```

   The claim's evidence is the (exit_code → job.state) pair plus `[fwv]` log lines.

   Without the `static` tag a job on latest/alatest can sit `pending` for minutes
   waiting for a dynamic engine (measured: 5.5 min untagged vs 15 s tagged on the
   same day). Add `tags=["static"]` to every probe launch.

6. Cleanup deactivates the exact version this run uploaded:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/cleanup.py" --run-id <run-id> --gear-version 0.1.N --dry-run
uv run "${CLAUDE_SKILL_DIR}/scripts/cleanup.py" --run-id <run-id> --gear-version 0.1.N
```

   Exact name plus exact version, no substring matching — a loose match could
   disable a version another run is still using. The summary JSON reports it under
   `gear_versions_deactivated`. Already-deactivated versions are skipped, so
   re-running is safe. Omit `--gear-version` when the run used no probe gear.

   "Deactivated" means `fw.delete_gear(gear_id)`, whose SDK docstring is "Delete a
   gear (not recommended) / **Disable a gear by id**" — it is a soft disable, not a
   removal: the version keeps existing and comes back from the API with a
   `disabled` timestamp, which is why step 2 must ask for invalid versions. Note
   `disabled` is a **timestamp or `None`**, not a boolean, and it lives on the
   gear *document* (`gear.disabled`), not the manifest (`gear.gear` has no
   `disabled`). Live-confirmed on 22.3.9 (runs fwv-0806-d340 and fwv-0806-fc9d):
   the version goes `disabled` rather than vanishing, the next run's version
   calculation still sees it, and `fw.delete_gear` needs no `delete_reason` even
   on an audit-trail site.

## Template maintenance

If `flyw gear build/upload` rejects the template after a CLI or spec upgrade:

1. `flyw gear create /tmp/fwv-regen -n claude-test-gear -l "fw-verify probe gear"`
   (basic template).
2. Diff the generated manifest/Dockerfile against `assets/probe-gear/`; adopt the
   new required fields.
3. Re-apply: the FWV-PAYLOAD markers in run.py, the `exit_code`/`run_id`/`debug`
   config block, the optional `input-file` input, and the runtime-echo plumbing.
4. Record what changed in `.learnings/LEARNINGS.md`.
