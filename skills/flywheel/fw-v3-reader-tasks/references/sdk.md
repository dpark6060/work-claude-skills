---
type: SDK Reference
title: V3 Reader Tasks — SDK & API Reference
description: Querying and managing V3 reader task protocols and tasks programmatically via the Flywheel Python SDK (protocols_api and reader tasks).
tags: [reader-tasks, v3, sdk, python]
timestamp: 2026-07-15T00:00:00Z
---

# V3 Reader Tasks — SDK & API Reference

Querying and working with reader tasks and protocols programmatically via the Flywheel Python SDK.

---

## Protocols API

Access via `client.protocols_api`.

### Create a protocol

```python
from flywheel.models import ProtocolValidInput, ReaderTaskConfig

protocol = client.protocols_api.create_task_protocol(
    body=ProtocolValidInput(
        label="Chest CT Read",         # 2–32 chars
        task_type="read",              # currently the only valid type
        group_id="my-group",
        protocol_config=ReaderTaskConfig(longitudinal=False),  # longitudinal is required but inert — see note
        form={ ... },                  # CustomForm dict
        completion_tags=["reviewed"],
        esignature_config=None,
        workflow=None,
        notes=None,
    )
)
print(protocol._id)
```

> **`longitudinal` is required but inert (verified against source, 2026-07).** `ReaderTaskConfig` requires `longitudinal`, but no code in any Flywheel repo reads its value — it is defined/persisted in core-api, required-present by the protocol editor, and hardcoded to `False` by the web app on creation. Setting `longitudinal=True` does not change what loads or what a task spans. The task's container level is set per-task via `parent_ref` at task creation (`create_reader_task` / `batch_create_reader_task`), and cross-session viewer visibility is controlled by `viewer_config.fileBrowser.scope`. See SKILL.md for the full trace.

### Get a protocol by ID

```python
protocol = client.protocols_api.get_task_protocol(protocol_id="<id>")
```

### List / find protocols

```python
result = client.protocols_api.find_task_protocols(
    filter="label=Chest CT Read",   # FlyQL filter string
    sort="created:desc",
    limit=50,
    skip=0,
)
protocols = result.results
```

Filter examples:

| Filter | Effect |
|---|---|
| `label=my-label` | Exact label match |
| `created>2024-01-01` | Created after date |
| `status=published` | Published protocols only |

Multiple filters are comma-separated (AND): `status=published,label=my-label`

### Modify a protocol

```python
from flywheel.models import ProtocolValidModify

client.protocols_api.modify_task_protocol(
    protocol_id="<id>",
    body=ProtocolValidModify(
        form={ ... },           # updated CustomForm
        completion_tags=["reviewed"],
        esignature_config=None,
        workflow=None,
        notes=None,
        protocol_config=None,   # omit to leave unchanged
    )
)
```

### Publish a protocol

```python
client.protocols_api.publish_task_protocol(protocol_id="<id>")
```

### Archive a protocol

```python
client.protocols_api.archive_task_protocol(protocol_id="<id>")
```

### Delete a protocol

```python
client.protocols_api.delete_task_protocol(protocol_id="<id>")
```

### Check impact before deleting (dry run)

Before deleting a protocol, check whether any active tasks would be affected:

```python
impacted = client.api_client.call_api(
    f'/api/read_task_protocols/{protocol_id}/dry_run_delete', 'GET',
    response_type=object,
    auth_settings=['ApiKey'],
    _return_http_data_only=True
)
print(f"{len(impacted.get('results', []))} todo/in_progress tasks would be affected")
```

Soft-delete only — tasks already using the protocol are not affected.

---

## Tasks API

Access via `client.tasks_api`. Endpoint: `/api/tasks/reader`.

### Create a single task

```python
from flywheel.models import ReaderTaskCreate

task = client.tasks_api.create_reader_task(body=ReaderTaskCreate(...))
```

### Create tasks in batch

```python
from flywheel.models import ReaderBatchCreate

result = client.tasks_api.batch_create_reader_task(body=ReaderBatchCreate(...))
```

### Create an adjudication task set (single container)

Creates 1 adjudicator task + 2 reader tasks for a single container.

```python
from flywheel.models import AdjudicationTaskCreate

client.tasks_api.create_adjudication_task_set(body=AdjudicationTaskCreate(...))
```

### Create adjudication tasks in batch

```python
from flywheel.models import AdjudicationBatchCreate

client.tasks_api.batch_create_adjudication_task_set(body=AdjudicationBatchCreate(...))
```

### Get a task by ID

```python
task = client.tasks_api.get_reader_task(task_id="<id>")
```

### List / filter tasks

Default `limit` is **10** — always set explicitly for bulk queries.

```python
result = client.tasks_api.find_all_api_tasks_reader_get(
    filter=f"parents.project={project.id},status=todo",
    sort="created:desc",
    limit=100,
    skip=0,
    columns="status,assignee,protocol_label",  # optional: limit returned fields
)
tasks = result.results
```

The `filter` parameter uses FlyQL string syntax. Filterable fields include:

| Filter | Example |
|---|---|
| `parents.project` | `parents.project=<project_id>` |
| `parents.group` | `parents.group=my-group` |
| `parents.acquisition` | `parents.acquisition=<acquisition_id>` |
| `status` | `status=todo` |

Multiple filters are comma-separated (AND).

### Get facet counts

Get counts for a specific field across all tasks (useful for dashboards/summaries).

```python
counts = client.tasks_api.get_facets_api_tasks_reader_facets_facet_field_get(
    facet_field="status",   # TaskFacet value
    filter=f"parents.project={project.id}",
)
```

### Assign a task

```python
from flywheel.models import TaskAssign

client.tasks_api.assign_reader_task(
    task_id="<id>",
    body=TaskAssign(...)
)
```

### Modify a task

```python
from flywheel.models import ReaderTaskModify

client.tasks_api.modify_reader_task(
    task_id="<id>",
    body=ReaderTaskModify(...)
)
```

### Complete (submit) a task

```python
from flywheel.models import TaskSubmission

client.tasks_api.complete_reader_task(
    task_id="<id>",
    body=TaskSubmission(...)   # optional
)
```

### Fallback: raw HTTP

If `client.tasks_api` doesn't resolve (depends on the generated SDK version):

```python
response = client.api_client.call_api(
    '/api/tasks/reader', 'GET',
    query_params={'filter': f'parents.project={project.id}', 'limit': 100},
    response_type=object,
    auth_settings=['ApiKey'],
    _return_http_data_only=True
)
tasks = response['results']
```

---

## Form Responses API

Access via `client.form_responses_api`. Manages the form data submitted by readers for a task.

**Key behaviors:**
- Draft saves have **no validation** — responses can be saved repeatedly before submission
- Validation is enforced only on submit or task completion
- Once submitted, a response is **locked** — no further edits
- Only the task assignee can create or replace responses
- Creating/replacing a submitted response returns **409 Conflict**

### Create or replace a response (draft save)

```python
from flywheel.models import FormResponseCreate

response = client.form_responses_api.create_or_replace_task_response(
    task_id="<task_id>",
    body=FormResponseCreate(data={"field_key": "value", ...})
)
```

If a draft response already exists it is replaced. If the response is already submitted, returns 409.

### Update an existing response (draft save)

Use when you have the `response_id` and want to update in place:

```python
from flywheel.models import FormResponseBase

client.form_responses_api.update_response(
    response_id="<response_id>",
    body=FormResponseBase(data={"field_key": "value", ...})
)
```

Only works on unsubmitted responses.

### Replace a response by ID (PUT)

```python
from flywheel.models import FormResponseCreate

client.form_responses_api.put_task_response(
    task_id="<task_id>",
    response_id="<response_id>",
    body=FormResponseCreate(data={"field_key": "value", ...})
)
```

Same 409 behaviour as `create_or_replace_task_response` if already submitted.

### Submit a response (lock it)

```python
client.form_responses_api.submit_response(response_id="<response_id>")
```

Sets `submitted=true`, records `submitted_at` timestamp, sets `origin` to the submitting user. Disables further edits.

### Get a response by ID

```python
response = client.form_responses_api.get_response(response_id="<response_id>")
```

### List all responses for a task

```python
result = client.form_responses_api.list_task_responses(
    task_id="<task_id>",
    sort="created:desc",
    limit=50,
)
responses = result.results
```

### Response data shape

`data` is a flat dict of `field_key → value`. The value type depends on the field type:

| Field type | Value type | Example |
|------------|-----------|---------|
| `text` / `text-area` | string | `"Patient had prior history..."` |
| `int` / `float` | number | `42` |
| `date` | string (YYYY-MM-DD) | `"2024-01-15"` |
| `radio` / `select` | string | `"abnormal"` |
| `checkbox` | array of selected values | `["Frontal", "Parietal"]` |
| `switch` | boolean | `true` |

Only answered fields appear. Conditionally hidden fields that were never shown have no entry. Fields shown but left blank may appear as `null` or `""`.

---

## Annotations / Measurements API

Measurements a reader draws in the viewer (Length, Bidirectional, etc.) are **not** stored in the
form response. They live in the **v3 annotation store** and are retrieved separately, filtered by
the reader task's 24-hex `_id`.

```python
task_id = "6a591ae418aa8b7e52831930"   # reader task _id == viewer URL taskId=
anns = fw.get(
    "/api/v3/annotations",
    params={"filter": f"task_id={task_id}", "limit": 100},
).results
for ann in anns:
    for el in ann.elements:
        print(el.type, el.label, el.metrics)
```

> **`task_id` = the reader task `_id`** (24-hex, `^[0-9a-fA-F]{24}$`), **not** the task object's
> human-readable `task_id` field (e.g. `"R-13-3"`). The `R-13-3` form 422s.

### Annotation shape

```json
{
  "elements": [
    {
      "label": "ivh",
      "type": "Bidirectional",
      "color": "#ffb400",
      "metrics": { "length": 16.66, "width": 15.47, "units": { "spatial": "mm" } }
    }
  ],
  "task_id": "6a591ae418aa8b7e52831930",
  "parents": { "project": "...", "session": "...", "acquisition": "...",
               "file": { "file_id": "6a5535d2ac6825abd7324bec", "version": 1 } },
  "origin": { "type": "user", "id": "reader@site.org" },
  "state": "LOCKED",
  "storage": { "format": "SR" }
}
```

- `elements[]` — one per drawn measurement: `type`, reader-chosen `label` (from `viewer_config.labels`),
  `color`, and `metrics` (numeric stats + units).
- A `Bidirectional` captures **two in-plane axes** (length + width) only. There is **no through-plane /
  slice-height dimension** — an ABC/2 "C" is not in the annotation.
- The only thing tying a measurement to a specific finding/lesion is its `label`. Nothing validates
  the reader labeled it correctly, and the default label set is keyed by finding type, not lesion index.
- `state` is `LOCKED` once the task is submitted; `origin` records the reader; stored as a DICOM `SR`.

### Endpoint gotchas (verified on pp2dg4, Flywheel 22.1.6, 2026-07-17)

- **Use `/api/v3/annotations`.** The legacy `GET /api/readertasks/{id}/annotations` 404s for V3 tasks
  (that route's store doesn't hold V3 Tasks Manager tasks).
- **v1 `GET /api/annotations` does not contain V3 task annotations** — returns `200` with 0 rows even
  when filtered by the correct 24-hex `file_ref.file_id`.
- v1 `/api/annotations` requires the 24-hex `file_id` (via `file_ref.file_id=`); passing a file's
  storage **uuid** yields a misleading `500 Unexpected error during deserialization`, not a clean 4xx.

---

## Staffing Pools API

Access via `client.staffing_pools_api`. Staffing pools are groups of users that can be assigned to tasks collectively.

### Create a staffing pool

```python
from flywheel.models import StaffingPoolCreate

pool = client.staffing_pools_api.create_staffing_pool(
    body=StaffingPoolCreate(...)
)
```

### Get a pool by ID

```python
pool = client.staffing_pools_api.get_staffing_pool(pool_id="<pool_id>")
```

### List / filter pools

```python
result = client.staffing_pools_api.find_all_api_staffing_pools_get(
    filter="label=my-pool",
    sort="label:asc",
    limit=50,
)
pools = result.results
```

### Modify a pool

```python
from flywheel.models import StaffingPoolModify

client.staffing_pools_api.modify_staffing_pool(
    pool_id="<pool_id>",
    body=StaffingPoolModify(...)
)
```

### Add a user to multiple pools

```python
from flywheel.models import StaffingPoolList

client.staffing_pools_api.set_user_staffing_pools(
    user_id="<user_id>",
    body=StaffingPoolList(...)
)
```

### Delete a pool

```python
client.staffing_pools_api.delete_staffing_pool(pool_id="<pool_id>")
```

---

## ReaderTaskOutput — Key Fields

| Field | Description |
|---|---|
| `_id` | Task ID |
| `status` | `todo`, `in_progress`, `completed`, `cancelled` |
| `assignee` | Who the task is assigned to |
| `protocol_id` / `protocol_label` | Associated protocol |
| `parents.project` / `.group` / `.acquisition` | Hierarchy IDs for filtering |
| `parent_details.project_label` | Human-readable project label (no extra lookup needed) |
| `priority` | Task priority |
| `due_date` | Due date |
