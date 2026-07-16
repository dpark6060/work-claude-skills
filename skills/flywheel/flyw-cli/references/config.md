---
type: CLI Reference
title: CLI Configuration
description: flyw config commands, the configuration source priority order, and the full catalog of CLI configuration options.
tags: [flyw, cli, config]
timestamp: 2026-07-15T00:00:00Z
---

# CLI Configuration

## Configuration Sources (priority order)

1. **Command-line arguments** — e.g. `--connect-timeout 30`
2. **Environment variables** — e.g. `export FW_CLI_CONNECT_TIMEOUT=30`
3. **`.env` file** — in current working directory, auto-loaded
4. **Config file** — `~/.fw/config.yml`
5. **Defaults** — built-in values

## Config Commands

```bash
flyw config set connect_timeout 30     # Set a value
flyw config get connect_timeout        # Get current value
flyw config list                       # Show all settings with sources
flyw config unset connect_timeout      # Remove, revert to default
```

### Config List Output

The **Source** column shows where each value comes from:
- `env (...)` — environment variable
- `.env` — .env file in PWD
- `yaml` — `~/.fw/config.yml`
- `default` — built-in default

## CLI Argument Overrides

| Config Option | CLI Argument |
|---|---|
| `default_profile` | `--profile NAME` |
| `container_client` | `--container-client (docker\|podman)` |
| `connect_timeout` | `--connect-timeout SEC` |
| `read_timeout` | `--read-timeout SEC` |
| `ssl_verify` | `--ssl-verify PATH` |
| `debug` | `--debug` |

## All Configuration Options

### Connection Settings

| Option | Default | Description |
|---|---|---|
| `connect_timeout` | 10 | HTTP connection timeout in seconds |
| `read_timeout` | 30 | HTTP read timeout in seconds |
| `ssl_verify` | yes | `yes`, `no`, or path to CA cert bundle |

### Performance Settings

| Option | Default | Description |
|---|---|---|
| `concurrent_file_uploads` | 8 | Files to upload concurrently |
| `concurrent_chunk_uploads` | 4 | Chunks per file uploaded concurrently |
| `concurrent_file_downloads` | 8 | Files to download concurrently |
| `retry_backoff_factor` | 0.1 | Exponential backoff factor |
| `retry_total` | 3 | Total retry attempts |

### Logging & UI Settings

| Option | Default | Description |
|---|---|---|
| `debug` | false | Enable verbose debug logging |
| `logs_retained` | 50 | Number of log files to keep |
| `live_refresh_interval` | 1.0 | Progress update interval (seconds) |
| `container_client` | docker | `docker` or `podman` |

### Feature Flags

| Option | Default | Description |
|---|---|---|
| `disable_compatibility_check` | false | Skip version compatibility checks |
| `disable_auto_update` | false | Disable automatic CLI updates |

## Boolean Values

For boolean settings, accepted values:
- **True**: `true`, `yes`, `1`, `on`
- **False**: `false`, `no`, `0`, `off`

## Environment Variables

All config options can be set via `FW_CLI_<UPPERCASE_OPTION>`:

```bash
export FW_CLI_CONCURRENT_FILE_UPLOADS=16
export FW_CLI_DEBUG=true
export FW_CLI_CONNECT_TIMEOUT=30
```

## .env File

Create a `.env` file in your working directory — the CLI auto-loads it:

```bash
# .env
FW_CLI_CONCURRENT_FILE_UPLOADS=16
FW_CLI_CONCURRENT_CHUNK_UPLOADS=8
FW_CLI_DEBUG=true
```

## Common Recipes

### High-performance upload
```bash
flyw config set concurrent_file_uploads 16
flyw config set concurrent_chunk_uploads 8
flyw config set read_timeout 120
```

### Debug connection issues
```bash
flyw config set debug true
flyw config set connect_timeout 30
flyw config set read_timeout 60
flyw config set ssl_verify /path/to/ca-bundle.crt
```

## Config File Location

Default: `~/.fw/config.yml`. Override with:
```bash
export FW_CLI_CONFIG_DIR=/custom/path
```
