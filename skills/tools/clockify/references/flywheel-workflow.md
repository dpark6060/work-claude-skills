# Clockify — Flywheel Time Logging Workflow

Two paths depending on whether a Jira ticket is involved.

---

## Path A: No Jira ticket (internal work)

When the user names a project and task directly (e.g. "log 43 min under SSE Admin, Training/Learning"):

1. **Resolve the client** — internal Flywheel work uses client `"Flywheel"` (`624529bbd0b47f4cf4a12c20`). Load from cache if uncertain.
2. **Find the project** by name under that client via `get_current_workspace_projects(clients=client_id)`
3. **Find the task** by name substring in `get_project_tasks(project_id)`
4. **Set `billable: False`** for internal projects (SSE Admin, Internal Projects, etc.)
5. **Confirm and post** — use the same confirmation table format as Path B

---

## Path B: Jira ticket

When asked to log time for a Flywheel Jira ticket, follow these steps exactly.

---

## Client Cache

A pre-built JSON cache of all Clockify clients lives at:

```
/Users/davidparker/Documents/Flywheel/Claude/skills/clockify/cache/clients.json
```

Format: `{ "Client Name": "clockify_client_id", ... }` — 172 entries, sorted alphabetically.

**Always load this first** before making any API calls. Only fall back to a live API
fetch if the client name isn't in the cache, or if the ID appears invalid (e.g. the
API returns a 404 or empty project list for that client ID). After a live re-fetch,
overwrite the cache file.

```python
import json
from pathlib import Path

CACHE_PATH = Path('/Users/davidparker/Documents/Flywheel/Claude/skills/clockify/cache/clients.json')

def load_client_cache() -> dict:
    with open(CACHE_PATH) as f:
        return json.load(f)

def refresh_client_cache(cl) -> dict:
    all_clients = []
    page = 1
    while True:
        batch = cl.client.make_call('get', f'workspaces/{cl.workspaceId}/clients',
                                     params={'page': page, 'page-size': 50})
        all_clients.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    cache = {c['name']: c['id'] for c in sorted(all_clients, key=lambda c: c['name'].lower())}
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)
    return cache
```

---

## Step 1: Fetch the Jira ticket

Use the Atlassian MCP with `cloudId: flywheelio.atlassian.net`.

Key fields to extract:
- **`customfield_10108`** — Customer/s (e.g. `"UWash - NACC"`) — maps to Clockify client name
- **`parent`** — Parent Epic key + summary (e.g. `GEAR-7595: [NACC] LONI Exporter`)
- **`labels`** — Look for `Hourly` or `Fixed` to determine project type

```
Hourly label → look in "Solutions Hourly" projects
Fixed label  → look in "Solutions Fixed" projects
(no label)   → default to "Solutions Hourly", ask user if ambiguous
```

---

## Step 2: Resolve the Clockify client ID

Load the cache and look up the customer name. Client names may have slight variations —
fuzzy match on key words (e.g. `"NACC"`, `"UWash"`) if an exact match fails.

```python
cache = load_client_cache()

# Try exact match first
customer_name = "UWash - NACC"
client_id = cache.get(customer_name)

# Fall back to fuzzy match
if not client_id:
    keyword = "nacc"
    match = next((name for name in cache if keyword in name.lower()), None)
    client_id = cache[match] if match else None

# If still not found, refresh cache and try again
if not client_id:
    cache = refresh_client_cache(cl)
    client_id = cache.get(customer_name)

if not client_id:
    # Pause and ask the user
    raise ValueError(f"Client '{customer_name}' not found even after cache refresh")
```

If the cache returns an ID but subsequent API calls return empty results or errors,
call `refresh_client_cache(cl)` and retry once before asking the user.

---

## Step 3: Find the right Clockify project

Filter `get_current_workspace_projects()` by client ID, then pick the project whose
name matches the label-driven type ("Solutions Hourly" or "Solutions Fixed").

```python
projects = cl.get_current_workspace_projects(clients=client_id)
target_type = "Solutions Hourly"  # or "Solutions Fixed"

# Prefer exact name match; avoid year-suffixed variants (e.g. "Solutions Hourly - 2023/2024")
candidates = [p for p in projects if p['name'] == target_type]
if not candidates:
    candidates = [p for p in projects if p['name'].startswith(target_type)]

project = candidates[0] if len(candidates) == 1 else None
if not project:
    # Pause and ask the user to choose
    ...
```

---

## Step 4: Find the task

Fetch tasks for the project and match by Epic key (`GEAR-XXXX`). Task names follow the
format `[GEAR-XXXX]: <description>` — match on the ticket number, not the text.

- If the Jira ticket has a **parent Epic**: match on the Epic's key (e.g. `GEAR-7595`)
- If there is **no parent Epic**: match on the ticket's own key (e.g. `GEAR-11709`)

```python
tasks = cl.get_project_tasks(project['id'])
epic_key = 'GEAR-7595'
task = next((t for t in tasks if epic_key in t['name']), None)

if not task:
    # Pause and ask the user — do not guess
    ...
```

---

## Step 5: Build and post the time entry

- `description` — `"GEAR-XXXXX: <ticket summary>"`
- `projectId` — from step 3
- `taskId` — from step 4
- `billable` — `True` for customer work (Hourly/Fixed labels)
- `start` / `end` — naive UTC `datetime` objects (**not strings** — see SKILL.md gotcha)

```python
from datetime import datetime, timedelta, timezone
from ClockifySdk.Models.time_entry import TimeEntryInput

end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
start_dt = end_dt - timedelta(hours=1, minutes=13)

entry = TimeEntryInput({
    'description': 'GEAR-11709: NACC LONI: Add mixed-protocol MRI skip (UnsupportedProtocolError)',
    'projectId': project['id'],
    'taskId': task['id'],
    'start': start_dt,
    'end': end_dt,
    'billable': True,
})
cl.add_time_entry(entry)
```

---

## Step 6: Confirm before posting

Always show the user a summary of what will be posted and wait for confirmation:

```
Description : GEAR-11709: NACC LONI: Add mixed-protocol MRI skip (UnsupportedProtocolError)
Client      : UWash - NACC
Project     : Solutions Hourly
Task        : [GEAR-7595]: [NACC] LONI Exporter
Start       : 2026-04-07T13:30:00Z
End         : 2026-04-07T14:43:00Z
Billable    : True
```

---

## When to pause and ask the user

- Client not found in cache or after refresh
- API returns empty/invalid results for a cached client ID (refresh cache, retry once first)
- Multiple ambiguous projects after applying name-match preference
- No task matching the Epic/ticket key
- Jira ticket has no `Customer/s` field set
- Label is neither `Hourly` nor `Fixed`
