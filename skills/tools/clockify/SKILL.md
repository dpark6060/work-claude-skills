---
name: clockify
description: >
  Logs, edits, and queries Clockify time entries using the ClockifySdk Python library.
  Use whenever the user wants to track time, add a time entry, log hours, or work with
  the Clockify API — even if they don't say "Clockify" explicitly. MANDATORY TRIGGERS:
  clockify, log time, time entry, track time, log hours, billable hours, time tracking,
  ClockifySdk, time log.
version: 2026-06-11
tags:
  - python
  - clockify
  - time-tracking
  - api
allowed-tools:
  - Bash
---

# Clockify SDK

## Before starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`.
Summarizing (not just reading) forces you to internalize what has and hasn't
worked in previous runs of this skill. If both files are empty, skip this step.

## After finishing

If this session produced anything worth capturing, append to the relevant file:

- **`.learnings/LEARNINGS.md`** — a pattern that worked well, a non-obvious API behavior, or a workflow adjustment that improved the result.
- **`.learnings/ERRORS.md`** — a failure, a script error, or a wrong assumption and how it was corrected.

Don't write an entry if nothing went wrong and nothing surprising happened. Use the entry format at the top of each file.

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
Call them via Bash: `python3 ${CLAUDE_SKILL_DIR}/scripts/<name>.py [args]`

All scripts require `CLOCKIFY_API` in the environment and default to
`--tz-offset -5` (CDT). **The default is a trap** — the user travels
(e.g. MDT, -6). Confirm the current timezone and pass `--tz-offset`
explicitly on every call.

| Script | Purpose | When to use |
|---|---|---|
| `get_day_entries.py` | Fetch all entries for a calendar day, sorted by start | Anytime you need to see what's already on a day |
| `add_jitter.py` | Apply scaled independent jitter to start and end | When the user gives an approximate duration (`~1hr`, `~30min`) |
| `check_overlap.py` | Detect overlap with existing entries and resolve interactively | **Always run before posting any new entry** (single-entry path) |
| `find_gaps.py` | Find free time slots ≥ N minutes on a given day | When looking for where to fit an entry |
| `parse_time_spec.py` | Convert fuzzy time phrases to UTC ISO datetime | When the user gives a non-exact time (`"yesterday afternoon"`, `"2pm CDT"`) |
| `refresh_cache.py` | Rebuild the Client > Project > Task workspace cache | Once, then again whenever a client/project/task is unresolvable |
| `batch_submit.py` | Post a batch of entries from a JSON intent file | Bulk fills (>5 entries); covers resolution, overlap checks, and posting |
| `lookup.py` | Importable resolver — substring hints → IDs via the cache | Used by the scripts above; not invoked directly |

### Mandatory workflow rules

1. **Always call `parse_time_spec.py`** when the user specifies a time loosely (e.g. "yesterday around 3", "this morning", "~2pm CDT"). Feed the returned `utc_iso` into subsequent scripts. (Reason: manual UTC conversion from fuzzy phrases has consistently produced off-by-one-hour errors, especially across DST boundaries.)
2. **Single-entry: always call `check_overlap.py`** with the proposed start/end before posting. Use its returned `start`/`end` for the actual entry. (Reason: posting without this check has caused overlapping entries that are difficult to untangle after the fact.)
3. **Call `add_jitter.py`** when the user prefixes a duration with `~` (tilde). Jitter both start and end independently; magnitude scales with duration. Show the jittered times in the confirmation summary. (Reason: exact round-number entries on approximate durations look fabricated; jitter makes the log credible.)

### Day fills: calendar-first scheduling (MANDATORY)

These rules apply whenever filling a day (or range of days) with estimated
entries — single-day or bulk.

0. **Confirm the user's CURRENT timezone before planning anything.** The
   user travels; do not assume CDT (-5). Ask, or infer from context, and
   pass the offset explicitly to every script (`--tz-offset`). The oof
   calendar events fix the working window in UTC (currently 15:00Z–23:00Z);
   the user's local labels for that window shift with their timezone
   (10:00–18:00 CDT ≡ 9:00–17:00 MDT). Planning in the wrong zone puts
   estimated entries an hour off — e.g. "8 AM" blocks landing at 7 AM
   local. No estimated entry should start before ~8:00 AM in the user's
   current zone.

1. **Pull the Outlook calendar first.** The Clockify public API cannot see
   the calendar events shown in the Clockify UI (confirmed: all calendar
   endpoints 404). Outlook via the Microsoft 365 MCP connector is the
   ground truth. Use `mcp__claude_ai_Microsoft_365__outlook_calendar_search`
   (load via ToolSearch if deferred) with `query: "*"`, `order: "oldest"`,
   and `afterDateTime`/`beforeDateTime` bounding the range. If the
   connector isn't available, tell the user and ask how to proceed.
2. **Skip canceled events** (`isCancelled: true`). Never log them, and
   flag any existing Clockify entry that matches a canceled meeting — it
   probably needs deleting.
3. **Log meetings by client:**
   - Internal meetings → `Flywheel > SSE Admin > Team Meetings`
   - Client meetings, or internal meetings *about* a client → that
     client's `Project Management` task (under their `Solutions Hourly`
     or `Impl. & Support` project).
4. **The working day must be contiguously filled.** The span between the
   two `Outside working hours` (`showAs: "oof"`) calendar events — e.g.
   10:00–18:00 CDT — must be covered by entries end-to-end, with a MAXIMUM
   gap of 25 minutes between consecutive entries. Gaps are fine (5–25 min
   is natural); the gap time is simply recouped by the SSE Admin > Other
   entry at the end of the day (rule 6), which may extend past working
   hours.
5. **Coding work prefers the oof window, contiguity wins.** Start the
   day's coding / development / hands-on technical work in the morning
   oof block (before working hours). When meetings + non-coding work
   (docs, writeups, project management) can't cover the working day by
   themselves, coding entries fill the remaining working hours — rule 4
   takes priority over keeping coding in oof.
6. **Every day must total EXACTLY 8.00 hours.** After meetings and work
   entries are placed, append one `Flywheel > SSE Admin > Other` entry at
   the end of the day sized to bring the total to exactly 8h — even if it
   lands outside working hours. The Other entry is the only flex; never
   pad other entries to hit the target.
7. **Every day needs at least 1.00h of `SSE Admin > Other` time** (the
   recurring 15-min "Flywheel Admin" block counts toward this). If
   meetings + work would leave less than 1h for it within the 8h total,
   shorten work entries to make room — preferring the estimated entries
   that plausibly shouldn't have taken long. Never go below 1h of SSE
   Admin time to fit more work.
8. **Personal calendar blocks (Focus Time, etc.) are reserved work
   time** — schedule work entries over them freely. The slots of canceled
   meetings are likewise free time to fill with work. Only actual
   meetings block their time.
9. Don't log Lunch calendar blocks as entries (work entries may span the
   lunch slot — it does not block scheduling).

**Default estimation mode.** When asked to fill a time period with no
further instructions, build the best estimate from two sources and apply
the rules above:

1. The Outlook calendar (rule 1) — gives each day's meetings and oof
   windows.
2. Claude session activity: scan `~/.claude/projects/*/` for `.jsonl`
   session files with mtimes in the period. File size per project per
   day approximates effort; the project directory name identifies the
   repo, which maps to a client/project (e.g. a CHOP repo dir → CHOP,
   `sdk-playground`/`core-api` → SDK docs, Claude/skills repos →
   `SSE Admin > Training/Learning`). Assume some work happened outside
   Claude sessions on the same projects.

Jira (tickets In Progress / In Review / Done in the period, via the
Atlassian MCP) is a useful third source for descriptions and client
attribution when available, but calendar + sessions are sufficient.
Always present the proposed table before posting.

### Bulk fills (>5 entries)

For multi-day or multi-entry fills, use the JSON-intent path instead of
chaining single-entry scripts:

1. **Ensure cache is current.** If `cache/workspace.json` is missing or
   `batch_submit.py` warns it's stale (>30 days), run
   `python3 scripts/refresh_cache.py` once (~1–3 minutes).
2. **Author an intent JSON** at `/tmp/clockify_batch_<topic>.json`. Use
   human-readable substring hints for `client`, `project`, `task`. Each
   hint must match a unique substring of the real name — the resolver
   prefers an exact (case-insensitive) name match if multiple candidates
   match. See `references/patterns.md` for the full schema.

   **Tiebreaker gotcha:** when a hint is *itself* the exact name of one
   candidate and also a substring of another, the exact match silently
   wins — even if the user meant the longer name. For example, the hint
   `"NACC"` matches both a literal client named `nacc` and `UWash - NACC`,
   and the resolver will pick `nacc`. Prefer the most specific name you
   can (e.g. `"UWash - NACC"` over `"NACC"`); resolution failures
   downstream are easier to debug than silently-wrong client IDs.
3. **Dry-run** first: `python3 scripts/batch_submit.py /tmp/file.json`
   prints a per-day preview and validates overlaps but posts nothing.
4. **Post** with `--yes` after the user confirms.

Resolution errors print the candidate list at the failing level — amend
the intent JSON with a more specific hint and re-run. `batch_submit.py`
internally checks for both in-batch and external overlaps; the
single-entry `check_overlap.py` is not needed.

### Script reference

```
get_day_entries.py  --date YYYY-MM-DD  --tz-offset N
add_jitter.py       --start ISO  --end ISO
check_overlap.py    --start ISO  --end ISO  --tz-offset N
find_gaps.py        --date YYYY-MM-DD  --min-duration-min N  --tz-offset N
parse_time_spec.py  --spec "TEXT"  --tz-offset N
refresh_cache.py    [--include-archived] [--clients-only | --projects-only]
batch_submit.py     INTENT_JSON  [--yes]  [--tz-offset N]  [--allow-conflicts]
```

---

## Fallback: Direct SDK

If the MCP is not available, the SDK can be called via Bash. See the reference files
for patterns. Note: `start`/`end` must be `datetime` objects — see Critical Gotcha below.

**SDK method names and pagination caveats.** The SDK wrapper method names
are `get_workplace_clients`, `get_current_workspace_projects`, and
`get_project_tasks` — not `get_clients`/`get_projects`. None of them
auto-paginate; each returns only the first 50 results. For full-workspace
scans, page manually via `cl.client.make_call(..., {"page": N,
"page-size": 200})` or use the `paginate_all` helper in `scripts/lookup.py`.

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
