# Clockify SDK — Common Patterns

---

## Pattern: Basic Setup

Always start with:

```python
import os
from ClockifySdk.clockify_sdk import Clockify

cl = Clockify(api_key=os.environ["CLOCKIFY_API"])
cl.get_flywheel_workspace()   # sets cl.current_workspace
```

If you're not in the "Flywheel" workspace, set `current_workspace` directly:

```python
cl.current_workspace = "your_workspace_id"
```

---

## Pattern: Fetching All Time Entries for a Date Range

```python
entries = cl.get_workspace_time_entries(
    start="2024-01-01T00:00:00Z",
    end="2024-01-31T23:59:59Z"
)
# Auto-paginated — returns ALL entries, not just page 1
```

Use `clockify_utils` to build the date strings from Python datetimes:

```python
from ClockifySdk import clockify_utils
from datetime import datetime

start_dt = datetime(2024, 1, 1, 0, 0, 0)
end_dt = datetime(2024, 1, 31, 23, 59, 59)

entries = cl.get_workspace_time_entries(
    start=clockify_utils.encode_clockify_datestr(start_dt),
    end=clockify_utils.encode_clockify_datestr(end_dt)
)
```

---

## Pattern: Working with Projects

```python
from ClockifySdk.Models.project_entry import ProjectEntry

# Get raw project dicts
projects_raw = cl.get_current_workspace_projects()

# Convert to typed objects
projects = [ProjectEntry.init_from_json(p) for p in projects_raw]

# Look up a project by name
project = next((p for p in projects if p.name == "My Project"), None)
if project:
    print(project.id)
```

Filter by client on the API side to reduce results:

```python
projects_raw = cl.get_current_workspace_projects(clients="client_id_here")
```

---

## Pattern: Getting Tasks for a Project

```python
tasks = cl.get_project_tasks(project.id)
for t in tasks:
    print(t["id"], t["name"], t.get("status"))
```

---

## Pattern: Creating a Time Entry

```python
from ClockifySdk.Models.time_entry import TimeEntryInput

entry = TimeEntryInput({
    "description": "Weekly sync",
    "projectId": project.id,
    "taskId": task["id"],           # optional
    "start": "2024-01-15T14:00:00Z",
    "end": "2024-01-15T14:30:00Z",
    "billable": True,
})
cl.add_time_entry(entry)
```

---

## Pattern: Creating a Time Entry from a Task

When you already have a task dict and want to log time against it:

```python
from ClockifySdk.Models.time_entry import TimeEntryInput
from ClockifySdk import clockify_utils
from datetime import datetime

task = tasks[0]  # dict with "id", "name", etc.

entry = TimeEntryInput.from_task(task)
entry.description = f"Working on {task['name']}"
entry.projectId = project.id
entry.start = clockify_utils.encode_clockify_datestr(datetime(2024, 1, 15, 9, 0))
entry.end = clockify_utils.encode_clockify_datestr(datetime(2024, 1, 15, 11, 0))

cl.add_time_entry(entry)
```

---

## Pattern: Analyzing Time Entry Durations

```python
entries = cl.get_workspace_time_entries(start="2024-01-01T00:00:00Z")

for e in entries:
    # Duration as formatted string
    duration_str = e.get_duration()        # "2:30:00"
    
    # Start/end as datetime objects
    start = e.start_timestamp              # datetime
    end = e.end_timestamp                  # datetime
    
    # Compute delta manually if needed
    from datetime import timedelta
    delta = end - start
    hours = delta.total_seconds() / 3600
    
    print(f"{e.description}: {hours:.2f}h")
```

---

## Pattern: Multi-Workspace Usage

```python
# List all workspaces via low-level call
workspaces_raw = cl.client.make_call("get", "workspaces")

for ws in workspaces_raw:
    print(ws["id"], ws["name"])

# Switch to a specific workspace
cl.current_workspace = workspaces_raw[1]["id"]

# All subsequent calls now use this workspace
entries = cl.get_workspace_time_entries(start="2024-01-01T00:00:00Z")
```

---

## Pattern: Repeating Events

Entries whose description ends in `REP[<days>]` are treated as repeating events.
Day codes: `M`=Mon, `T`=Tue, `W`=Wed, `R`=Thu, `F`=Fri.

```python
from ClockifySdk import clockify_utils

# Decode which days an entry repeats on (returns list of weekday ints, 0=Mon)
days = clockify_utils.decode_days("Standup REP[MTWRF]")
# → [0, 1, 2, 3, 4]

days = clockify_utils.decode_days("Team sync REP[TR]")
# → [1, 3]

# Returns None if no REP pattern in description
days = clockify_utils.decode_days("One-off task")
# → None
```

To propagate a repeating entry to the current week:

```python
entries = cl.get_workspace_time_entries(start="2024-01-01T00:00:00Z")

for entry in entries:
    repeat_days = clockify_utils.decode_days(entry.description)
    if repeat_days is None:
        continue
    
    # Check if today matches a repeat day
    from datetime import date
    today = date.today()
    if today.weekday() in repeat_days:
        # Create new entry for today
        new_entry = TimeEntryInput({
            "description": entry.description,
            "projectId": entry.projectId,
            "taskId": entry.taskId,
            "start": ...,  # today's start time
            "end": ...,    # today's end time
        })
        cl.add_time_entry(new_entry)
```

---

## Pattern: Low-Level API Call (Custom Endpoints)

For anything not covered by the high-level methods:

```python
# GET example
tags = cl.client.make_call(
    "get",
    f"workspaces/{cl.workspaceId}/tags"
)

# POST example
new_project = cl.client.make_call(
    "post",
    f"workspaces/{cl.workspaceId}/projects",
    data={
        "name": "New Project",
        "isPublic": False,
        "color": "#ff0000",
    }
)
```

See Clockify API docs for all available endpoints. Base URL is
`https://api.clockify.me/api/v1`.
