---
type: CLI Reference
title: Authentication & Profiles
description: flyw auth login/status/logout commands and profile management for switching between multiple Flywheel instances without re-authenticating.
tags: [flyw, cli, auth, profiles]
timestamp: 2026-07-15T00:00:00Z
---

# Authentication & Profiles

## `auth login`

Most commands require authentication. Generate an API key from the Flywheel UI Profile page, then:

```bash
flyw auth login
# Enter API key when prompted (format: site.flywheel.io:4PIk3ywQZ9REx4mp13)
```

### Automation (non-interactive)

Set the `FW_CLI_API_KEY` environment variable to skip the interactive prompt:

```bash
FW_CLI_API_KEY=site.flywheel.io:4PIk3ywQZ9REx4mp13 flyw auth login
```

## `auth status`

```bash
flyw auth status              # Show login status for current profile
flyw auth status --all        # Show all saved profiles
```

## `auth logout`

```bash
flyw auth logout              # Remove current profile credentials
```

Credentials are stored in `~/.fw/config.yml`. Exiting the shell does NOT log you out.

## Profiles

**Profiles are the most commonly used CLI feature.** They allow switching between multiple Flywheel instances without re-authenticating.

### Creating Profiles

```bash
# Log in to production (stored as "prod" profile)
flyw --profile prod auth login

# Log in to staging (stored as "staging" profile)
flyw --profile staging auth login

# Log in with default profile (no --profile flag)
flyw auth login
```

### Using Profiles

The `--profile` flag (or `FW_CLI_PROFILE` env var) must be specified on **every command** — it is not sticky between calls:

```bash
# List gears on prod
flyw --profile prod gear ls

# List jobs on staging
flyw --profile staging job ls

# Import using the default profile
flyw import list

# Using environment variable
FW_CLI_PROFILE=prod flyw gear ls
```

### Profile Strategy

A common pattern is to use the `default` profile for your primary site and named profiles for secondary sites:

```bash
# Primary site — no --profile needed
flyw auth login
flyw gear ls

# Secondary sites — always specify --profile
flyw --profile staging auth login
flyw --profile staging gear ls
```

### Where Profiles Are Stored

Profiles and their credentials are persisted in `~/.fw/config.yml`. You can change the config directory:

```bash
export FW_CLI_CONFIG_DIR=/custom/path
```
