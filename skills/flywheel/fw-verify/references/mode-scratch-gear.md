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

## Manifest fields you'll commonly tweak

- `name` — MUST become `<run-id>-probe` (e.g. `fwv-0806-a3f2-probe`) so cleanup.py
  can find and delete it. Never upload under the template name.
- `custom.gear-builder.image` — keep in sync with name: `<run-id>-probe:0.1.0`.
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

2. Edit `manifest.json` (name/image per above) and inject the payload into
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

3. Build and upload (requires Docker running and `flyw` logged in to the target
   site):

```bash
flyw gear build .
flyw gear upload .
```

4. Run against the dummy project and observe:

```python
gear = fw.lookup("gears/<run-id>-probe")
job_id = gear.run(destination=project, config={"exit_code": 1, "run_id": "<run-id>"})
# poll fw.get_job(job_id).state; then pull logs via /api/jobs/{id}/logs/text
# setup, poll, and log-pull snippets: see [mode-file-curator.md](mode-file-curator.md) steps 2, 4, and 5.
```

   The claim's evidence is the (exit_code → job.state) pair plus `[fwv]` log lines.

5. Cleanup is `cleanup.py --run-id <run-id>` — it deletes the gear by name match.

## Template maintenance

If `flyw gear build/upload` rejects the template after a CLI or spec upgrade:

1. `flyw gear create /tmp/fwv-regen -n fwv-probe -l "fw-verify probe gear"` (basic
   template).
2. Diff the generated manifest/Dockerfile against `assets/probe-gear/`; adopt the
   new required fields.
3. Re-apply: the FWV-PAYLOAD markers in run.py, the `exit_code`/`run_id`/`debug`
   config block, the optional `input-file` input, and the runtime-echo plumbing.
4. Record what changed in `.learnings/LEARNINGS.md`.
