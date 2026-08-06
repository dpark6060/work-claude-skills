---
name: fw-verify
description: >
  Empirically verify claims about Flywheel behavior by running real code against a
  live (dev) instance — direct SDK probes, the file-curator gear as a harness, or a
  from-scratch probe gear. Produces a claim-by-claim verdict report
  (CONFIRMED/REFUTED/INCONCLUSIVE) backed by re-runnable scripts. Use whenever a doc,
  MR, review comment, or person asserts Flywheel behavior worth re-deriving instead
  of trusting. MANDATORY TRIGGERS: verify, verify this claim, validate claim,
  double-check, confirm this claim, does flywheel actually, re-derive, prove it,
  test this behavior, empirically, exit code semantics, exit semantics, fw-verify.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# fw-verify — empirical claim validation

You verify claims about Flywheel behavior by running real code against a live
instance. A claim is CONFIRMED, REFUTED, or INCONCLUSIVE only on observed evidence —
never on documentation, memory, or plausibility.

## Before starting

1. Read and summarize `${CLAUDE_SKILL_DIR}/.learnings/LEARNINGS.md` and
   `${CLAUDE_SKILL_DIR}/.learnings/ERRORS.md`.
2. Load config: `${CLAUDE_SKILL_DIR}/cache/config.json`. If missing, STOP and walk
   the user through copying `${CLAUDE_SKILL_DIR}/assets/config.example.json` there
   and filling in: the env var holding their dev-site API key, the namespace group,
   and a site label. Never proceed without it.
3. Auth check — one cheap call before anything else, so a bad key fails here instead
   of halfway through a probe:

```bash
uv run --with flywheel-sdk python -c '
import sys, os, json, flywheel
cfg = json.load(open(sys.argv[1]))["default_site"]
print(flywheel.Client(os.environ[cfg["api_key_env"]]).get_current_user().email)
' "${CLAUDE_SKILL_DIR}/cache/config.json"
```

## Workflow

1. **Intake.** Collect claims from the MR/doc/message. Number each one and restate
   it as a falsifiable statement — use the `ste-writing` skill (STE-flavored mode)
   for the restatements and for any instructions you hand the user (e.g. upload
   requests). The final verdict report is EXEMPT from ste-writing.
2. **Classify each claim onto the ladder** — cheapest mode that can genuinely test
   it (user can force a mode):
   - **Mode 1 — SDK probe** (client-observable: finders, return types, endpoint
     semantics) → read `${CLAUDE_SKILL_DIR}/references/mode-sdk.md`
   - **Mode 2 — file-curator harness** (behavior inside a gear runtime that
     arbitrary Python can observe) → read
     `${CLAUDE_SKILL_DIR}/references/mode-file-curator.md`
   - **Mode 3 — probe gear** (manifest/exit-code/engine semantics ARE the subject)
     → read `${CLAUDE_SKILL_DIR}/references/mode-scratch-gear.md`
3. **Generate a run id** and provision if any claim needs instance data:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/build_project.py" --spec <spec.json> [--run-id <id>] [--site <name>]
```

   Writes a JSON result to stdout: `project_id`, `project_label`, `run_id`,
   `pending_uploads`. Write the spec JSON yourself following
   `${CLAUDE_SKILL_DIR}/assets/hierarchy.example.json` (path depth = level;
   trailing `/` = empty container; per-path `metadata` sets info/classification/
   type/content for containers AND files). Content choices: omit for placeholder
   text; `"fake-dicom"` when only routing/metadata/type-matching is under test;
   `"real"` when something must actually parse the file. Setup problems (missing
   config, unset key env var, bad spec) print `Setup error: ...` to stderr and exit
   non-zero — fix the setup, don't reinterpret it as evidence.
4. **Pending uploads pause.** If `pending_uploads` is non-empty, list each waiting
   path to the user, ask them to upload, and WAIT for confirmation before running
   claims that need those files.
5. **Execute** each claim per its mode reference. Save every probe script to the
   report directory so verdicts are re-runnable.
6. **Report** (see format below).
7. **Cleanup:**

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/cleanup.py" --run-id <id> [--site <name>] [--dry-run]
```

   Run it unless the user asked to keep artifacts. It deletes ONLY artifacts whose
   label/name contains the run id, and refuses ids not matching the `fwv-` run-id
   format (`fwv-MMDD-xxxx`) — a truncated id would match far more than one run.

## Verdict report

Write to `./fw-verify/<run-id>/report.md` (or the user's directory), scripts
alongside. Plain engineering prose — no ste-writing.

    # fw-verify report — <run-id>
    Site: <label> | Group: <group> | Date: <date>
    SDK: <version> | Instance: <api url>

    ## Claim 1: <restated claim>
    Mode: sdk | Script: claim1_<slug>.py
    Verdict: REFUTED
    Observed: <raw output excerpt>
    Notes: <source cross-check, caveats, gear versions>

Verdicts: CONFIRMED / REFUTED / INCONCLUSIVE. An INCONCLUSIVE verdict states
exactly what blocked the test. Chat summary = one verdict line per claim.

## Gotchas

- **A silent probe is INCONCLUSIVE, not REFUTED.** A job that completed with no
  evidence lines usually means the probe code never reached the assertion. Prove the
  probe ran before reading its silence as a result.
- **Job pickup is not instant.** Jobs sit `pending` until an engine claims them, plus
  image pull on a cold engine. Budget minutes; a timeout is a harness problem.
- **A verdict is only valid for the versions you observed.** Record SDK version, gear
  version, and instance URL in the report — the same claim flips across releases.
- **Setup failures are not evidence.** Missing gear, 403, unset env var, bad spec:
  fix the harness and re-run. Never convert an infrastructure error into a verdict.
- **Re-run a REFUTED claim once** before reporting it. A single-run refutation is the
  most expensive thing to get wrong, and dev instances are flaky.
- **Finder queries have quoting rules that fail silently** (numeric labels, parent
  filters). Read `~/.claude/rules/flywheel_specific/sdk/FinderBehaviors.md` before
  writing one, or you will verify your own typo.

## Safety rules

- Deletion ONLY via `cleanup.py`. Never call `fw.delete_*` directly.
- No writes outside the configured namespace group on the target site.
- Creating projects or uploading gears on any site other than `default_site`
  requires explicit user confirmation in chat first.
- API keys come from env vars named in config — never echo, log, or write them
  into reports or scripts.
- Every created artifact (project label, gear name) carries the run id, because
  cleanup matches on it.

## After finishing

Append to `${CLAUDE_SKILL_DIR}/.learnings/LEARNINGS.md` (patterns that worked,
non-obvious behaviors) or `ERRORS.md` (failures, wrong assumptions and fixes).
Skip if nothing surprising happened.
