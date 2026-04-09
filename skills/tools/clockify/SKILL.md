---
name: clockify
description: Interact with the Clockify time-tracking API using the ClockifySdk Python library
version: 2026-04-07
tags:
  - python
  - clockify
  - time-tracking
  - api
---

# Clockify SDK

## Overview

`ClockifySdk` is a Python wrapper around the Clockify REST API v1. It handles
authentication, pagination, and date encoding automatically, and exposes typed
data models for all core resources.

**Source repo:** `/Users/davidparker/Documents/Flywheel/Code/clockify/ClockifySdk`

## Installation / Import

The SDK is a local module. Import directly:

```python
from ClockifySdk.clockify_sdk import Clockify
from ClockifySdk.Models.time_entry import TimeEntryInput, TimeEntryOutput
from ClockifySdk.Models.project_entry import ProjectEntry
from ClockifySdk.Models.workspace_entry import WorkspaceEntry
from ClockifySdk import clockify_utils
```

## MCP Tools (preferred)

This skill has a companion MCP server with embedded Flywheel workflow
instructions. When registered, use these tools directly instead of Python scripts.
See `server/README.md` for setup.

### Lookup

| Tool | Purpose |
|---|---|
| `get_clients(use_cache)` | All clients as `{name: id}`. Cached by default. |
| `refresh_client_cache()` | Force re-fetch clients and overwrite cache. |
| `get_projects(client_id)` | Projects, optionally filtered by client. |
| `get_tasks(project_id)` | Tasks for a project. |
| `get_tags()` | All tags in the workspace. |
| `get_current_user()` | Authenticated user profile. |
| `get_workspace_users()` | All users in the workspace. |

### Time entries

| Tool | Purpose |
|---|---|
| `log_time(desc, project_id, task_id, minutes, billable, tag_ids)` | Entry ending now, by duration. |
| `log_time_range(desc, project_id, task_id, start, end, billable, tag_ids)` | Entry with explicit start/end. |
| `get_time_entries(days_back, start, end, description, project_id)` | Query entries with flexible filters. |
| `update_time_entry(entry_id, ...)` | Modify an existing entry. |
| `delete_time_entry(entry_id)` | Delete an entry by ID. |

All write tools (`log_time`, `log_time_range`, `update_time_entry`, `delete_time_entry`)
embed "confirm with user first" instructions in their docstrings.

## Scripts

Reusable helper scripts live at `/Users/davidparker/.claude/skills/clockify/scripts/`.
Call them via Bash: `python3 /Users/davidparker/.claude/skills/clockify/scripts/<name>.py [args]`

All scripts require `CLOCKIFY_API` in the environment and default to `--tz-offset -5` (CDT).

| Script | Purpose | When to use |
|---|---|---|
| `get_day_entries.py` | Fetch all entries for a calendar day, sorted by start | Anytime you need to see what's already on a day |
| `add_jitter.py` | Apply scaled independent jitter to start and end | When the user gives an approximate duration (`~1hr`, `~30min`) |
| `check_overlap.py` | Detect overlap with existing entries and resolve interactively | **Always run before posting any new entry** |
| `find_gaps.py` | Find free time slots ≥ N minutes on a given day | When looking for where to fit an entry |
| `parse_time_spec.py` | Convert fuzzy time phrases to UTC ISO datetime | When the user gives a non-exact time (`"yesterday afternoon"`, `"2pm CDT"`) |

### Mandatory workflow rules

1. **Always call `parse_time_spec.py`** when the user specifies a time loosely (e.g. "yesterday around 3", "this morning", "~2pm CDT"). Feed the returned `utc_iso` into subsequent scripts.
2. **Always call `check_overlap.py`** with the proposed start/end before posting. Use its returned `start`/`end` for the actual entry.
3. **Call `add_jitter.py`** when the user prefixes a duration with `~` (tilde). Jitter both start and end independently; magnitude scales with duration. Show the jittered times in the confirmation summary.

### Script reference

```
get_day_entries.py  --date YYYY-MM-DD  --tz-offset N
add_jitter.py       --start ISO  --end ISO
check_overlap.py    --start ISO  --end ISO  --tz-offset N
find_gaps.py        --date YYYY-MM-DD  --min-duration-min N  --tz-offset N
parse_time_spec.py  --spec "TEXT"  --tz-offset N
```

---

## Fallback: Direct SDK

If the MCP is not available, the SDK can be called via Bash. See the reference files
for patterns. Note: `start`/`end` must be `datetime` objects — see Critical Gotcha below.

## Initialization

```python
cl = Clockify(api_key="your_key")
```

On init, the SDK fetches the current user and stores:
- `cl.userId` — current user's ID
- `cl.default_workspace` — user's default workspace ID
- `cl.current_workspace` — `None` until explicitly set
- `cl.workspaceId` (property) — returns `current_workspace` if set, else `default_workspace`

## Guide Index

Load the relevant reference based on your task:

- **[api-reference.md](references/api-reference.md)** — All `Clockify` class methods,
  endpoints, parameters, and return types. Start here when you need to know what calls exist.
- **[endpoints.md](references/endpoints.md)** — Complete Clockify API v1 endpoint map
  (all endpoints, not just SDK-wrapped ones). Use with `cl.client.make_call()` for
  anything the SDK doesn't cover directly. Includes auth, pagination, rate limits.
- **[models.md](references/models.md)** — All dataclass/model definitions: `TimeEntryInput`,
  `TimeEntryOutput`, `ProjectEntry`, `WorkspaceEntry`, `TimeInterval`, `Rate`, `Membership`.
  Includes cross-checks against real API response shapes.
- **[patterns.md](references/patterns.md)** — Common task patterns: filtering entries,
  creating entries from tasks, working with projects, multi-workspace, repeating events.
- **[utils.md](references/utils.md)** — Date/time encoding helpers, range checks,
  repeating event day decoding.
- **[flywheel-workflow.md](references/flywheel-workflow.md)** — Flywheel-specific workflow
  for logging time from a Jira ticket: resolving customer → project → task in Clockify.

## Guide Selection Strategy

**Making API calls with SDK methods?** Load api-reference.md.

**Need an endpoint not in the SDK?** Load endpoints.md, then use `cl.client.make_call()`.

**Working with returned data or constructing inputs?** Load models.md.

**Not sure how to accomplish a task?** Load patterns.md.

**Handling dates or repeating events?** Load utils.md.

**Logging time for a Flywheel Jira ticket?** Load flywheel-workflow.md.

## Key Concepts

- Auth uses the `x-api-key` header — set the API key via `CLOCKIFY_API` env var
- The `Clockify` class is the only entry point you need; `ClockifyClient` is internal
- `get_workspace_time_entries()` auto-paginates by default — omit `page` to get all results
- Dates are always ISO 8601: `"YYYY-MM-DDTHH:MM:SSZ"` — use `clockify_utils` to encode/decode
- `current_workspace` must be set before calling workspace-scoped endpoints if you want
  to target a non-default workspace
- `get_flywheel_workspace()` is a convenience shortcut that sets `current_workspace` to
  the workspace named "Flywheel"
- Rate limit: 50 requests/second — HTTP 429 when exceeded
- Pagination: `page` (1-indexed) + `page-size`; response header `Last-Page: true` signals end
- The Reports API uses a different base URL (`https://reports.api.clockify.me/v1`) — the
  SDK client cannot reach it directly; use `requests` with the same API key header

## Critical Gotcha: TimeEntryInput dates must be `datetime` objects

`TimeEntryInput.to_dict()` calls `clockify_utils.encode_clockify_datestr()` on `start`
and `end` internally. That function calls `.strftime()`, so it requires a `datetime`
object — **not a string**. Always pass naive UTC `datetime` objects:

```python
from datetime import datetime, timedelta, timezone

end_dt = datetime.now(timezone.utc).replace(tzinfo=None)   # naive UTC
start_dt = end_dt - timedelta(hours=1, minutes=30)

entry = TimeEntryInput({
    "start": start_dt,   # datetime object, NOT a string
    "end": end_dt,
    ...
})
```

## Code Quality Standards

All Clockify code you write should:
1. Read the API key from environment (`os.environ["CLOCKIFY_API"]`), never hardcode it
2. Set `current_workspace` explicitly before making workspace-scoped calls
3. Use `clockify_utils` for all date encoding/decoding — never hand-format ISO strings
4. Prefer typed model objects (`TimeEntryInput`, `ProjectEntry`) over raw dicts when
   writing or manipulating data
5. Let `get_workspace_time_entries()` auto-paginate — only pass `page` when fetching
   a specific page intentionally
6. Follow project coding conventions (`rules/general_coding/`)
