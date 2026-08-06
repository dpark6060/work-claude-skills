---
type: Procedure Reference
title: Mode 2 — file-curator as a test harness
description: Launch the file-curator gear with a custom curator script to observe behavior inside a real gear runtime, and read verdict evidence back out of job logs.
tags: [fw-verify, file-curator, gear-harness]
timestamp: 2026-08-06T00:00:00Z
---

# Mode 2 — file-curator as a test harness

Use when the claim is about behavior *inside* a gear runtime (context contents, file
staging, metadata writes, environment) and arbitrary Python running in a gear can
observe it. Cheaper than building a gear; can't test manifest/exit-code semantics
(that's mode 3).

## Contract (verified against file-curator v1.0.4 on 2026-08-06)

Read from `https://gitlab.com/flywheel-io/scientific-solutions/gears/file-curator`
(`main`): `manifest.json`, `README.md`, `run.py`, `fw_gear_file_curator/{main,parser,utils}.py`,
`pyproject.toml`. Gear image `flywheel/file-curator:1.0.4`, gear level **acquisition**.

- Gear lookup: `fw.lookup("gears/file-curator")`
- Inputs:

| Input | Base | Required | Notes |
|---|---|---|---|
| `file-input` | `file` | yes | The file handed to the curator. Any file works; the gear downloads it. |
| `curator` | `file` | yes | The Python script. Manifest restricts it to file type `source code`. |
| `additional-input-one` | `file` | no | Path exposed on the curator as `self.additional_input_one`. |
| `additional-input-two` | `file` | no | Path exposed as `self.additional_input_two`. |
| `requirements` | `file` | no | `requirements.txt`, pip-installed before the script loads. |
| `api-key` | `api-key` | n/a | Supplied by the platform — never pass it in `inputs`. Its presence is why `self.context.client` works. |

- Config: `debug` (boolean, default `false` — sets log level to DEBUG),
  `tag` (string, default `""` — **non-empty values tag the input file after a successful
  run, which mutates data; leave it empty**), `install-latest-flywheel-sdk` (boolean,
  default `false` — pip-installs and reloads the newest `flywheel-sdk` at runtime; use it
  only when the claim is about a newer SDK than the image ships).

- Curator script contract:
  - The module must define a class named exactly `Curator` (the gear does
    `getattr(mod, "Curator")`), subclassing `FileCurator` from **`fw_curation.curator`**
    — *not* `flywheel_gear_toolkit`, which v1.x actively rejects (see Gotchas).
  - Define `curate_file(self, file_)`. Optionally define
    `validate_file(self, file_) -> bool`; the base returns `True`. The gear calls
    `curator.curate_container(file_input)`, and `FileCurator.curate_container` is just
    `if self.validate_file(container): self.curate_file(container)`.
  - Instantiated as `Curator(context=gear_context, additional_input_one=..., additional_input_two=...)`.
    The base `Curator.__init__` `setattr`s every kwarg, so inside the script you get
    `self.context` (an `fw_gear.GearContext`), `self.additional_input_one`,
    `self.additional_input_two` (both `Path` or `None`).
  - Useful `self.context` surface: `self.context.config.opts` (gear config dict),
    `self.context.config.destination` (`{"type": ..., "id": ...}`),
    `self.context.config.get_input_path("...")`, `self.context.client` (SDK client),
    `self.context.metadata`, `self.context.work_dir`, `self.context.output_dir`.
  - `file_` is the raw input dict, not an SDK object:

    ```python
    {"base": "file",
     "location": {"path": "/flywheel/v0/input/file-input/<name>", "name": "<name>"},
     "hierarchy": {"type": "<container_type>", "name": "<file_name>"},
     "object": {"info": {}, "mimetype": ..., "tags": [], "type": ..., "size": ...}}
    ```

    (`file_["object"]["file_id"]` is also present — `run.py` uses it for tagging.)

  - Extra pip packages: set a module-level `EXTRA_PACKAGES = ["polars"]` list, or pass a
    `requirements` input. Preinstalled per the README: `lxml`, `pandas`, `nibabel`,
    `Pillow`, `piexif`, `pydicom`, `pypng`, `flywheel-sdk`, `fw-client`, `fw-curation`,
    `fw-file`, `fw-gear`. Image Python is 3.13.

- Error/exit semantics (this is what the skill greps against):
  - `main.curate` wraps curation in `try/except Exception` and logs exactly
    **`Curation failed: {e}`** — one line, **no traceback** — then returns `1`;
    `run.py` does `sys.exit(1)`, so the job state is `failed`.
  - A failed job therefore means "the curator raised", not "the harness broke". Treat
    `Curation failed:` in the log as evidence, not as an infrastructure error.
  - If you want a traceback, catch it yourself in `curate_file` and
    `log.exception(...)` before re-raising.
  - Preflight failures (`parser.parse_config`) exit `1` *before* the script runs:
    missing curator input, missing file input, failed `EXTRA_PACKAGES` install, or a
    v0-compatibility rejection.
  - Logging is set up by `context.init_logging()`; use `logging.getLogger(__name__)`.
    Plain `print` also lands in the job log.

## Workflow

1. Write the curator script: subclass `fw_curation.curator.FileCurator` as `Curator`; put
   observations in `log.info(...)` lines prefixed `[fwv]` so they're greppable in job logs.

```python
import logging
from fw_curation.curator import FileCurator

log = logging.getLogger(__name__)


class Curator(FileCurator):
    """fw-verify probe: observe gear runtime state, then report."""

    def curate_file(self, file_):
        log.info(f"[fwv] file_keys={sorted(file_.keys())}")
        log.info(f"[fwv] location={file_['location']}")
        log.info(f"[fwv] destination={self.context.config.destination}")
        log.info(f"[fwv] opts={self.context.config.opts}")
        # ...the actual claim under test goes here, one [fwv] line per observation
```

2. Upload the script to the dummy project (any container file works as a gear input):
   `project.upload_file("probe_curator.py")`. Re-read the container afterward
   (`project = project.reload()`) so `get_file` sees it.
3. Launch. Destination should be the container that owns `file-input` (the gear is
   acquisition-level):

```python
gear = fw.lookup("gears/file-curator")
print(gear.gear.version)   # confirm the site's version matches this contract

job_id = gear.run(
    destination=acquisition,
    inputs={
        "curator": project.get_file("probe_curator.py"),
        "file-input": acquisition.get_file("image.dcm"),
    },
    config={"debug": True},
)
```

4. Poll until terminal state (complete/failed), timeout ~10 min:

```python
import time

while True:
    job = fw.get_job(job_id)
    if job.state in ("complete", "failed", "cancelled"):
        break
    time.sleep(10)
```

5. Pull logs and extract `[fwv]` lines as evidence:

```python
logs = fw_http.get(f"/api/jobs/{job_id}/logs/text", raw=True).text
evidence = [ln for ln in logs.splitlines() if "[fwv]" in ln]
failure = [ln for ln in logs.splitlines() if "Curation failed:" in ln]
```

## Gotchas

- **The class must be named `Curator`.** `load_curator` does `getattr(mod, "Curator")`;
  any other name is an `AttributeError` at load time.
- **`self.config` is not the gear config.** The gear passes only `context=`, so the base
  class builds a default `fw_curation` `CurationConfig`. Gear config lives at
  `self.context.config.opts`. `self.reporter` is `None` unless you set one up.
- **v1.x statically rejects v0 scripts.** `check_script_version` AST-parses the script
  before running it and exits `1` if it finds `import flywheel_gear_toolkit`,
  `from flywheel_gear_toolkit... import ...`, or an `extra_packages=` kwarg in
  `Curator.__init__`. The log line is "Curation script not compatible with File Curator
  version 1+". If the site only has file-curator 0.x installed, invert this: use
  `flywheel_gear_toolkit.utils.curator.FileCurator` and `self.context` as a
  `GearToolkitContext`, where the destination is `self.context.destination` rather than
  `self.context.config.destination`.
- **Version-pin the reading, not just the run.** `fw.lookup("gears/file-curator")` returns
  whatever version that site has installed, which may predate 1.0.4. Print
  `gear.gear.version` and, if it isn't 1.0.x, re-check the contract before trusting this
  doc.
- **The gear must be installed on the site.** `fw.lookup` raises `ApiException` (404) if
  it isn't; that's a harness problem, not a verdict.
- **Job pickup is not instant.** The job sits in `pending` until an engine claims it, plus
  image pull on a cold engine. Budget minutes, not seconds, before calling a timeout real.
- **Leave `tag` empty.** A non-empty `tag` makes `run.py` call
  `context.metadata.add_file_tags` on the input file — a real mutation on the dummy
  project, and one more thing cleanup has to undo.
- **`EXTRA_PACKAGES` / `requirements` cost wall-clock.** Every run pip-installs them
  fresh. Prefer the preinstalled set when the claim doesn't need anything else.
- **Curation is silent on success.** If `validate_file` returns `False`, `curate_file`
  never runs and the job still completes with exit `0` — an empty `[fwv]` evidence list
  with a `complete` job usually means that, not "nothing happened".

## Verify at first live run

- The exact `gear.run(inputs=...)` reference form — SDK file object (as written above) vs
  a `{"type": ..., "id": ..., "name": ...}` dict. Correct this doc if reality differs.
- Whether `destination` must be the file's parent acquisition, or whether a project-level
  destination is accepted for this acquisition-level gear.
- Whether the `curator` input's manifest type restriction (`enum: ["source code"]`) is
  enforced at job creation, and whether a `.py` upload is auto-typed `source code` or
  needs an explicit `file.update(type="source code")`.
- The file-curator version actually installed on the target site (this contract is 1.0.4).
- That the `[fwv]` prefix survives into `/api/jobs/{job_id}/logs/text` unmangled by the
  gear's log formatter.
