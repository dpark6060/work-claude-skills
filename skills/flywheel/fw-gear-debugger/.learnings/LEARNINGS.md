## Learnings — fw-gear-debugger skill

Format:
```
## [YYYY-MM-DD] | Priority: HIGH/MEDIUM/LOW | Status: OPEN/RESOLVED
**Area:** <section of workflow>
**Summary:** <one line>
**Details:** <what was observed>
**Suggested action:** <what to do differently next time>
```

---

<!-- Append new entries below this line -->

## [2026-04-13] | Priority: HIGH | Status: OPEN
**Area:** Skill workflow — gear config and gear run
**Summary:** `gear config -c KEY=VALUE` sets config options; `gear run --prepare` scaffolds a directory but does NOT create run.sh
**Details:** The skill was missing `flyw gear config -c KEY=VALUE` for setting config values (distinct from `-i` for inputs). `flyw gear run --prepare` creates a gear directory in /tmp (or `-d DIR`), not run.sh. There is no `--dry-run` or run.sh generation built into the CLI.
**Suggested action:** Use `gear run .` (or with `-- --entrypoint=/bin/bash`) directly from the pulled job directory. Include `gear config -c` in the workflow for config overrides.

## [2026-04-13] | Priority: HIGH | Status: RESOLVED
**Area:** Gear code location — mount behavior confirmed
**Summary:** `flyw gear run` mounts individual files/dirs, NOT the whole directory — gear code at `/flywheel/v0/` is preserved
**Details:** `soft-copy:0.6.0` bakes `fw_gear_soft_copy/` and `run.py` into `/flywheel/v0/` in the image. `flyw gear run .` mounts only `config.json`, `manifest.json`, `input/`, `output/`, `work/` individually. Gear code is NOT shadowed and is fully accessible for VSCode breakpoints after attaching to the running container.
**Suggested action:** No workaround needed. `flyw gear run . -- --entrypoint=/bin/bash` is safe and leaves gear code intact.

## [2026-04-13] | Priority: MEDIUM | Status: OPEN
**Area:** Profile selection
**Summary:** Always pass `-P <profile>` — the default profile may point to a stale/unreachable site
**Details:** The `default` profile pointed to `latest.sse.flywheel.io` (timed out) while the correct site was `sse-latest-azure.dev.flywheel.io` (profile: `alatest`). All flyw commands must use `-P alatest` for this site.
**Suggested action:** Confirm which profile to use at the start of each session with `flyw auth status --all` or by asking the user.
