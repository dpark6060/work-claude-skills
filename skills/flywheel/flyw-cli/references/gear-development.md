# Gear Development

Local gear development workflow: create → build → config → run → debug → version bump → upload.

## Contents
- [Prerequisites](#prerequisites) — Docker/Podman requirement
- [`gear create`](#gear-create) — Scaffold new gear (templates, base images)
- [`gear build`](#gear-build) — Build container image (env, pass-through args)
- [`gear config`](#gear-config) — Build config.json for local runs
- [`gear run`](#gear-run) — Run gear locally (workflow, directory structure)
- [`gear version`](#gear-version) — Show/bump version
- [Debugging](#debugging) — Pointer to fw-gear-debugger skill

## Prerequisites

Gear commands require **Docker** (default) or **Podman** installed.

```bash
flyw --container-client podman gear build    # Use Podman instead
```

## `gear create` — Scaffold a New Gear

```bash
flyw gear create                      # Interactive in current dir
flyw gear create /path/to/dir         # Specify directory
flyw gear create -n my-gear -l "My Gear" -a "Name <email>"
```

### Options

| Option | Description |
|---|---|
| `-n, --name NAME` | Machine name (lowercase, numbers, hyphens only) |
| `-l, --label LABEL` | Human label (shown in UI, allows spaces) |
| `-a, --author AUTHOR` | `Firstname Lastname <email>` |
| `-i, --image IMAGE` | Base Docker image |
| `-t, --template TEMPLATE` | Gear template (basic or flywheel-poetry) |
| `-c, --category CATEGORY` | Gear category |
| `-d, --description DESC` | Description |
| `-s, --sdk` | Enable Flywheel SDK usage |
| `--sdk-readonly` | SDK in read-only mode (implies --sdk) |
| `--cite CITE` | Citation info |
| `--license LICENSE` | License [default: MIT] |
| `--url URL` | Source URL |

### Templates

- **Basic** — Dockerfile, manifest.json, requirements.txt, run.py
- **Flywheel Poetry** — Full package structure with tests, docs, pre-commit, CI, poetry

### Base Images

- `python:3.8-buster`, `python:3.7-buster` — vanilla Python
- `flywheel/python:main` — includes poetry, vim, jq, yq, curl, git
- `flywheel/python-gdcm:main` — adds GDCM (C++ DICOM library)
- `ubuntu:latest`, `neurodebian:latest` — bare Linux

### Created Structure

```
├── Dockerfile
├── manifest.json
├── requirements.txt
└── run.py
```

## `gear build` — Build Container Image

```bash
flyw gear build                       # Build in current dir
flyw gear build /path/to/gear         # Specify directory
flyw gear build --no-update-env       # Skip environment update
flyw gear build --env-dry-run         # Show what env would be updated
flyw gear build . -- --pull --no-cache  # Pass-through Docker args
```

### Options

| Option | Description |
|---|---|
| `--update-env / --no-update-env` | Update manifest environment from image [default: update] |
| `-i, --env-ignore KEY` | `<key>=[YES/no]` customize ignored env vars |
| `--env-dry-run` | Print env changes without writing to manifest |

### Pass-through Arguments

Anything after `--` is passed directly to `docker build` / `podman build`:
```bash
flyw gear build . -- --pull --no-cache
```

**Do NOT use `--tag / -t`** — it may break other CLI commands (e.g. `gear run`).

### Gear Environment

Flywheel **overrides** Dockerfile environment variables with the manifest `environment` dict. By default, `gear build` populates this dict from the built image. Ignored by default: `TERM`, `HOSTNAME`, `LSCOLORS`, `HOME`.

### Implicit Build Arguments

- `--platform=linux/amd64` — Flywheel only supports amd64
- `--provenance=False` (Docker only) — avoids OCI Image Index issues
- `--format=docker` (Podman only)

## `gear config` — Build config.json for Local Runs

```bash
flyw gear config --new                         # Create from manifest defaults
flyw gear config --show                        # Show all options
flyw gear config -i input-file=/path/to/file   # Add file input
flyw gear config -c debug=true                 # Set config option
flyw gear config -i api_key=$MY_API_KEY        # Set API key
flyw gear config -d fw://group/project         # Set destination
```

### Options

| Option | Description |
|---|---|
| `-n, --new` | Create new config from manifest |
| `-s, --show` | Show all config and input options |
| `-i, --input KEY=VALUE` | Set input (chainable) |
| `-c, --config KEY=VALUE` | Set config value (chainable) |
| `-d, --destination DEST` | Set destination (FW path or ID) |

### Config Types

Types are inferred from manifest:
- boolean: `gear config -c my_bool=true` (accepts True/true/T/t/False/false/F/f)
- string: `gear config -c my_str='my long string'`
- number: `gear config -c my_int=2` or `gear config -c my_float=2.45`
- array: `gear config -c my_array=1,2,3` (split on commas)

### File Inputs

Accepts local paths or Flywheel paths:
```bash
flyw gear config -i input-file=/local/path/to/file.dcm
flyw gear config -i input-file=fw://group/project/sub/ses/acq/file.dcm
```

Flywheel paths download the file and populate metadata in config.json. Mappings stored in `.input_map.json`.

## `gear run` — Run Gear Locally

```bash
flyw gear run                                   # Run in current dir
flyw gear run --prepare                         # Prepare gear directory
flyw gear run /tmp/gear/my-gear_0.1.0           # Run prepared directory
flyw gear run . -- --gpus all                   # Pass-through Docker args
flyw gear run . -- -e MYVAL=example             # Inject env vars
flyw gear run . -- --entrypoint=/bin/bash       # Interactive debugging
```

### Workflow

1. `gear config --new` — create config.json
2. `gear config -i <input>=<path>` — add inputs
3. `gear run --prepare` — creates gear directory structure
4. `gear run /path/to/prepared/dir` — run the gear

### Gear Directory Structure

```
├── config.json
├── manifest.json
├── input/
│   └── <input-name>/
│       └── <file>
├── output/
└── work/
```

### Implicit Run Arguments

`-u 0:0` is automatically passed (runs as root in container) for local dev. Override with: `-- -u <USER>`.

## `gear version` — Show/Bump Version

```bash
flyw gear version                     # Print current version
flyw gear version 1.2.1              # Bump to 1.2.1
flyw gear version 1.2.1 -d /path     # Bump in specific directory
```

## Debugging

For debugging failed gear jobs (pulling jobs, running interactively, VSCode attach, dev.py scripts), use the **`fw-gear-debugger`** skill.
