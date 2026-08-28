---
name: fw-gear-debugger
description: >
  Debug failed Flywheel gear jobs locally — pull a job, set up a local debug environment,
  create dev.py scripts, and attach VSCode to a gear container. Use even when the user
  doesn't say "debug" explicitly — triggers on gear failures, job errors, and container issues.
  MANDATORY TRIGGERS: debug gear, gear failed, job failed, gear error, gear crash, pull job,
  gear not working, troubleshoot gear, dev.py, attach VSCode, flyw job pull
version: 1.0.0
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`.
Summarizing (not just reading) forces you to internalize what has and hasn't worked
in previous debug sessions.

## After Finishing

If this session produced anything worth capturing, append to the relevant file:
- **`.learnings/LEARNINGS.md`** — a non-obvious pattern, workaround, or approach that worked well.
- **`.learnings/ERRORS.md`** — an unexpected container setup, gear structure quirk, or gotcha
  that had to be worked around (Apple Silicon issues, non-standard entrypoints, etc.).

Don't write an entry if nothing went wrong and nothing surprising happened.

---

## Workflow Overview

```
1. Pull the failed job         →  flyw job pull <JOB_ID>
2. Re-add the API key          →  flyw gear config -i api_key=$MY_API_KEY
3. Adjust config if needed     →  flyw gear config -c debug=true
4. Generate run.sh             →  flyw gear run --prepare
5. Launch container with bash  →  flyw gear run . -- --entrypoint=/bin/bash
6. Debug inside container      →  python -m pdb run.py  OR  dev.py (VSCode)
7. Generate HOW_TO.md          →  so the user can re-launch easily
```

## Step 1: Pull the Failed Job

```bash
flyw job pull <JOB_ID>
flyw job pull <JOB_ID> /path/to/debug/dir
flyw --profile mysite job pull <JOB_ID> /path/to/debug/dir
```

### Options

| Option | Description |
|---|---|
| `JOB_ID` | Job ID [required] |
| `DIR` | Output directory [optional] |
| `--image / --no-image` | Pull gear image if not present |

### Pulled Directory Structure

```
<gear-name>-<version>-<job-id>/
├── config.json          # Job configuration (API key redacted)
├── manifest.json        # Gear manifest
├── input/
│   └── <input-name>/
│       └── <file>
├── output/
├── run.sh
└── work/
```

## Step 2: Re-add the API Key and Adjust Config

`flyw job pull` redacts the API key in `config.json`. Add it back:

```bash
cd <gear-name>-<version>-<job-id>/
flyw gear config -i api_key=$MY_API_KEY
```

The key must be for the site the job ran on. Which sites there are keys for, and where
they live (`~/.fw/config.yml` profiles, env-var fallbacks):
`~/.claude/skills/shared/flywheel/instance-access.md`. Export it into the environment —
don't paste a key value into `config.json` or any file you keep.

Optionally override config values (types inferred from manifest):

```bash
flyw gear config -c debug=true
flyw gear config -c my_string='some value'
flyw gear config -c my_int=2
```

## Step 3: Generate run.sh

Run `--prepare` to create a `run.sh` in the pulled directory. This is the recommended way to launch for both normal testing and VSCode debugging:

```bash
flyw gear run --prepare
```

This creates a `run.sh` with the exact `docker run` command needed. You can then run the gear with:

```bash
bash run.sh            # run gear normally
```

Or edit `run.sh` to override the entrypoint for interactive debugging.

## Step 4: Launch the Container

```bash
# Interactive bash shell
flyw gear run . -- --entrypoint=/bin/bash

# Pass environment variables
flyw gear run . -- -e FW_API_KEY=$MY_API_KEY --entrypoint=/bin/bash

# Pass-through Docker args (e.g. GPUs)
flyw gear run . -- --gpus all --entrypoint=/bin/bash
```

Or using Docker directly:

```bash
docker run -it --platform linux/amd64 --entrypoint=/bin/bash -v "$(pwd)":/flywheel/v0 <docker-image>
```

> **Apple Silicon (M1/M2/M3)**: The `--platform linux/amd64` flag is required because Flywheel gear images are amd64-only. Docker emulates via Rosetta/QEMU.

## Container Mount Mapping

`flyw gear run` mounts **individual files and subdirectories**, NOT the whole directory:

```
-v <pulled-dir>/config.json    → /flywheel/v0/config.json
-v <pulled-dir>/manifest.json  → /flywheel/v0/manifest.json
-v <pulled-dir>/input/         → /flywheel/v0/input/
-v <pulled-dir>/output/        → /flywheel/v0/output/
-v <pulled-dir>/work/          → /flywheel/v0/work/
```

This means gear code baked into the image at `/flywheel/v0/` (e.g. `run.py`, `fw_gear_<name>/`) is **preserved** — it is not shadowed by the mount. The gear code is visible and breakpointable from VSCode after attaching to the container.

The equivalent Docker command (for reference or manual use):

```bash
docker run -it --platform linux/amd64 \
  -u 0:0 \
  -v "$(pwd)/config.json":/flywheel/v0/config.json \
  -v "$(pwd)/manifest.json":/flywheel/v0/manifest.json \
  -v "$(pwd)/input":/flywheel/v0/input \
  -v "$(pwd)/output":/flywheel/v0/output \
  -v "$(pwd)/work":/flywheel/v0/work \
  --entrypoint=/bin/bash \
  <docker-image>
```

## config.json Schema

After pulling a job and re-adding the API key:

```json
{
  "config": {
    "debug": false,
    "my_string_opt": "some value",
    "my_bool_opt": true
  },
  "inputs": {
    "api-key": {
      "key": "instance.example.com:API_KEY_VALUE"
    },
    "my-input-file": {
      "hierarchy": {
        "id": "63a3718141edd378ce32a7ac",
        "type": "project"
      },
      "object": {
        "type": "source code",
        "mimetype": "application/json",
        "size": 12345,
        "file_id": "6997c78d4c791102c56d6859"
      },
      "location": {
        "path": "/flywheel/v0/input/my-input-file/filename.json",
        "name": "filename.json"
      },
      "base": "file"
    }
  },
  "destination": {
    "type": "analysis",
    "id": "69cd7d58e9d2bc7bedb5e099"
  },
  "job": {
    "id": "69cd7d58e9d2bc7bedb5e09b"
  }
}
```

### Key Paths for Programmatic Access

- **API key**: `config["inputs"]["api-key"]["key"]`
- **Config values**: `config["config"]["<option_name>"]`
- **Input file path**: `config["inputs"]["<input-name>"]["location"]["path"]`
- **Input file name**: `config["inputs"]["<input-name>"]["location"]["name"]`
- **Destination ID**: `config["destination"]["id"]` (usually an analysis; get its `.parent` for the project)

## Debugging Inside the Container

```bash
# Run the gear normally
python run.py

# Run with pdb
python -m pdb run.py

# Find where gear code is installed
python -c "import my_gear; print(my_gear.__file__)"
```

Gear Python code is installed in the container's virtualenv, typically under `/venv/lib/python/site-packages/`.

## VSCode Debugging with dev.py

For interactive VSCode debugging with breakpoints:

1. **Create a `dev.py`** in the pulled job directory that bypasses `GearContext` and calls the gear's main `run()` function directly. `GearContext` wraps config parsing and SDK client setup — `dev.py` does the same thing from `config.json` so you can control and inspect every step.

2. **Launch the container with bash**:
   ```bash
   flyw gear run . -- --entrypoint=/bin/bash
   ```

3. **Attach VSCode** to the running container (Remote - Containers extension -> "Attach to Running Container").

4. **Run `/flywheel/v0/dev.py`** from VSCode's Run/Debug panel with breakpoints set in the gear code.

### dev.py Template

Adapt the `run()` call at the bottom to match the gear's main entry point signature.

```python
"""Dev script for local debugging inside a pulled gear container.

Place in the pulled job directory alongside config.json.
Run from /flywheel/v0/dev.py inside the container.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Container paths
FLYWHEEL_DIR = Path("/flywheel/v0")
CONFIG_PATH = FLYWHEEL_DIR / "config.json"
OUTPUT_DIR = FLYWHEEL_DIR / "output"
WORK_DIR = FLYWHEEL_DIR / "work"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def load_config():
    """Load config.json."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_api_key(config):
    """Get API key from config, fall back to env var if redacted."""
    key = config.get("inputs", {}).get("api-key", {}).get("key", "")
    if key and "REDACTED" not in key.upper():
        return key
    # Fallback to env var
    key = os.environ.get("FW_API_KEY", "") or os.environ.get("API_KEY", "")
    if not key:
        raise RuntimeError(
            "API key is redacted and no env var found. "
            "Run: flyw gear config -i api_key=$MY_API_KEY"
        )
    return key


def get_input_path(config, input_name):
    """Get the container path for a named input file. Returns None if not present."""
    inp = config.get("inputs", {}).get(input_name)
    if not inp:
        return None
    path_str = inp.get("location", {}).get("path")
    return Path(path_str) if path_str else None


def get_project_id(config, api_key):
    """Resolve project ID from the destination analysis."""
    import flywheel

    dest_id = config["destination"]["id"]
    fw = flywheel.Client(api_key)
    analysis = fw.get(dest_id)
    if hasattr(analysis, "parent") and analysis.parent.type == "project":
        return analysis.parent.id
    raise RuntimeError(f"Could not resolve project from destination {dest_id}")


def main():
    config = load_config()
    gear_config = config.get("config", {})
    api_key = get_api_key(config)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # ----- Adapt below to your gear's run() signature -----
    # from my_gear.main import run
    # e_code = run(
    #     api_key=api_key,
    #     project_id=get_project_id(config, api_key),
    #     work_dir=WORK_DIR,
    #     output_dir=OUTPUT_DIR,
    #     data_model_path=get_input_path(config, "data model"),
    #     version_label=gear_config.get("version_label"),
    # )
    # sys.exit(e_code)
    pass


if __name__ == "__main__":
    main()
```

### Key Points

- **API key handling**: `flyw job pull` redacts the API key. Either re-inject with `flyw gear config -i api_key=...` before launching, or pass via env var: `-- -e FW_API_KEY=$MY_API_KEY`.
- **Project ID**: Most gears resolve the project from the destination analysis. The destination in `config.json` is an analysis ID — call `fw.get(dest_id).parent` to get the project.
- **Breakpoints**: Set breakpoints anywhere in the gear's installed Python packages (typically `/venv/lib/python/site-packages/`).
- **Gear code location**: `python -c "import my_gear; print(my_gear.__file__)"` inside the container.

## Generate a HOW_TO.md

When setting up a pulled job for debugging, **always create a `HOW_TO.md`** file in the pulled job directory. This gives the user copy-pasteable commands to re-launch the debug session.

Read the docker image from `manifest.json` at `custom.gear-builder.image`. Read the job ID from `config.json` at `job.id`.

### HOW_TO.md Template

Generate with actual values filled in:

````markdown
# Debug Setup for <gear-name> <gear-version>

Job ID: `<job-id>`
Image:  `<docker-image>`

## Run the gear (normal)

```bash
bash run.sh
```

## Launch container interactively

```bash
flyw gear run . -- --entrypoint=/bin/bash
```

> **Apple Silicon (M1/M2/M3)**: `--platform linux/amd64` is applied automatically by flyw.

Or directly with Docker:

```bash
docker run -it --platform linux/amd64 --entrypoint=/bin/bash -v "$(pwd)":/flywheel/v0 <docker-image>
```

## Inside the container

```bash
# Run the gear normally
python run.py

# Run with pdb
python -m pdb run.py

# Find where gear code is installed
python -c "import <gear_python_package>; print(<gear_python_package>.__file__)"
```

## VSCode attach

1. Launch the container: `flyw gear run . -- --entrypoint=/bin/bash`
2. In VSCode: Remote-Containers → "Attach to Running Container"
3. Open `/flywheel/v0/run.py` and run with debugger (F5)
4. Set breakpoints in gear code (see path from import check above)
````

### How to Populate the Template

- **`<docker-image>`**: `manifest.json` -> `custom.gear-builder.image`
- **`<gear-name>`** and **`<gear-version>`**: `manifest.json` -> `name` and `version`
- **`<job-id>`**: `config.json` -> `job.id`
- **`<gear_python_package>`**: Replace hyphens with underscores in gear name (e.g., `fw-parquet-etl` -> `fw_parquet_etl`). If `run.py` is available, read the actual import name from it.

## Implicit Container Arguments

- `flyw gear run` passes `-u 0:0` automatically (runs as root) for local dev
- `--platform=linux/amd64` — Flywheel only supports amd64
- `--provenance=False` (Docker only) — avoids OCI Image Index issues
- `--format=docker` (Podman only)
