# Clockify API v1 — Complete Endpoint Reference

Use `cl.client.make_call(method, path, params={...}, data={...})` for anything
not covered by the high-level SDK methods. See api-reference.md for those.

**Base URL (main API):** `https://api.clockify.me/api/v1`
**Base URL (reports API):** `https://reports.api.clockify.me/v1`

---

## Authentication

All requests require one of:
- `X-Api-Key: <key>` — personal API key from Profile Settings
- `X-Addon-Token: <token>` — for marketplace addons

The SDK sets `x-api-key` automatically from the key passed to `Clockify(api_key=...)`.

---

## Pagination

All list GET endpoints support:
- `page` (int, 1-indexed, default 1)
- `page-size` (int, default 50)

Response includes `Last-Page` header: `true` when on the final page.

**Note:** The SDK's `get_workspace_time_entries()` auto-paginates. All other SDK
methods do not — pass `page`/`page-size` manually.

---

## Rate Limits

50 requests/second per addon per workspace. Exceeding returns HTTP 429
"Too many requests".

---

## User Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| GET | `/v1/user` | `cl.get_current_user()` | Get current user info |
| POST | `/v1/file/image` | — | Upload profile photo |
| GET | `/v1/workspaces/{wId}/member-profile/{uId}` | — | Get member profile |
| PATCH | `/v1/workspaces/{wId}/member-profile/{uId}` | — | Update member profile |
| GET | `/v1/workspaces/{wId}/users` | — | List workspace users |
| POST | `/v1/workspaces/{wId}/users/info` | — | Filter workspace users (POST body) |
| PUT | `/v1/workspaces/{wId}/users/{uId}/custom-field/{cfId}/value` | — | Set user custom field |
| GET | `/v1/workspaces/{wId}/users/{uId}/managers` | — | Get user's managers |
| POST | `/v1/workspaces/{wId}/users/{uId}/roles` | — | Give manager role |
| DELETE | `/v1/workspaces/{wId}/users/{uId}/roles` | — | Remove manager role |

### GET `/v1/user` query params
| Param | Type | Description |
|-------|------|-------------|
| `include-memberships` | bool | Include membership data in response |

### GET `/v1/workspaces/{wId}/users` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `email` | string | — | Filter by email substring |
| `name` | string | — | Filter by name substring |
| `project-id` | string | — | Filter to users with access to this project |
| `status` | enum | — | `PENDING`, `ACTIVE`, `DECLINED`, `INACTIVE`, `ALL` |
| `account-statuses` | string | — | e.g. `LIMITED` |
| `sort-column` | enum | `EMAIL` | `ID`, `EMAIL`, `NAME`, `NAME_LOWERCASE`, `ACCESS`, `HOURLYRATE`, `COSTRATE` |
| `sort-order` | enum | `ASCENDING` | `ASCENDING`, `DESCENDING` |
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page |
| `memberships` | enum | `NONE` | `ALL`, `NONE`, `WORKSPACE`, `PROJECT`, `USERGROUP` |
| `include-roles` | string | `false` | Include manager role details |

---

## Workspace Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| GET | `/v1/workspaces` | `cl.get_flywheel_workspace()` (partial) | List all workspaces |
| POST | `/v1/workspaces` | — | Create workspace |
| GET | `/v1/workspaces/{wId}` | — | Get workspace by ID |

### GET `/v1/workspaces` query params
| Param | Type | Description |
|-------|------|-------------|
| `roles` | enum (repeatable) | Filter by role: `WORKSPACE_ADMIN`, `OWNER`, `TEAM_MANAGER`, `PROJECT_MANAGER` |

### POST `/v1/workspaces` body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | 1–50 characters |
| `organizationId` | string | no | Organization to attach to |

---

## Client Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| GET | `/v1/workspaces/{wId}/clients` | `cl.get_workplace_clients()` | List all clients |
| POST | `/v1/workspaces/{wId}/clients` | — | Create client |
| GET | `/v1/workspaces/{wId}/clients/{cId}` | — | Get client by ID |
| PUT | `/v1/workspaces/{wId}/clients/{cId}` | — | Update client |
| DELETE | `/v1/workspaces/{wId}/clients/{cId}` | — | Delete client |

### GET `/v1/workspaces/{wId}/clients` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | — | Filter by name substring |
| `sort-column` | string | — | Column to sort by |
| `sort-order` | enum | `ASCENDING` | `ASCENDING`, `DESCENDING` |
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page |
| `archived` | bool | — | Filter archived clients |

### Client response object
```json
{
  "id": "string",
  "name": "string",
  "workspaceId": "string",
  "archived": false,
  "address": "string",
  "email": "string",
  "note": "string",
  "currencyId": "string",
  "currencyCode": "string"
}
```

---

## Project Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| GET | `/v1/workspaces/{wId}/projects` | `cl.get_current_workspace_projects()` | List projects |
| POST | `/v1/workspaces/{wId}/projects` | — | Create project |
| POST | `/v1/workspaces/{wId}/projects/from-template` | — | Create from template |
| GET | `/v1/workspaces/{wId}/projects/{pId}` | — | Get project by ID |
| PUT | `/v1/workspaces/{wId}/projects/{pId}` | — | Update project |
| DELETE | `/v1/workspaces/{wId}/projects/{pId}` | — | Delete project |
| PATCH | `/v1/workspaces/{wId}/projects/{pId}/estimate` | — | Update estimate |
| PATCH | `/v1/workspaces/{wId}/projects/{pId}/memberships` | — | Update memberships |
| POST | `/v1/workspaces/{wId}/projects/{pId}/users` | — | Assign/remove users |
| PATCH | `/v1/workspaces/{wId}/projects/{pId}/template` | — | Update template |
| PUT | `/v1/workspaces/{wId}/projects/{pId}/users/{uId}/cost-rate` | — | Set user cost rate |
| PUT | `/v1/workspaces/{wId}/projects/{pId}/users/{uId}/hourly-rate` | — | Set user billable rate |

### GET `/v1/workspaces/{wId}/projects` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page |
| `archived` | bool | — | Filter by archived status |
| `name` | string | — | Filter by name substring |
| `clients` | string | — | Filter by client ID |
| `contains-client` | bool | — | Only return projects with a client |
| `client-status` | enum | — | `ACTIVE`, `ARCHIVED` |
| `users` | string | — | Filter by user ID |
| `contains-user` | bool | — | Only projects with users |
| `user-status` | enum | — | `ACTIVE`, `INACTIVE` |
| `is-template` | bool | — | Filter template projects |
| `sort-column` | enum | — | `ID`, `NAME`, `CLIENT_NAME`, `START_DATE`, `DUE_DATE` |
| `sort-order` | enum | `ASCENDING` | `ASCENDING`, `DESCENDING` |

### POST `/v1/workspaces/{wId}/projects` body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Project name |
| `clientId` | string | no | Associated client |
| `isPublic` | bool | no | Public visibility |
| `color` | string | no | Hex color e.g. `"#ff0000"` |
| `note` | string | no | Project description |
| `billable` | bool | no | Default billable flag |
| `hourlyRate` | object | no | `{amount, currency}` |
| `costRate` | object | no | `{amount, currency}` |
| `estimate` | object | no | `{estimate, type}` |

---

## Task Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| GET | `/v1/workspaces/{wId}/projects/{pId}/tasks` | `cl.get_project_tasks(pId)` | List tasks |
| POST | `/v1/workspaces/{wId}/projects/{pId}/tasks` | — | Create task |
| GET | `/v1/workspaces/{wId}/projects/{pId}/tasks/{tId}` | — | Get task by ID |
| PUT | `/v1/workspaces/{wId}/projects/{pId}/tasks/{tId}` | — | Update task |
| DELETE | `/v1/workspaces/{wId}/projects/{pId}/tasks/{tId}` | — | Delete task |
| PUT | `/v1/workspaces/{wId}/projects/{pId}/tasks/{tId}/cost-rate` | — | Set task cost rate |
| PUT | `/v1/workspaces/{wId}/projects/{pId}/tasks/{tId}/hourly-rate` | — | Set task billable rate |

### GET `/v1/workspaces/{wId}/projects/{pId}/tasks` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page |
| `is-active` | bool | — | Filter by active status |
| `name` | string | — | Filter by name substring |
| `sort-column` | string | — | Column to sort by |
| `sort-order` | enum | `ASCENDING` | `ASCENDING`, `DESCENDING` |

### Task response object
```json
{
  "id": "string",
  "name": "string",
  "projectId": "string",
  "workspaceId": "string",
  "assigneeIds": ["string"],
  "userGroupIds": ["string"],
  "estimate": "string",
  "status": "ACTIVE|DONE",
  "duration": "string",
  "billable": false,
  "hourlyRate": {"amount": 0, "currency": "USD"},
  "costRate": {"amount": 0, "currency": "USD"},
  "budgetEstimate": 0
}
```

---

## Time Entry Endpoints

| Method | Path | SDK method | Description |
|--------|------|-----------|-------------|
| POST | `/v1/workspaces/{wId}/time-entries` | `cl.add_time_entry()` | Add entry (current user) |
| GET | `/v1/workspaces/{wId}/time-entries` | — | Get in-progress timers |
| PATCH | `/v1/workspaces/{wId}/time-entries` | — | Mark entries as invoiced |
| GET | `/v1/workspaces/{wId}/time-entries/{teId}` | — | Get entry by ID |
| PUT | `/v1/workspaces/{wId}/time-entries/{teId}` | — | Update entry |
| DELETE | `/v1/workspaces/{wId}/time-entries/{teId}` | — | Delete entry |
| PUT | `/v1/workspaces/{wId}/time-entries/bulk` | — | Bulk edit entries |
| POST | `/v1/workspaces/{wId}/time-entries/{teId}/duplicate` | — | Duplicate entry |
| GET | `/v1/workspaces/{wId}/user/{uId}/time-entries` | `cl.get_workspace_time_entries()` | Get user's entries |
| POST | `/v1/workspaces/{wId}/user/{uId}/time-entries` | — | Add entry for another user |
| PATCH | `/v1/workspaces/{wId}/user/{uId}/time-entries` | — | Stop running timer |
| DELETE | `/v1/workspaces/{wId}/user/{uId}/time-entries` | — | Delete all user entries |

### GET `/v1/workspaces/{wId}/user/{uId}/time-entries` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `start` | string | — | ISO 8601 — entries at or after this time |
| `end` | string | — | ISO 8601 — entries at or before this time |
| `description` | string | — | Filter by description substring |
| `project` | string | — | Filter by project ID |
| `task` | string | — | Filter by task ID |
| `tags` | string | — | Filter by tag ID |
| `project-required` | bool | — | Only entries with a project |
| `task-required` | bool | — | Only entries with a task |
| `consider-duration-format` | bool | — | Apply workspace duration format |
| `hydrated` | bool | — | Expand nested objects (project, task, tag) |
| `in-progress` | bool | — | Return only running timer |
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page (max 5000) |

### POST `/v1/workspaces/{wId}/time-entries` body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | string | yes | ISO 8601 start time |
| `end` | string | no | ISO 8601 end time (omit for running timer) |
| `description` | string | no | Entry label |
| `projectId` | string | no | Project ID |
| `taskId` | string | no | Task ID |
| `tagIds` | array | no | Array of tag ID strings |
| `billable` | bool | no | Billable flag |
| `customFields` | array | no | `[{customFieldId, value}]` |
| `type` | string | no | Entry type |

### Time entry response object
```json
{
  "id": "string",
  "description": "string",
  "userId": "string",
  "projectId": "string",
  "taskId": "string",
  "workspaceId": "string",
  "billable": false,
  "isLocked": false,
  "kioskId": "string",
  "tagIds": ["string"],
  "type": "string",
  "timeInterval": {
    "start": "2024-01-15T09:00:00Z",
    "end": "2024-01-15T11:00:00Z",
    "duration": "PT2H"
  },
  "hourlyRate": {"amount": 0, "currency": "USD"},
  "costRate": {"amount": 0, "currency": "USD"},
  "customFieldValues": [{"customFieldId": "string", "value": "any"}]
}
```

**Note:** `timeInterval.duration` is ISO 8601 duration format (e.g. `"PT2H30M"`), not
`"H:MM:SS"`. Use `entry.get_duration()` on `TimeEntryOutput` for a human-readable string.

---

## Tag Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/workspaces/{wId}/tags` | List all tags |
| POST | `/v1/workspaces/{wId}/tags` | Create tag |
| GET | `/v1/workspaces/{wId}/tags/{tId}` | Get tag by ID |
| PUT | `/v1/workspaces/{wId}/tags/{tId}` | Update tag |
| DELETE | `/v1/workspaces/{wId}/tags/{tId}` | Delete tag |

### GET `/v1/workspaces/{wId}/tags` query params
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | — | Filter by name substring |
| `archived` | bool | — | Filter by archived status |
| `page` | int | 1 | Page number |
| `page-size` | int | 50 | Results per page |
| `sort-column` | string | — | Column to sort by |
| `sort-order` | enum | `ASCENDING` | `ASCENDING`, `DESCENDING` |

### Tag response object
```json
{
  "id": "string",
  "name": "string",
  "workspaceId": "string",
  "archived": false
}
```

---

## Webhook Endpoints

Workspace admins can create up to 10 webhooks each; max 100 per workspace.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/workspaces/{wId}/webhooks` | List webhooks |
| POST | `/v1/workspaces/{wId}/webhooks` | Create webhook |
| GET | `/v1/workspaces/{wId}/webhooks/{whId}` | Get webhook by ID |
| PUT | `/v1/workspaces/{wId}/webhooks/{whId}` | Update webhook |
| DELETE | `/v1/workspaces/{wId}/webhooks/{whId}` | Delete webhook |
| POST | `/v1/workspaces/{wId}/webhooks/{whId}/logs` | Get webhook logs |
| PATCH | `/v1/workspaces/{wId}/webhooks/{whId}/token` | Regenerate auth token |
| GET | `/v1/workspaces/{wId}/addons/{addonId}/webhooks` | Get addon webhooks |

Known webhook trigger events include: timer started, time entry created/updated/deleted.

---

## Reports API

**Base URL:** `https://reports.api.clockify.me/v1`

All report endpoints use POST with a JSON body containing the filter criteria.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/workspaces/{wId}/reports/detailed` | Detailed time entry report |
| POST | `/v1/workspaces/{wId}/reports/summary` | Summary report |
| POST | `/v1/workspaces/{wId}/reports/weekly` | Weekly report |
| POST | `/v1/workspaces/{wId}/reports/attendance` | Attendance/team report |
| POST | `/v1/workspaces/{wId}/reports/expense` | Expense report |
| POST | `/v1/workspaces/{wId}/reports/audit-log` | Audit log report |
| GET/POST/PUT/DELETE | `/v1/workspaces/{wId}/reports/shared` | Shared report management |

**Note:** The reports API uses a different base URL. Using `cl.client.make_call()` will hit
the wrong base URL. For reports, instantiate a separate client or use `requests` directly:

```python
import requests

headers = {"X-Api-Key": os.environ["CLOCKIFY_API"]}
body = {
    "dateRangeStart": "2024-01-01T00:00:00Z",
    "dateRangeEnd": "2024-01-31T23:59:59Z",
    "detailedFilter": {"page": 1, "pageSize": 50}
}
resp = requests.post(
    f"https://reports.api.clockify.me/v1/workspaces/{workspace_id}/reports/detailed",
    json=body,
    headers=headers
)
```

---

## Other Available Endpoint Groups

These exist in the API but are not commonly needed for time-logging workflows. Use
`cl.client.make_call()` with appropriate paths if needed.

| Group | Base path |
|-------|-----------|
| Custom fields | `/v1/workspaces/{wId}/custom-fields` |
| Expenses | `/v1/workspaces/{wId}/expenses` |
| Holidays | `/v1/workspaces/{wId}/holidays` |
| Invoices | `/v1/workspaces/{wId}/invoices` |
| Scheduling | `/v1/workspaces/{wId}/scheduling` |
| Time off / balance | `/v1/workspaces/{wId}/time-off` |
| User groups | `/v1/workspaces/{wId}/user-groups` |
| Approval requests | `/v1/workspaces/{wId}/approval-requests` |

---

## Regional API URLs

For workspaces on regional servers, replace the base URL prefix:

| Region | Prefix |
|--------|--------|
| EU (Germany) | `euc1.clockify.me/api/v1` |
| USA | `use2.clockify.me/api/v1` |
| UK | `euw2.clockify.me/api/v1` |
| AU | `apse2.clockify.me/api/v1` |

The SDK always uses `https://api.clockify.me/api/v1` (global). If targeting a regional
workspace, you'd need to set `cl.client.baseurl` or construct a separate client.
