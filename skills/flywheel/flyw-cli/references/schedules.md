---
type: CLI Reference
title: Import & Export Schedules
description: flyw import/export schedule commands for running imports and exports once at a future time or periodically via cron.
tags: [flyw, cli, schedules, cron]
timestamp: 2026-07-15T00:00:00Z
---

# Import & Export Schedules

Both import and export support scheduling — run once at a future time or periodically via cron.

## `import schedule create`

Creates a scheduled import. Accepts all the same rule/behavior options as `import run`, plus scheduling options.

```bash
# Run once at a specific time
flyw import schedule create \
    --project fw://group/Project \
    --storage <STORAGE_ID> \
    --mapping 'path={subject.label}/{session.label}/{acquisition.label}/*' \
    --start "2024-12-31T00:00:00+00:00"

# Run every Sunday at midnight UTC
flyw import schedule create \
    --project fw://group/Project \
    --storage <STORAGE_ID> \
    --mapping 'path={subject.label}/{session.label}/{acquisition.label}/*' \
    --cron "0 0 * * 0"

# Run every Sunday starting after a specific date
flyw import schedule create ... \
    --cron "0 0 * * 0" --start "2024-06-01T00:00:00+00:00"

# Run every Sunday until an end date
flyw import schedule create ... \
    --cron "0 0 * * 0" --end "2025-12-31T00:00:00+00:00"
```

## `export schedule create`

Same pattern as import — accepts all `export run` options plus scheduling:

```bash
flyw export schedule create \
    --project fw://group/Project \
    --storage <STORAGE_ID> \
    --include type=dicom \
    --cron "0 0 * * 0"
```

## Scheduling Options

| Option | Description |
|---|---|
| `--cron EXPR` | Cron expression (always UTC) |
| `--start DATE` | Start time (timezone-aware) — run once or enable cron at this time |
| `--end DATE` | End time (timezone-aware) — disable cron at this time |

### Cron Syntax

Standard 5-field cron format (minute, hour, day-of-month, month, day-of-week):

| Example | Meaning |
|---|---|
| `"0 0 * * 0"` | Every Sunday at 00:00 UTC |
| `"0 0 * * *"` | Every day at midnight UTC |
| `"0 */6 * * *"` | Every 6 hours |
| `"30 2 1 * *"` | 1st of every month at 02:30 UTC |

**Important:** `--cron` always assumes **UTC**. `--start`/`--end` are timezone-aware.

### Date Formats

| Format | Interpretation |
|---|---|
| `"2024-12-31 00:00"` | Local timezone |
| `"2024-12-31T00:00:00+00:00"` | Explicit UTC |
| `"2024-12-31T00:00:00-05:00"` | Explicit US Eastern |

## Managing Schedules

### Get schedule details
```bash
flyw import schedule get <SCHEDULE_ID>
flyw export schedule get <SCHEDULE_ID>
```

### List schedules
```bash
flyw import schedule list
flyw import schedule list --filter <expr>
flyw import schedule list --all              # Include previous runs

flyw export schedule list
flyw export schedule list --filter <expr>
flyw export schedule list --all
```

### Update schedule timing
```bash
flyw import schedule update <SCHEDULE_ID> --cron "0 0 * * 1"
flyw import schedule update <SCHEDULE_ID> --start "2025-01-01T00:00:00+00:00"
flyw import schedule update <SCHEDULE_ID> --end "2025-12-31T00:00:00+00:00"

flyw export schedule update <SCHEDULE_ID> --cron "0 0 * * 1"
```

### Cancel a schedule
```bash
flyw import schedule cancel <SCHEDULE_ID>
flyw export schedule cancel <SCHEDULE_ID>
```

## Common Options on All Schedule Commands

| Option | Description |
|---|---|
| `-o, --output OUTPUT` | Output format |
| `--filter EXPR` | Filter (list only) |
| `--after-id ID` | Pagination token (list only) |
| `--limit INT` | Page limit (list only) |
| `--all / --no-all` | Include previous runs (list only) |
