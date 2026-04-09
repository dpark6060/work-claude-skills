# Clockify SDK — Data Models

---

## TimeEntryInput

Used to create new time entries. Passed to `cl.add_time_entry()`.

```python
from ClockifySdk.Models.time_entry import TimeEntryInput
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | `str` | `""` | Entry label |
| `projectId` | `str` | `""` | Clockify project ID |
| `taskId` | `str` | `""` | Clockify task ID |
| `start` | `datetime` | `None` | Start time — must be a `datetime` object |
| `end` | `datetime` | `None` | End time — must be a `datetime` object |
| `billable` | `bool` | `False` | Billable flag |
| `tagIds` | `List[str]` | `[]` | Tag IDs |
| `customFields` | `List[Dict]` | `[]` | `[{customFieldId, value}]` |
| `customAttributes` | `List[Dict]` | `[]` | Custom attributes |
| `type` | `str` | `""` | Entry type |

**Critical:** `start` and `end` must be naive UTC `datetime` objects. `to_dict()` calls
`clockify_utils.encode_clockify_datestr()` on them, which calls `.strftime()`. Passing a
string will raise `AttributeError`. See SKILL.md.

**Construction:**

```python
from datetime import datetime, timedelta, timezone

end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
start_dt = end_dt - timedelta(hours=1, minutes=30)

# From dict
entry = TimeEntryInput({
    "description": "Code review",
    "projectId": "abc123",
    "start": start_dt,
    "end": end_dt,
    "billable": True,
})

# From a task dict — sets taskId from task["id"]
task = {"id": "task_456", "name": "Implement feature"}
entry = TimeEntryInput.from_task(task)
entry.description = "Implementing feature"
entry.projectId = "abc123"
entry.start = start_dt
entry.end = end_dt
```

**Methods:**

- `to_dict() -> Dict` — Serializes to API-ready dict (encodes start/end to ISO strings)
- `from_task(entry: Dict) -> TimeEntryInput` — classmethod; sets `taskId` from `entry["id"]`
- `__str__() -> str` — Human-readable summary

**API fields not in TimeEntryInput:** The API also accepts `type` (present in SDK) but
does not use `customAttributes` (SDK-only field that gets sent but is not an API field).

---

## TimeEntryOutput

Returned by `cl.get_workspace_time_entries()`. Represents a stored entry.

```python
from ClockifySdk.Models.time_entry import TimeEntryOutput
```

**Fields (mapped from API response):**

| SDK Field | API Field | Type | Description |
|-----------|-----------|------|-------------|
| `id` | `id` | `str` | Entry ID |
| `description` | `description` | `str` | Entry description |
| `projectId` | `projectId` | `str` | Project ID |
| `taskId` | `taskId` | `str` | Task ID |
| `userId` | `userId` | `str` | User who logged the entry |
| `workspaceId` | `workspaceId` | `str` | Workspace ID |
| `billable` | `billable` | `bool` | Billable flag |
| `isLocked` | `isLocked` | `bool` | Entry locked status |
| `kioskId` | `kioskId` | `str` | Kiosk ID if applicable |
| `tagIds` | `tagIds` | `List[str]` | Tag IDs |
| `type` | `type` | `str` | Entry type |
| `timeInterval` | `timeInterval` | `TimeInterval` | Start/end/duration |
| `hourlyRate` | `hourlyRate` | `Rate` | Hourly rate applied |
| `costRate` | `costRate` | `Rate` | Cost rate applied |
| `customFieldValues` | `customFieldValues` | `List[Dict]` | Custom field data |
| `start_timestamp` | _(derived)_ | `datetime` | Decoded from `timeInterval.start` |
| `end_timestamp` | _(derived)_ | `datetime` | Decoded from `timeInterval.end` |

**API fields NOT captured by SDK:** None — the SDK maps all significant response fields.

**Methods:**

- `get_duration() -> str` — Returns `"H:MM:SS"` string (computed from start/end diff)
- `from_json(data: Dict) -> TimeEntryOutput` — classmethod constructor
- `from_time_input(entry: TimeEntryInput) -> TimeEntryOutput` — classmethod
- `to_dict() -> Dict` — Serializes back to dict
- `plot_entry(axis, color, linewidth)` — matplotlib helper (internal use)

**Usage:**

```python
entries = cl.get_workspace_time_entries(start="2024-01-01T00:00:00Z")
for e in entries:
    print(e.description)
    print(e.start_timestamp, "→", e.end_timestamp)   # datetime objects
    print(e.get_duration())                           # "2:30:00"
    print(e.projectId, e.taskId)
    print(e.billable, e.isLocked)
```

---

## TimeInterval

Embedded in `TimeEntryOutput.timeInterval`.

| Field | Type | Description |
|-------|------|-------------|
| `start` | `str` or `None` | ISO 8601 start string (`"2024-01-15T09:00:00Z"`) |
| `end` | `str` or `None` | ISO 8601 end string |
| `duration` | `str` or `None` | ISO 8601 duration (`"PT2H30M"`) — **not** `"H:MM:SS"` |

Access decoded datetimes via `entry.start_timestamp` / `entry.end_timestamp` on
`TimeEntryOutput` — these are computed in `__init__`.

`TimeInterval` has a `to_dict()` method (used by `TimeEntryOutput.to_dict()`).

**Note on `duration`:** The API returns ISO 8601 duration format (e.g. `"PT2H30M"`).
`TimeEntryOutput.get_duration()` recomputes from start/end diff and returns `"H:MM:SS"`.

---

## ProjectEntry

Typed project model.

```python
from ClockifySdk.Models.project_entry import ProjectEntry

projects_raw = cl.get_current_workspace_projects()
projects = [ProjectEntry.init_from_json(p) for p in projects_raw]
```

**Fields mapped by SDK:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Project ID |
| `name` | `str` | Project name |
| `color` | `str` | Hex color (default `"#000000"`) |
| `duration` | `str` | Total logged duration |
| `note` | `str` | Project notes |
| `public` | `bool` | Visibility flag |
| `workspaceId` | `str` | Workspace ID |
| `memberships` | `List[Membership]` | Project members |

**API fields returned but NOT in SDK model:** `clientId`, `clientName`, `archived`,
`billable`, `hourlyRate`, `costRate`, `estimate`, `timeEstimate`, `budgetEstimate`.
Access these from the raw dict before converting:

```python
raw = cl.get_current_workspace_projects()
for p in raw:
    client_id = p.get("clientId")      # not on ProjectEntry
    is_billable = p.get("billable")    # not on ProjectEntry
    project = ProjectEntry.init_from_json(p)
```

---

## WorkspaceEntry

Returned by `cl.get_flywheel_workspace()`.

```python
from ClockifySdk.Models.workspace_entry import WorkspaceEntry
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Workspace ID |
| `name` | `str` | Workspace name |
| `imageUrl` | `str` | Image URL |
| `featureSubscriptionType` | `str` | Subscription tier |
| `features` | `List[str]` | Enabled features |
| `currencies` | `List[Currency]` | Available currencies |
| `memberships` | `List[Membership]` | Members |
| `workspaceSettings` | `WorkspaceSettings` | Full settings object |
| `hourlyRate` | `Rate` | Default hourly rate |
| `costRate` | `Rate` | Default cost rate |
| `subdomain` | `Subdomain` | Subdomain config |

`WorkspaceEntry()` (no args) returns an empty instance with zero-value defaults —
used as the "not found" sentinel from `get_flywheel_workspace()`.

---

## WorkspaceSettings

Embedded in `WorkspaceEntry.workspaceSettings`. Reflects workspace configuration
options. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `forceDescription` | `bool` | Require description on entries |
| `forceProjects` | `bool` | Require project on entries |
| `forceTasks` | `bool` | Require task on entries |
| `forceTags` | `bool` | Require tags on entries |
| `defaultBillableProjects` | `bool` | New projects default billable |
| `onlyAdminsCreateProject` | `bool` | Restrict project creation |
| `onlyAdminsSeeAllTimeEntries` | `bool` | Restrict entry visibility |
| `lockTimeEntries` | `str` | Lock policy string |
| `automaticLock` | `AutomaticLock` | Auto-lock configuration |
| `timeTrackingMode` | `str` | e.g. `"DEFAULT"` |
| `trackTimeDownToSecond` | `bool` | Second-level precision |
| `durationFormat` | `str` | Display format |
| `round` | `Round` | Time rounding config |

---

## Rate

Used in billing fields across models.

| Field | Type | Default |
|-------|------|---------|
| `amount` | `float` | `0.0` |
| `currency` | `str` | `"USD"` |

```python
rate = Rate.init_from_json({"amount": 150.0, "currency": "USD"})
```

---

## Membership

Used in `ProjectEntry.memberships` and `WorkspaceEntry.memberships`.

| Field | Type | Description |
|-------|------|-------------|
| `userId` | `str` | Member's user ID |
| `targetId` | `str` | Target resource ID |
| `membershipStatus` | `str` | e.g. `"ACTIVE"`, `"PENDING"` |
| `membershipType` | `str` | e.g. `"PROJECT"`, `"WORKSPACE"` |
| `hourlyRate` | `Rate` | Member's hourly rate |
| `costRate` | `Rate` | Member's cost rate |

---

## Currency

Embedded in `WorkspaceEntry.currencies`.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Currency ID |
| `code` | `str` | e.g. `"USD"` |
| `isDefault` | `bool` | Default currency flag |

---

## Subdomain

Embedded in `WorkspaceEntry.subdomain`.

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | `bool` | Whether subdomain is active |
| `name` | `str` | Subdomain name |

---

## AutomaticLock

Embedded in `WorkspaceSettings.automaticLock`.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | Lock type |
| `changeDay` | `str` | Day of change |
| `dayOfMonth` | `int` | Day number |
| `firstDay` | `str` | First day of period |
| `olderThanPeriod` | `str` | Period string |
| `olderThanValue` | `int` | Period value |

---

## Round

Embedded in `WorkspaceSettings.round`.

| Field | Type | Description |
|-------|------|-------------|
| `minutes` | `str` | Rounding interval in minutes |
| `round` | `str` | Rounding direction |
