---
type: Library Reference
title: "fw-gear Basics: GearContext, Inputs, Outputs"
description: The canonical run.py pattern and how to use GearContext for config, input files, destination container, outputs, logging, and the SDK client.
tags: [fw-gear, gearcontext, gears, python]
timestamp: 2026-07-15T00:00:00Z
---

# fw-gear Basics: GearContext, Inputs, Outputs

## Contents
- [The Canonical run.py Pattern](#canonical-run)
- [Gear Exit Lifecycle](#exit-lifecycle)
- [GearContext Constructor](#constructor)
- [Logging](#logging)
- [Accessing Configuration Options](#config)
- [Accessing Input Files](#inputs)
- [Accessing the Destination Container](#destination)
- [Writing Output Files](#outputs)
- [SDK Client](#sdk-client)
- [Checking Gear Runtime Context](#runtime-context)
- [Accessing Manifest Properties](#manifest)
- [Testing Patterns](#testing)

---

## The Canonical run.py Pattern

The standard gear structure separates `run.py` (entry point) from a `main.py` module
(the actual logic). `run.py` should be minimal.

```python
#!/usr/bin/env python
"""The run script."""
import logging
import sys

from fw_gear import GearContext

from my_gear.main import run
from my_gear.parser import parse_config

log = logging.getLogger(__name__)


def main(context: GearContext) -> int:
    """Parses gear config and runs the gear."""
    args = parse_config(context)
    e_code = run(context, **args)
    return e_code


if __name__ == "__main__":
    with GearContext() as gear_context:
        gear_context.init_logging()
        gear_context.log_config()
        e_code = main(gear_context)
        # Exit inside the block: GearContext writes metadata only on a 0 exit
        sys.exit(e_code)
```

**Always** use `GearContext` as a context manager (`with` block). It handles
initialization and cleanup, including writing `.metadata.json` on exit.

**`sys.exit(e_code)`** — use the return code from `run()`, not just `sys.exit(0)`.
Flywheel marks the job as failed if the process exits with a non-zero code.

---

## Gear Exit Lifecycle

`GearContext.__exit__` (fw-gear 0.3.7, `fw_gear/context.py:271`) decides between the
success path and the failure path from the exception it sees:

```python
if exc_type is None or (issubclass(exc_type, SystemExit) and exc_value.code == 0):
    ...metadata.write(...)       # success: write .metadata.json
elif self._clean_on_error:
    self._clean_output()         # failure: optionally clean outputs
```

`SystemExit(0)` is treated as success on purpose, so where `sys.exit()` runs decides
what a failed run does:

| | Exit code 0 | Non-zero exit |
|---|---|---|
| `sys.exit()` inside the `with` block | metadata written | metadata not written; outputs cleaned if `clean_on_error` |
| `sys.exit()` after the `with` block | metadata written | metadata written anyway; `clean_on_error` never fires |

### The rule

**Call `sys.exit(e_code)` inside the `with` block.** Exiting after the block makes
`__exit__` see a clean exit every time, so a failed gear writes its metadata as if it
succeeded. Having `main()` return the exit code (instead of calling `sys.exit` itself)
keeps `main()` testable; the skeleton calls `sys.exit` inside `main()`, which is
equivalent at runtime.

```python
# CORRECT — __exit__ sees the real exit code
if __name__ == "__main__":
    with GearContext() as gear_context:
        gear_context.init_logging()
        e_code = main(gear_context)
        sys.exit(e_code)
```

```python
# WRONG — __exit__ always sees a clean exit, so failed runs write metadata
if __name__ == "__main__":
    with GearContext() as gear_context:
        gear_context.init_logging()
        e_code = main(gear_context)

    sys.exit(e_code)
```

### Exception handling in run()

The `run()` function in `main.py` should catch exceptions, log them, and return a
non-zero exit code — never let exceptions propagate up through the `with` block
uncontrolled.

```python
def run(context: GearContext, **args) -> int:
    """Main gear logic. Returns 0 on success, 1 on failure."""
    try:
        do_the_work(context, **args)
    except Exception as e:
        log.exception(e)
        return 1
    return 0
```

**Why `log.exception()` instead of re-raising:**
- `log.exception()` captures the full traceback in the gear log where it's visible
  to anyone debugging the job
- Returning 1 instead of raising lets `main()` pass the code to `sys.exit(1)` inside
  the `with` block, so `GearContext` takes its failure path (no metadata, outputs
  cleaned if `clean_on_error`) with a controlled log line instead of a raw traceback
- A re-raised exception takes the same failure path in `__exit__`; the difference is
  only what lands in the log

### Expected exceptions vs. unexpected

You can differentiate between known failure modes (return gracefully) and unexpected
errors (log the traceback):

```python
def run(context: GearContext, **args) -> int:
    """Main gear logic."""
    try:
        validate_inputs(context)
    except PreviousRunError as e:
        log.warning(e)  # Known, non-error condition
        return 0

    try:
        process_data(context, **args)
    except Exception as e:
        log.exception(e)  # Unexpected failure — log full traceback
        return 1
    return 0
```

### Suppressing httpx Logging

When the gear is at INFO level, the httpx client (used by fw-client) logs every request.
Suppress it to keep logs clean:

```python
if logging.root.level == logging.INFO:
    logging.getLogger("httpx").setLevel(logging.WARNING)
```

Add this after `gear_context.init_logging()` in the `__main__` block.

---

## GearContext Constructor

```python
GearContext(
    gear_path="/flywheel/v0",          # Default; where config.json/manifest.json live
    manifest_path="/flywheel/v0/manifest.json",
    config_path="/flywheel/v0/config.json",
    log_metadata=True,                  # Log metadata contents on write
    fail_on_validation=True,            # Fail gear if metadata validation fails
    clean_on_error=False,               # Delete output dir on exception if True
)
```

---

## Logging

```python
# In the __main__ block, before calling main():
context.init_logging()   # Sets INFO by default, DEBUG if config["debug"] is True
context.log_config()     # Logs destination container and all input file paths
```

Use standard `logging` throughout your gear code — do not use `print()`.

When `debug` is `True`, `GearContext` automatically logs all SDK API calls (endpoint
and count) on context exit. This is useful for profiling SDK usage without extra code.

**Log routing:** `INFO` and `WARNING` go to stdout; `DEBUG`, `ERROR`, and `CRITICAL`
go to stderr. Flywheel captures both streams in the job log.

**Log size guidance:** Keep logs under 1 MB (ideally < 10 KB). Flywheel may truncate
large logs. Avoid logging every iteration of a loop; log the start/end of operations
instead.

```python
import logging
log = logging.getLogger(__name__)

log.info("Processing file: %s", input_path)
log.debug("Threshold value: %s", threshold)
log.error("Failed to process: %s", str(e))
```

---

## Accessing Configuration Options

Configuration options come from `context.config.opts` (a dict built from `config.json`):

```python
# Get with default
threshold = context.config.opts.get("threshold", 0.5)
debug = context.config.opts.get("debug", False)

# Get required option (raises KeyError if missing)
mode = context.config.opts["mode"]
```

---

## Accessing Input Files

Inputs are files passed to the gear at runtime. Use the input name as defined in
`manifest.json`.

```python
# Get the full path to an input file (returns Path or None if optional and absent)
dicom_path = context.config.get_input_path("dicom")

# Get just the filename
filename = context.config.get_input_filename("dicom")

# Open the file directly
with context.config.open_input("dicom", "rb") as f:
    data = f.read()

# Get the raw input dict (contains hierarchy, location, object metadata)
input_obj = context.config.get_input("dicom")

# Get a specific metadata field from the file object in config.json
file_type = context.config.get_input_file_object_value("dicom", "type")
```

**Always check for None** when inputs are optional:
```python
dicom_path = context.config.get_input_path("dicom")
if dicom_path is None:
    log.info("No dicom input provided, skipping")
    return
```

---

## Accessing the Destination Container

The destination is where the gear is running (e.g., an acquisition or analysis).

```python
# The raw destination dict (always available, no SDK required)
dest_type = context.config.destination.get("type")   # e.g., "acquisition", "analysis"
dest_id = context.config.destination.get("id")

# Subscript notation also works (use when you know the key exists)
dest_id = context.config.destination["id"]

# Get the actual SDK container object (requires api-key input)
dest_container = context.config.get_destination_container()

# Get the parent of the destination (requires api-key input)
dest_parent = context.config.get_destination_parent()
```

### Navigating the Destination Hierarchy (SDK)

When you need the analysis container and its parent hierarchy:

```python
# For an analysis-level gear:
dest_id = context.config.destination["id"]
analysis = context.client.get_analysis(dest_id)
run_level = analysis.parent["type"]     # "project", "subject", or "session"
parent_id = analysis.parent["id"]

# Get all ancestor IDs
hierarchy = analysis.parents  # dict: {"group": "...", "project": "...", "subject": "...", etc.}
project_id = hierarchy["project"]
group_id = hierarchy["group"]

# Get the parent container dynamically (without knowing its type ahead of time)
get_fn = getattr(context.client, f"get_{analysis.parent.type}")
parent = get_fn(analysis.parent.id)
```

### Destination Dict Access Note

Both `destination.get("type")` and `destination["type"]` work. Prefer `.get("type", "")`
when the value might be absent; use `destination["type"]` when it's always present (e.g.,
in the context of an analysis gear where `type` is always set).

---

## Writing Output Files

All files written to `context.output_dir` are saved to Flywheel when the gear exits
successfully. Files in `context.work_dir` are scratch space and not saved.

```python
# Write an output file (use open_output for automatic path handling)
with context.open_output("results.nii.gz", "wb") as f:
    f.write(nifti_bytes)

# Access the output directory Path directly (e.g., to pass to a subprocess)
print(context.output_dir)   # Path("/flywheel/v0/output")

# Access the work directory for temp/intermediate files
print(context.work_dir)     # Path("/flywheel/v0/work")
```

---

## SDK Client

The SDK client is auto-initialized when an `api-key` input exists in `config.json`.

```python
# Always guard access to the client
if context.client:
    project = context.client.lookup("group/project-label")
else:
    log.warning("No SDK client available — no api-key input defined")
```

See `fw-gear[sdk]` install extra — the SDK is not bundled by default.

### Extracting the Raw API Key (for FWClient)

When you need an `FWClient` (for HTTP API calls not in the SDK), extract the raw key from
`context.config.inputs`:

```python
from fw_client import FWClient

api_key = None
for inp in context.config.inputs.values():
    if inp.get("base") == "api-key" and inp.get("key"):
        api_key = inp["key"]
        break

if api_key:
    fw = FWClient(api_key=api_key, timeout=300)
```

This relies on the same `api-key` input already declared in the manifest — no extra manifest
entry needed.

---

## Checking Gear Runtime Context

```python
# Returns True when actually running inside a Flywheel gear container
if context.is_fw_context():
    log.info("Running in Flywheel gear context")
else:
    log.info("Running locally")
```

---

## Accessing Manifest Properties

```python
# context.manifest may be None if no manifest.json was found
if context.manifest:
    gear_name = context.manifest.name
    gear_version = context.manifest.version
```

---

## Testing Patterns

Two patterns are used in the wild for unit-testing gear code:

### Option A: Full MagicMock (fast, no filesystem)

Best for unit tests where you control all context access:

```python
from unittest.mock import MagicMock
import pytest
from fw_gear import GearContext
from fw_gear.config import Config

@pytest.fixture
def mock_context(tmp_path):
    context = MagicMock(spec=GearContext)
    context.config = MagicMock(spec=Config)
    context.config.opts = {"debug": False, "threshold": 0.5}
    context.config.destination = {"type": "acquisition", "id": "abc123"}
    context.config.get_input_path = MagicMock(return_value=str(tmp_path / "input.dcm"))
    context.config.get_input_filename = MagicMock(return_value="input.dcm")
    context.config.get_input = MagicMock(return_value={"hierarchy": {"id": "file123"}})
    context.metadata = MagicMock()
    context.output_dir = tmp_path / "output"
    context.work_dir = tmp_path / "work"
    context.client = MagicMock()
    return context
```

### Option B: Real GearContext with test fixture files

Best for integration-style tests where you want to test against a real `config.json`.
Requires test asset files at `tests/assets/gear_run/manifest.json` and `config.json`:

```python
import pathlib
from unittest.mock import MagicMock
import pytest
from fw_gear import GearContext

root_dir = pathlib.Path(__file__).resolve().parent.parent
job_manifest_path = root_dir / "tests/assets/gear_run/manifest.json"
job_config_path = root_dir / "tests/assets/gear_run/config.json"

@pytest.fixture
def gear_context():
    context = GearContext(
        manifest_path=job_manifest_path,
        config_path=job_config_path,
    )
    context._client = MagicMock()  # inject mock SDK client
    return context
```

You can also patch individual `Config` methods with `pytest-mock`:

```python
@pytest.fixture
def mock_get_input_path(mocker):
    return mocker.patch("fw_gear.config.Config.get_input_path")

@pytest.fixture
def mock_get_input(mocker):
    return mocker.patch("fw_gear.config.Config.get_input")
```
