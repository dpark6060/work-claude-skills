---
type: CLI Reference
title: Gear Management
description: flyw gear commands for listing, uploading, exporting, installing, updating, and permissioning gears on a Flywheel site.
tags: [flyw, cli, gear, management]
timestamp: 2026-07-15T00:00:00Z
---

# Gear Management

Commands for listing, uploading, exporting, installing, updating, and permissioning gears on a Flywheel site.

## Contents
- [`gear ls`](#gear-ls) — List installed gears
- [`gear upload`](#gear-upload) — Build + upload to Flywheel (gear categories)
- [`gear export`](#gear-export) — Export between sites or download locally
- [`gear install`](#gear-install) — Install from gear exchange
- [`gear update`](#gear-update) — Update from gear exchange
- [`gear permission`](#gear-permission) — Manage access control (permissions model)
- [`gear --enable` / `gear --disable`](#gear---enable--gear---disable)
- [`gear --validate`](#gear---validate)

## `gear ls` — List Installed Gears

```bash
flyw gear ls                                          # List all (latest enabled)
flyw gear ls test                                     # Simple name filter
flyw gear ls -f gear.name=test -a                     # All versions of "test"
flyw gear ls -f gear.name=test -a -d                  # Include disabled versions
flyw gear ls -f created>2024-10-01                    # By upload date
flyw gear ls -f 'created>2024-10-01,gear.name=test'   # Combined filters
flyw gear ls -o json                                  # JSON output
```

### Options

| Option | Description |
|---|---|
| `FILTER` | Simple name filter (equivalent to `-f gear.name=~<value>`) |
| `-f, --filter EXPR` | Full filter expression |
| `-l, --limit N` | Number of gears to return |
| `-a, --all-versions` | Return all gear versions |
| `-d, --disabled` | Include disabled gears |
| `-o, --output OUTPUT` | Output format (e.g. `json`) |

### Gotcha: the default list is truncated

`gear ls` applies a default result limit even with a name filter. To see every version of a gear
(including disabled and old `-rc` builds), pass `-a -d` **and** a generous `-l`. Verify the count
before claiming a version does not exist.

```bash
flyw gear ls -f gear.name=session-splitter -a -d -l 100
```

## `gear upload` — Build + Upload to Flywheel

Builds, tags, pushes to instance registry, and registers the gear:

```bash
flyw gear upload                      # Upload from current dir
flyw gear upload /path/to/gear        # Specify directory
flyw gear upload -c analysis          # Override category
flyw --no-interactive --assume-yes gear upload .   # Unattended (scripts, agents)
```

### Options

| Option | Description |
|---|---|
| `PATH` | Directory containing gear [default: PWD] |
| `-c, --category CATEGORY` | Override manifest category |

### Gotchas (confirmed 2026-09, CLI 0.36.1)

- **Platform**: `flyw gear build` / `gear upload` already build `linux/amd64` on Apple Silicon.
  No `docker buildx build --platform linux/amd64 --load` step is needed.
- **Docker must be running**: `docker info` failing means Docker Desktop is stopped; `open -a Docker`
  and wait for the daemon. The first `gear upload` right after daemon start can fail at the tag step
  with `No such image: flywheel/<gear>:<ver>`; just rerun it.
- **Slow uplink**: the push step fails with `net/http: timeout awaiting response headers` on a
  single layer. Retry the push directly; already-accepted layers are skipped, so each retry gets
  further. When it succeeds, rerun `gear upload` to do the (now instant) registration step.

  ```bash
  until docker push <host>/<gear>:<ver>; do sleep 5; done
  flyw --profile <p> --no-interactive --assume-yes gear upload .
  ```
- **Push succeeded but gear not registered** is a valid intermediate state. `gear ls` shows nothing
  until the `gear upload` registration step completes.

### Gear Categories

- **`analysis`** — runs in immutable analysis containers, produces analysis results
- **`utility`** — general utility function on parent container
- **`converter`** — converts input to different format
- **`classifier`** — applies classification to input data
- **`qa`** — applies quality measures to input

## `gear export` — Export Between Sites or Download

```bash
# Export to another site
flyw --profile source gear export -d target my-gear

# Export specific version
flyw gear export my-gear:0.4.1

# Export by ID
flyw gear export 619542005c0c1baeeb68981a

# Export multiple gears at once
flyw gear export gear-1 gear-2:0.1.2 619542005c0c1baeeb68981a

# Download to local directory
flyw gear export -p /tmp/gears my-gear

# Show all versions to choose from
flyw --profile source gear export -a my-gear -d target
```

### Options

| Option | Description |
|---|---|
| `GEAR...` | List of gears by ID, name, or name:version [required] |
| `-d, --destination PROFILE` | Destination site profile |
| `-a, --all-versions` | Show all versions for selection |
| `-p, --path PATH` | Directory to download gears into |

Must be logged into both source and destination sites. Source via `--profile`, destination via `-d`.

## `gear install` — Install from Gear Exchange

```bash
flyw gear install -n my-gear                    # Latest version
flyw gear install -n my-gear -v 1.2.0           # Specific version
flyw gear install -n my-gear -c analysis --yes  # Override category, skip confirm
```

### Options

| Option | Description |
|---|---|
| `-n, --name NAME` | Gear name [required] |
| `-v, --gear-version VERSION` | Version to install [default: latest] |
| `-c, --category CATEGORY` | Override manifest category |
| `--yes` | Skip confirmation prompt |

Private gears require Docker registry login for the image host.

## `gear update` — Update from Gear Exchange

```bash
flyw gear update my-gear              # Update specific gear
flyw gear update --all                # Update all installed gears
flyw gear update my-gear --yes        # Skip confirmation
```

### Options

| Option | Description |
|---|---|
| `GEAR` | Gear name (optional if --all) |
| `--all` | Update all gears to latest |
| `--yes` | Skip confirmation |

## `gear permission` — Manage Access Control

By default, gears are accessible to all users and projects. Adding a user or project to permissions **excludes everyone else not listed**.

### View permissions
```bash
flyw gear permission my-gear
```

### Add permissions
```bash
flyw gear permission -a -u user@example.com my-gear
flyw gear permission -a -p fw://group/project my-gear
flyw gear permission -a -p <project-id> my-gear
```

### Remove permissions
```bash
flyw gear permission -d -u user@example.com my-gear
flyw gear permission -d -p fw://group/project my-gear
```

### Reset to default (all users/projects)
```bash
flyw gear permission -r my-gear
```

### Options

| Option | Description |
|---|---|
| `GEAR` | Gear name [required] |
| `-a, --add` | Add permissions |
| `-d, --delete` | Remove permissions |
| `-r, --reset` | Reset to default (accessible to all) |
| `-p, --project ID` | Project ID or FW path |
| `-u, --user ID` | User email |

### Permissions Model

Permissions operate as a **union** of user and project lists:
- **User permission** — user can access the gear in **any** project
- **Project permission** — **all** users can access the gear in that project
- Adding a user excludes all other users not in the list (same for projects)

## `gear --enable` / `gear --disable`

```bash
flyw gear --enable my-gear            # By name (latest)
flyw gear --enable my-gear:0.1.0      # By name + version
flyw gear --enable <gear-id>          # By ID
flyw gear --disable my-gear
```

Disabled gears reserve their name+version — you cannot upload a new gear with the same combination.

## `gear --validate`

Validate a gear manifest without building:
```bash
flyw gear --validate /path/to/manifest.json
```
