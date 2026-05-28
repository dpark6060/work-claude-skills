# API Reference: Read Task Protocols (`/api/read_task_protocols`)

Source: `fw-client` OpenAPI spec, tag `read_task_protocols`.

A protocol joins a Form and a ViewerConfig and is the unit that tasks are created from.
Protocols are scoped to a project via the `parent` field.

---

## List all protocols

```
GET /api/read_task_protocols
```

| Param | Type | Notes |
|-------|------|-------|
| `filter` | string | e.g. `parents.project={project_id}` |
| `include_deleted` | boolean | Include soft-deleted protocols |
| `sort` | string | e.g. `created:desc` |
| `limit` / `skip` / `page` / `after_id` / `exhaustive` | — | Pagination |

```python
protocols = fw.get(
    "/api/read_task_protocols",
    params={"filter": f"parents.project={project_id}"}
).results

for p in protocols:
    print(p.label, p._id, p.form_id, p.viewer_config_id)
```

---

## Get a protocol by ID

```
GET /api/read_task_protocols/{protocol_id}
```

| Param | Type | Notes |
|-------|------|-------|
| `protocol_id` | path | 24-char hex ID |
| `include_deleted` | query | Return even if soft-deleted |

```python
protocol = fw.get(f"/api/read_task_protocols/{protocol_id}")
print(protocol.label, protocol.form_id, protocol.viewer_config_id)
```

---

## Create a protocol

```
POST /api/read_task_protocols
```

Body: `label` (string, required), `description` (string), `form_id` (string), `viewer_config_id` (string), `parent` (object: `{type: "project", id: project_id}`).

```python
protocol = fw.post("/api/read_task_protocols", json={
    "label": "pet-visual-read-v2",
    "description": "PET amyloid visual read protocol, version 2",
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "parent": {"type": "project", "id": project_id}
})
protocol_id = protocol._id
```

---

## Update a protocol

```
PUT /api/read_task_protocols/{protocol_id}
```

Same body shape as create. Used to update label, description, or swap in a new form/viewer config.

> **UI note**: The Flywheel UI treats published protocols as immutable and enforces versioning.
> Direct API PUT bypasses this and modifies the protocol in place. Only do this on
> draft/unpublished protocols or when you deliberately want to patch without versioning.

```python
fw.put(f"/api/read_task_protocols/{protocol_id}", json={
    "label": "updated-label",
    "description": "Updated description",
    "form_id": new_form_id,
    "viewer_config_id": viewer_config_id,
    "parent": {"type": "project", "id": project_id}
})
```

---

## Delete a protocol

```
DELETE /api/read_task_protocols/{protocol_id}
```

Soft-deletes the protocol. Tasks already using this protocol are not affected.

```python
fw.delete(f"/api/read_task_protocols/{protocol_id}")
```

---

## Dry run delete (check for impacted tasks)

```
GET /api/read_task_protocols/{protocol_id}/dry_run_delete
```

Returns all Todo or In_progress tasks that would be affected by deleting this protocol.
Run this before deleting to avoid orphaning active tasks.

```python
impacted = fw.get(
    f"/api/read_task_protocols/{protocol_id}/dry_run_delete"
).results
print(f"{len(impacted)} tasks would be affected")
```
