---
name: flyw-cli
description: Reference for the Flywheel CLI (flyw). Use when constructing or running CLI commands, writing shell scripts that invoke the CLI, or debugging CLI usage. Use even when the user doesn't mention "flyw" directly — if they're asking how to perform a Flywheel operation from the command line or in a shell script, this skill applies. Triggers on "flyw", "flywheel cli", "flywheel command line", "cli command". MANDATORY TRIGGERS: flyw, flywheel cli, flywheel command line, import from S3, import from cloud storage, export data, export to cloud, run a gear, batch run, build a gear, upload a gear, install a gear, pull job, gear job, list jobs, retry job, import status, check import, schedule import, schedule export, auth login, switch sites, storage credentials, storage connection, browse flywheel files
version: 2.0.0
allowed-tools: [Read, Bash]
---

You are using the Flywheel CLI (`flyw`).

## Overview

The Flywheel CLI manages data and site configuration on the Flywheel Biomedical Research Data Platform. It handles authentication, data browsing, gear development/management, job control, data import/export with external cloud storage, and admin operations.

## Command Tree

```
flyw
├── auth                          Authentication
│   ├── login                     Log in with API key
│   ├── status [--all]            Check login status / list profiles
│   └── logout                    Remove stored credentials
├── config                        CLI configuration
│   ├── list                      Show all settings with sources
│   ├── get KEY                   Get a setting value
│   ├── set KEY VALUE             Set a setting value
│   └── unset KEY                 Remove a setting (revert to default)
├── ls [PATH] [-a]                List containers/files at path
├── update [VERSION]              Update the CLI itself
├── gear                          Gear development & management
│   ├── create                    Scaffold new gear from template
│   ├── build                     Build gear container image
│   ├── config                    Build config.json for local run
│   ├── run                       Run gear locally in container
│   ├── version                   Show/bump gear version
│   ├── upload                    Build + push to Flywheel
│   ├── ls                        List installed gears
│   ├── export                    Export gear to site or local
│   ├── install                   Install from gear exchange
│   ├── update                    Update from gear exchange
│   └── permission                Show/modify gear permissions
├── job                           Job control
│   ├── ls                        List jobs
│   ├── run                       Run job on site
│   ├── pull                      Pull job for local debugging
│   ├── retry                     Retry a failed job
│   └── batch run                 Run gear across containers
├── import                        Import from external storage
│   ├── run / test / get / list / cancel / rerun
│   ├── schedule create/get/list/update/cancel
│   └── rule-set create/get/list/update/archive/restore
├── export                        Export to external storage
│   ├── run / get / list / cancel / rerun
│   ├── schedule create/get/list/update/cancel
│   └── rule-set create/get/list/update/archive/restore
├── admin
│   └── storage create/get/list/update/delete
└── utils
    ├── collect-logs              Collect logs tarball for support
    └── deid                      Test de-identification
```

## Global Options

These apply to **every** command:

| Option | Description |
|---|---|
| **`-P, --profile NAME`** | **Login profile to use — most commonly used global option** |
| `-C, --container-client (docker\|podman)` | Container client for gear commands [default: docker] |
| `--connect-timeout SEC` | HTTP connect timeout [default: 10] |
| `--read-timeout SEC` | HTTP read timeout [default: 30] |
| `--ssl-verify PATH` | SSL CA cert path, or `no` to disable [default: yes] |
| `-D, --debug` | Enable verbose debug logging |
| `--collect-logs DIR` | Collect logs to tarball for support |

## Authentication: Use `--profile`, Not `auth login`

**Do NOT run `flyw auth login` to switch between sites.** Profiles are already stored from prior logins. Just pass `--profile` on every command:

```bash
flyw --profile prod gear ls
flyw --profile staging import list
flyw --profile dev job ls -g my-gear
```

`--profile` selects which stored credentials to use. It does not require a separate login step. The user has already logged into their profiles — you just need to specify which one.

Only use `flyw auth login` if the user explicitly asks to authenticate a new profile or if a command fails with an auth error.

## Flywheel Path Format

`fw://<group>/<project>/<subject>/<session>/<acquisition>/<file>`

The `fw://` prefix may be omitted. Container IDs can also be used anywhere a path is accepted.

## Critical: Flag Syntax

All options use dashes. **Never omit the dashes.** Common mistakes:

| WRONG | CORRECT |
|---|---|
| `flyw auth login list` | `flyw auth status --all` |
| `flyw auth logout all` | `flyw auth logout` (removes current profile) |
| `flyw gear ls all-versions` | `flyw gear ls --all-versions` |

## Simple Commands

**`ls`** — List containers and files:
```bash
flyw ls                          # List groups
flyw ls fw://group/Project       # List contents
flyw ls --all                    # Site admin view
```

**`update`** — Update the CLI: `flyw update` (stable), `flyw update latest` (dev), `flyw update <tag>`

**`utils deid`** — Test de-identification locally:
```bash
flyw utils deid file.DCM --project fw://group/Project
flyw utils deid file.DCM --deid-profile profile.yml --output deidentified.dcm
```

**`utils collect-logs`** — Collect diagnostic logs into a tarball for Flywheel support.

## Guide Index

| Reference File | Covers |
|---|---|
| `references/auth-profiles.md` | Auth login, logout, status, **profiles (heavy)**, API key automation |
| `references/config.md` | All CLI config options, env vars, .env files, config commands |
| `references/gear-development.md` | gear create, build, config, run locally, version |
| `references/gear-management.md` | gear ls, upload, export, install, update, permission |
| `references/job.md` | job ls, run, pull, retry, batch run |
| `references/import.md` | import run/test/get/list/cancel/rerun, rules, filters, mappings, DICOM, rule-sets |
| `references/export.md` | export run/get/list/cancel/rerun, snapshots, rules, filters, paths, rule-sets |
| `references/schedules.md` | import/export schedule create/get/list/update/cancel, cron |
| `references/admin-storage.md` | storage CRUD, cloud URIs, credentials, ref-in-place |

## Guide Selection Strategy

- **Authenticating or switching between Flywheel sites** → `auth-profiles.md`
- **Changing CLI settings (timeouts, concurrency, debug)** → `config.md`
- **Creating, building, or running a gear locally** → `gear-development.md`
- **Listing, uploading, installing, or permissioning gears on a site** → `gear-management.md`
- **Running, listing, retrying, or pulling jobs** → `job.md`
- **Importing data from external cloud storage** → `import.md`
- **Exporting data to external cloud storage** → `export.md`
- **Scheduling recurring imports or exports** → `schedules.md`
- **Registering or managing external storage connections** → `admin-storage.md`
- **Debugging a failed gear job locally** → use the `fw-gear-debugger` skill instead
