---
name: fw-gear
description: >
  Write Python gear code using the fw-gear library — GearContext, run.py, config/input
  access, metadata writing, manifest.json. Use when the user is building, updating, or
  debugging a Flywheel gear even if they don't say "fw-gear" explicitly.
  MANDATORY TRIGGERS: gear, run.py, GearContext, manifest.json, flywheel gear,
  gear input, gear output, gear config, api-key input, context.client,
  context.destination, context.config.destination, destination container,
  get_destination_container, get_destination_parent, gear destination,
  parse_config, init_logging, log_config, context.work_dir, context.output_dir,
  fw_gear, fw-gear
version: 2026-03-03
tags:
  - python
  - flywheel
  - fw-gear
  - gear
  - code-generation
---

# fw-gear

## Overview

`fw-gear` is the standard Python library for writing Flywheel gears. A gear is a
containerized algorithm that runs on Flywheel's compute infrastructure, with access
to input files from the Flywheel data hierarchy and the ability to write output files
and metadata back to the platform.

`fw-gear` replaces the older `flywheel-gear-toolkit` package. All new gears should use
`fw-gear`.

## Installation

```bash
pip install fw-gear              # Basic
pip install fw-gear[sdk]         # With Flywheel SDK client support
pip install fw-gear[dicom]       # fw-file + nibabel for DICOM handling
pip install fw-gear[fw-file]     # fw-file support for various file types
pip install fw-gear[nipype]      # nipype + nibabel for workflow integration
pip install fw-gear[numpy]       # numpy array JSON support
pip install fw-gear[all]         # All extras
```

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`.
Summarizing (not just reading) forces you to internalize what has and hasn't worked
in previous runs of this skill.

## After Finishing

If this session produced anything worth capturing, append to the relevant file:
- **`.learnings/LEARNINGS.md`** — a pattern that worked well or a non-obvious fw-gear behavior.
- **`.learnings/ERRORS.md`** — a wrong method name, incorrect import path, or API pattern
  that had to be corrected (especially anything from the old flywheel-gear-toolkit API).

Don't write an entry if nothing went wrong and nothing surprising happened.

---

## File Layout Is Not Yours To Change

Gears start from the skeleton template, and its file and module names are the standard:
`run.py` at the repo root, `fw_gear_<name>/main.py`, `fw_gear_<name>/parser.py`. **Never rename
them** — not to `gear_config.py`, not to `pipeline.py`, not because a design doc or module tree
says otherwise. Adding modules (`models.py`, `fw_ops.py`, …) is fine; renaming what ships is not.

Read `~/.claude/rules/flywheel_specific/gears/GearStructure.md` before creating or renaming any
file in a gear repo. It has the full sanctioned list and the reject table.

## Guide Index

Load the relevant guide(s) based on your task:

- **[gear-basics.md](references/gear-basics.md)** - GearContext, the canonical `run.py`
  pattern, accessing config options and input files, writing output files, work directory
- **[gear-metadata.md](references/gear-metadata.md)** - Writing `.metadata.json`, updating
  container and file metadata, adding QC results and file tags, SDK-enabled metadata methods
- **[metadata-capability-matrix.md](references/metadata-capability-matrix.md)** - Decision
  reference: what `context.metadata` CAN/CANNOT write (per-field file-vs-container matrix),
  the 0.3.1 api-key requirement, and the destination-and-up hierarchy rule
- **[gear-utils.md](references/gear-utils.md)** - Running external commands (`exec_command`),
  ZIP archive utilities, SDK retry handlers, launching child gears (`setup_gear_run`),
  Nipype integration, resource/FD monitoring
- **[gear-manifest.md](references/gear-manifest.md)** - `manifest.json` structure, config
  and input field definitions, api-key inputs, output metadata spec

## Guide Selection Strategy

**Writing a new gear or run.py?** Load gear-basics.md first.

**Writing output metadata or QC results?** Load gear-metadata.md.

**Deciding whether `context.metadata` can even do what you need (fields, api-key, hierarchy)?** Load metadata-capability-matrix.md.

**Calling an external binary or subprocess?** Load gear-utils.md.

**Defining or editing manifest.json?** Load gear-manifest.md.

**Full gear from scratch?** Load all four guides.

## Key Concepts

- All gear code runs inside a Docker container at `/flywheel/v0`
- `GearContext` is the central object — always use it as a context manager
- Inputs land at `/flywheel/v0/input/<input-name>/<filename>` at runtime
- Output files go to `/flywheel/v0/output/` — anything there is saved to Flywheel
- `context.work_dir` (`/flywheel/v0/work/`) is scratch space, not saved
- The SDK client is only available if an `api-key` input is defined in the manifest
- Metadata can be written without the SDK via `.metadata.json`; use the SDK for
  containers outside the destination hierarchy

## Code Quality Standards

All gear code you write should:
1. Use `GearContext` as a context manager (the `with` pattern)
2. Call `context.init_logging()` and `context.log_config()` at startup
3. Place `sys.exit(e_code)` **outside** the `with GearContext()` block — never inside it. `main()` returns the exit code; `sys.exit()` happens after context cleanup. See the Gear Exit Lifecycle section in gear-basics.md.
4. Catch exceptions in `run()` with `log.exception()` and return 1 — never let exceptions propagate uncontrolled through the context manager
5. Use correct method names from the guides (not outdated `flywheel-gear-toolkit` names)
6. Only access `context.client` if the gear manifest declares an `api-key` input
7. Access the destination via `context.config.destination["id"]` (a dict on `context.config`) — **never** `context.destination.id`. That attribute does not exist and will raise `AttributeError`. For the SDK container, use `context.config.get_destination_container()`. See gear-basics.md.
8. Follow project coding conventions (`~/.claude/rules/general_coding/`) and gear structure rules (`~/.claude/rules/flywheel_specific/gears/GearStructure.md`)
