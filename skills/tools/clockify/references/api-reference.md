# Clockify SDK — API Reference

All methods are on the `Clockify` class unless noted.
For endpoints not covered here, see endpoints.md for the full endpoint map and use
`cl.client.make_call()`.

---

## Initialization

```python
cl = Clockify(api_key: str)
```

Fetches current user on construction. Populates `cl.userId`, `cl.default_workspace`.

---

## User

### `get_current_user() -> dict`

Returns the authenticated user's profile.

**Endpoint:** `GET /v1/user`

```python
user = cl.get_current_user()
# user["id"], user["defaultWorkspace"], user["email"], user["name"]
# user["activeWorkspace"], user["status"], user["settings"]
```

**Response fields:** `id`, `email`, `name`, `activeWorkspace`, `defaultWorkspace`,
`profilePicture`, `status` (`ACTIVE`/`INACTIVE`), `customFields`, `memberships`, `settings`

---

## Workspaces

### `get_flywheel_workspace() -> WorkspaceEntry`

Fetches all workspaces, finds the one named `"Flywheel"`, sets `cl.current_workspace`
to that workspace's ID, and returns it as a `WorkspaceEntry`. Returns an empty
`WorkspaceEntry` if not found.

**Endpoint:** `GET /v1/workspaces`

```python
ws = cl.get_flywheel_workspace()
# cl.current_workspace is now set
print(ws.id, ws.name)
```

### `get_workplace_clients() -> List[dict]`

Returns all clients in the current workspace as raw dicts.

**Endpoint:** `GET /v1/workspaces/{workspaceId}/clients`

```python
clients = cl.get_workplace_clients()
for c in clients:
    print(c["id"], c["name"])
```

**Response fields per client:** `id`, `name`, `workspaceId`, `archived`, `address`,
`email`, `note`, `currencyId`, `currencyCode`

**Note:** No auto-pagination. If the workspace has more than 50 clients, paginate manually
via `cl.client.make_call()`. See flywheel-workflow.md for the pagination pattern.

---

## Projects

### `get_current_workspace_projects(**kwargs) -> List[dict]`

Returns projects in the current workspace as raw dicts. Accepts any Clockify
query params as kwargs.

**Endpoint:** `GET /v1/workspaces/{workspaceId}/projects`

**Supported kwargs:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default 1) |
| `page-size` | int | Results per page (default 50) |
| `archived` | bool | Filter by archived status |
| `name` | string | Filter by name substring |
| `clients` | string | Filter by client ID |
| `contains-client` | bool | Only projects with a client |
| `client-status` | enum | `ACTIVE`, `ARCHIVED` |
| `users` | string | Filter by user ID |
| `contains-user` | bool | Only projects with users |
| `user-status` | enum | `ACTIVE`, `INACTIVE` |
| `is-template` | bool | Template projects only |
| `sort-column` | enum | `ID`, `NAME`, `CLIENT_NAME`, `START_DATE`, `DUE_DATE` |
| `sort-order` | enum | `ASCENDING`, `DESCENDING` |

```python
# All projects
projects = cl.get_current_workspace_projects()

# Filter by client ID
projects = cl.get_current_workspace_projects(clients="client_id_here")

# Convert to typed objects
from ClockifySdk.Models.project_entry import ProjectEntry
typed = [ProjectEntry.init_from_json(p) for p in projects]
```

**Note:** No auto-pagination. Pass `page`/`page-size` manually for large workspaces.

**Response fields per project:** `id`, `name`, `color`, `workspaceId`, `clientId`,
`clientName`, `duration`, `note`, `public`, `archived`, `billable`, `hourlyRate`,
`costRate`, `estimate`, `memberships`, `timeEstimate`, `budgetEstimate`

**SDK model gap:** `ProjectEntry.init_from_json()` maps only `id`, `name`, `color`,
`duration`, `note`, `public`, `workspaceId`, `memberships`. Fields `clientId`,
`clientName`, `archived`, `billable`, `hourlyRate`, `costRate` are available in the
raw dict but not in the `ProjectEntry` dataclass.

### `get_project_tasks(project_id: str, **kwargs) -> List[dict]`

Returns all tasks for a project as raw dicts.

**Endpoint:** `GET /v1/workspaces/{workspaceId}/projects/{projectId}/tasks`

**Supported kwargs:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default 1) |
| `page-size` | int | Results per page (default 50) |
| `is-active` | bool | Filter by active status |
| `name` | string | Filter by name substring |
| `sort-column` | string | Column to sort by |
| `sort-order` | enum | `ASCENDING`, `DESCENDING` |

```python
tasks = cl.get_project_tasks("project_id_here")
for t in tasks:
    print(t["id"], t["name"], t.get("status"))   # status: "ACTIVE" or "DONE"
```

**Note:** No auto-pagination. Pass `page`/`page-size` manually for projects
with more than 50 tasks, or use `paginate_all()` from
`scripts/lookup.py`.

**Response fields per task:** `id`, `name`, `projectId`, `workspaceId`, `assigneeIds`,
`userGroupIds`, `estimate`, `status` (`ACTIVE`/`DONE`), `duration`, `billable`,
`hourlyRate`, `costRate`, `budgetEstimate`

---

## Time Entries

### `get_workspace_time_entries(**kwargs) -> List[TimeEntryOutput]`

Returns time entries for the current user. **Auto-paginates by default** (page size 50).
Pass `page=N` explicitly to fetch a single specific page.

**Endpoint:** `GET /v1/workspaces/{workspaceId}/user/{userId}/time-entries`

**Supported kwargs:**

| Param | Type | Description |
|-------|------|-------------|
| `start` | string | ISO 8601 — entries at or after this time |
| `end` | string | ISO 8601 — entries at or before this time |
| `description` | string | Filter by description substring |
| `project` | string | Filter by project ID |
| `task` | string | Filter by task ID |
| `tags` | string | Filter by tag ID |
| `project-required` | bool | Only entries with a project assigned |
| `task-required` | bool | Only entries with a task assigned |
| `hydrated` | bool | Expand project/task/tag objects inline |
| `in-progress` | bool | Return only the running timer |
| `page` | int | Fetch a specific page (disables auto-pagination) |
| `page-size` | int | Results per page (default 50, max 5000) |

```python
# All entries in range (auto-paginated)
entries = cl.get_workspace_time_entries(
    start="2024-01-01T00:00:00Z",
    end="2024-01-31T23:59:59Z"
)

# Filter by description substring
entries = cl.get_workspace_time_entries(description="standup")

# Single specific page
page = cl.get_workspace_time_entries(page=2, **{"page-size": 100})
```

Returns `List[TimeEntryOutput]` — see models.md for field details.

### `add_time_entry(time_entry: TimeEntryInput) -> None`

Posts a new time entry for the current user.

**Endpoint:** `POST /v1/workspaces/{workspaceId}/time-entries`

`start` and `end` in the input must be `datetime` objects (not strings) — see
SKILL.md "Critical Gotcha" section.

```python
from datetime import datetime, timedelta, timezone
from ClockifySdk.Models.time_entry import TimeEntryInput

end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
start_dt = end_dt - timedelta(hours=1, minutes=30)

entry = TimeEntryInput({
    "description": "Sprint planning",
    "projectId": "abc123",
    "taskId": "task456",
    "start": start_dt,
    "end": end_dt,
    "billable": True,
    "tagIds": ["tag789"],
})
cl.add_time_entry(entry)
```

Returns `None`. The API returns the created entry but the SDK discards it.

---

## Low-Level Access

### `ClockifyClient.make_call(action, endpoint, params=None, data=None) -> Any`

Direct HTTP call. Access via `cl.client`. For endpoints not covered by the high-level
methods above.

```python
# GET tags
tags = cl.client.make_call("get", f"workspaces/{cl.workspaceId}/tags")

# POST new project
new_project = cl.client.make_call(
    "post",
    f"workspaces/{cl.workspaceId}/projects",
    data={"name": "New Project", "isPublic": False, "color": "#ff0000"}
)

# PUT update a time entry
cl.client.make_call(
    "put",
    f"workspaces/{cl.workspaceId}/time-entries/{entry_id}",
    data={"description": "Updated description", "start": "...", "end": "..."}
)

# DELETE a time entry
cl.client.make_call(
    "delete",
    f"workspaces/{cl.workspaceId}/time-entries/{entry_id}"
)
```

**Note:** `data` must be a JSON-serializable dict (not a string). The `add_time_entry()`
method calls `json.dumps(data)` before passing to `make_call`, which is an inconsistency —
when calling `make_call` directly, pass a plain dict.

**Base URL:** `https://api.clockify.me/api/v1`

**Auth:** `x-api-key` header set automatically.

**See endpoints.md** for the full list of available paths.

---

## Workspace ID Resolution

`cl.workspaceId` (property) returns:
- `cl.current_workspace` if set
- `cl.default_workspace` otherwise

Always call `cl.get_flywheel_workspace()` or set `cl.current_workspace` explicitly
before making workspace-scoped calls if your target workspace differs from the default.
