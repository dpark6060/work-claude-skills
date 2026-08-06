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
`pyproject.toml`. Gear image `flywheel/file-curator:1.0.4`. The manifest carries no gear-level
field; the README's classification checklist marks the gear **acquisition**-level, which is where
the destination guidance below comes from — inferred from docs, not from the manifest.

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
    `fw-file`, `fw-gear`. Image Python is 3.13 per the manifest's `PYTHON_VERSION`
    (its `PYTHONPATH` still points at `python3.12/site-packages` — the two contradict each
    other; check at runtime rather than trusting either).

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

2. Upload both required inputs to the dummy project and defensively set the script's file
   type. The target file for `file-input` can be one `scripts/build_project.py` already
   created (e.g. `sub-01/ses-01/acq-01/image.dcm` in `assets/hierarchy.example.json`) — in
   that case skip its upload and just fetch the acquisition. Otherwise upload one:

```python
import io
import os
import sys
from pathlib import Path

import flywheel

# Read from the env var rather than pasting a path: "${CLAUDE_SKILL_DIR}" does
# not expand inside a Python string. Or just run this from the skill's scripts/ dir.
sys.path.insert(0, f"{os.environ['CLAUDE_SKILL_DIR']}/scripts")
from fwv_common import get_api_key, get_site_config

cfg = get_site_config()          # default site from cache/config.json
api_key = get_api_key(cfg)       # resolved from the env var named in that config
group_id = cfg.group
project_label = "..."            # "project_label" from build_project.py's printed JSON

fw = flywheel.Client(api_key)
project = fw.lookup(f"{group_id}/{project_label}")           # the fwv-<run_id> dummy project
acquisition = fw.lookup(f"{group_id}/{project_label}/sub-01/ses-01/acq-01")

# The curator script.
script = Path("probe_curator.py").read_bytes()
project.upload_file(
    flywheel.FileSpec("probe_curator.py", io.BytesIO(script), size=len(script))
)

# The file the curator will be handed, if the dummy project doesn't already have one.
payload = b"fw-verify placeholder\n"
acquisition.upload_file(
    flywheel.FileSpec("image.dcm", io.BytesIO(payload), size=len(payload))
)

project = project.reload()          # so get_file sees the new files
acquisition = acquisition.reload()

# The manifest restricts the curator input to file type "source code"; don't rely on
# the classifier having typed the .py upload that way.
project.update_file("probe_curator.py", {"type": "source code"})
```

3. Launch. Destination should be the container that owns `file-input` (the gear is
   acquisition-level per the README):

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
    tags=["static"],   # ALWAYS: routes the job to the static engine (15s pickup vs minutes)
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

5. Pull logs and extract `[fwv]` lines as evidence. `fw.get_job_logs(job_id)` is on the
   SDK client (live-verified fwv-0806-fc9d) — no separate HTTP client needed. One caveat:
   each entry's `.msg` can be a multi-line block, so split before grepping:

```python
logs = fw.get_job_logs(job_id)
lines = [ln for entry in logs.logs for ln in entry.msg.splitlines()]
evidence = [ln for ln in lines if "[fwv]" in ln]
failure = [ln for ln in lines if "Curation failed:" in ln]
```

## Gotchas

- **The class must be named `Curator`.** `load_curator` does `getattr(mod, "Curator")`;
  any other name is an `AttributeError` at load time.
- **The manifest's own `curator` description is stale.** In 1.0.4 it still links
  gear-toolkit's `FileCurator` docs
  (`flywheel_gear_toolkit/utils/#curator`) — that is the v0 contract, and v1.x AST-rejects
  gear-toolkit imports. Ignore the manifest description; the README and this doc are right.
- **`self.config` is not the gear config.** The gear passes only `context=`, so
  fw-curation's base `Curator.__init__` (the parent of `FileCurator`) builds a default
  `CurationConfig`. Gear config lives at
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

## Live-verified (run fwv-0806-fc9d, alatest 22.3.9, file-curator 1.0.4-dev)

- `gear.run(inputs=...)` with SDK file objects (as written above) works as-is.
- `destination=acquisition` (the file's parent) works. Project-level destination untested.
- The `[fwv]` prefix survives into the job log (`fw.get_job_logs`) — the gear's log
  formatter prepends timestamp/level/module but leaves the message intact.
- alatest ships `1.0.4-dev`, which matches this 1.0.4 contract.
- Job pickup with `tags=["static"]` was 15 s; an untagged mode-3 job the same day sat
  pending 5.5 min. Always tag.
- Still untested: whether the `curator` input's `enum: ["source code"]` type restriction
  is enforced at job creation (step 2 sets the type defensively either way).
