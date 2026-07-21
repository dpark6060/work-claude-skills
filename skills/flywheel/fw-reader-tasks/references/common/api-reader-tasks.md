---
type: API Reference
title: "API Reference: Reader Tasks"
description: REST endpoints for reader tasks (/api/readertasks) — listing, filtering, and managing task assignments and status.
tags: [reader-tasks, api, tasks]
timestamp: 2026-07-15T00:00:00Z
---

# API Reference: Reader Tasks (`/api/readertasks`)

Source: `fw-client` OpenAPI spec, tag `reader_tasks`.

---

## List all tasks (global)

```
GET /api/readertasks
```

| Param | Type | Notes |
|-------|------|-------|
| `filter` | string | Comma-separated. e.g. `assignee=user@example.com,status=Complete` |
| `sort` | string | e.g. `created:desc` |
| `limit` | integer | Max entries to return |
| `skip` | integer | Entries to skip |
| `page` | integer | Page number |
| `after_id` | string | Cursor pagination (cannot combine with sort/page/skip) |
| `exhaustive` | boolean | Return all results (admin only) |

```python
tasks = fw.get("/api/readertasks", params={"filter": "status=Todo", "limit": 100}).results
```

---

## List tasks for a project

```
GET /api/readertasks/project/{project_id}
```

Same filter/sort/pagination params as above. **Preferred over the global endpoint** when you know the project.

```python
tasks = fw.get(
    f"/api/readertasks/project/{project_id}",
    params={"filter": f"protocol_id={protocol_id},status=Complete"}
).results
```

Filterable fields include: `status`, `assignee`, `protocol_id`, `tags`, `due_date`, `priority`.

---

## Get a single task

```
GET /api/readertasks/{task_id}
```

```python
task = fw.get(f"/api/readertasks/{task_id}")
print(task._id, task.status, task.assignee, task.form_id, task.protocol_id)
```

---

## Get full task details

```
GET /api/readertasks/{task_id}/details
```

Returns expanded task info including related objects.

---

## Get viewer launch context

```
GET /api/readertasks/{task_id}/launch_viewer
```

Returns `TaskContextData` — the viewer URL and context payload.

---

## Create a single task

```
POST /api/readertasks
```

Body fields: `assignee`, `parent` (object with `type` + `id`), `status`, `form_id`, `viewer`, `viewer_config_id`, `protocol_id`, `due_date`, `priority`, `tags`, `description`.

```python
task = fw.post("/api/readertasks", json={
    "assignee": "reader@example.com",
    "parent": {"type": "session", "id": session_id},
    "protocol_id": protocol_id,
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "viewer": "OHIF_V3",
    "task_type": "R",
    "due_date": "2025-06-01",
    "priority": "High"
})
```

---

## Create a batch of tasks

```
POST /api/readertasks/batch
```

Creates multiple tasks at once, one per matching container.

```python
tasks = fw.post("/api/readertasks/batch", json={
    "assignees": ["reader@example.com"],        # can be multiple
    "parent_type": "session",                    # "session", "acquisition", or "file"
    "parent_tag_filter": {
        "include": ["tag-to-include"],
        "exclude": ["tag-to-exclude"]
    },
    "viewer": "OHIF_V3",
    "task_type": "R",
    "project_id": project_id,
    "protocol_id": protocol_id,
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "due_date": "2025-06-01",
    "tags": ["batch-1"],
    "filters": [],
    "allow_duplicates": False
})
print(f"Created {len(tasks)} tasks")
```

---

## Dry run a batch (preview without creating)

```
POST /api/readertasks/batch/dryrun
```

Same body as batch create. Returns what *would* be created.

```python
preview = fw.post("/api/readertasks/batch/dryrun", json=batch_payload)
```

---

## Count containers matching a filter

```
POST /api/readertasks/batch/parents
```

```python
count = fw.post("/api/readertasks/batch/parents", json={
    "project_id": project_id,
    "parent_type": "session",
    "include_tags": ["ready-for-read"],
    "exclude_tags": []
})
print(count["matching"])
```

---

## Check for duplicate tasks

```
POST /api/readertasks/batch/duplicates
```

Returns tasks that would be duplicates of the proposed batch.

---

## Clone tasks to a new assignee

```
POST /api/readertasks/batch/clone
```

Creates copies of existing tasks assigned to a new reader. Useful for consensus reads or multi-reader studies.

```python
cloned = fw.post("/api/readertasks/batch/clone", json={
    "project_id": project_id,
    "task_ids": [t._id for t in source_tasks],
    "assignees": ["second-reader@example.com"]
})
print(cloned.clone_ids)
```

---

## Update a task

```
PUT /api/readertasks/{task_id}
```

Modifiable fields: `assignee`, `status`, `form_id`, `viewer`, `viewer_config_id`, `due_date`, `priority`, `tags`, `description`.

```python
task = fw.get(f"/api/readertasks/{task_id}")
task_dict = dict(task)
task_dict["due_date"] = "2025-07-15T00:00:00Z"
task_dict["assignee"] = "reassigned@example.com"
fw.put(f"/api/readertasks/{task_id}", json=task_dict)
```

---

## Delete a task

```
DELETE /api/readertasks/{task_id}
```

```python
fw.delete(f"/api/readertasks/{task_id}")
```

---

## Get annotations for a task

> **V2 / legacy only.** `GET /api/readertasks/{task_id}/annotations` belongs to the legacy
> reader-task store. It 404s for **V3 Tasks Manager** tasks (`/api/tasks/reader`) — verified on
> pp2dg4 22.1.6: it returns `404 Could not find resource reader_task:<id>` for a valid V3 task id,
> and 422s on any non-24-hex id. For V3 annotations use `/api/v3/annotations` (see below).

```
GET /api/readertasks/{task_id}/annotations
```

| Param | Type | Notes |
|-------|------|-------|
| `filter` | string | Filter annotations |
| `sort` | string | Sort order |
| `limit` / `skip` / `page` / `after_id` | — | Pagination |

```python
annotations = fw.get(f"/api/readertasks/{task_id}/annotations").results
for ann in annotations:
    print(ann.data.location, ann.data.toolType)
```

### V3 annotations / measurements (the working path)

For a V3 reader task, pull the reader's drawn measurements from the **v3 annotation store**,
filtering by the reader task's 24-hex `_id`:

```python
task_id = "6a591ae418aa8b7e52831930"   # the reader task _id (== viewer URL taskId=)
anns = fw.get(
    "/api/v3/annotations",
    params={"filter": f"task_id={task_id}", "limit": 100},
).results
for ann in anns:
    for el in ann.elements:              # one per drawn measurement
        print(el.type, el.label, el.metrics)   # e.g. Bidirectional ivh {length, width, units}
```

**`task_id` here is the reader task `_id`** (24-hex, matches `^[0-9a-fA-F]{24}$`) — **not** the
task object's human-readable `task_id` field (e.g. `"R-13-3"`). Passing the `R-13-3` form 422s.

Each annotation carries: `elements[]` (`type`, `label`, `color`, `metrics` with `length` / `width`
/ `units.spatial`), `parents` (project→file, incl. `file.file_id` + `version`), `origin` (the reader),
`state` (`LOCKED` once submitted), stored as a DICOM `SR`. A `Bidirectional` gives two in-plane axes
(length + width) only — no through-plane / slice dimension.

**Do NOT use the v1 `GET /api/annotations` for V3 task annotations.** It won't contain them —
returns `200` with **0 rows** even when filtered by the correct 24-hex `file_ref.file_id`. And it
wants that 24-hex `file_id` specifically: pass a file's storage **uuid** instead and it fails with a
misleading `500 Unexpected error during deserialization` rather than a clean 4xx. (All verified on
pp2dg4 22.1.6, 2026-07-17.)

---

## Get available task types

```
GET /api/readertasks/task_types
```

Returns the dict of valid task type values (currently `"R"` for Reader).

---

## Status / filter value reference

| Field | Valid values |
|-------|-------------|
| `status` | `Todo`, `In_progress`, `Complete` |
| `viewer` | `OHIF`, `Form`, `OHIF_V3` |
| `task_type` | `R` |
| `priority` | `Blocker`, `High`, `Medium`, `Low` |
| `parent_type` | `session`, `acquisition`, `file` |
