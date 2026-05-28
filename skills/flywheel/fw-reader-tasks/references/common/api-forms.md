# API Reference: Forms, Form Responses & Viewer Configs

Source: `fw-client` OpenAPI spec, tags `forms`, `form_responses`, `viewer_configs`.

---

## Forms (`/api/forms`)

A Form holds the question schema that readers fill out. It is created separately from a
protocol and then linked via `form_id`. One form can be reused across multiple protocols.

### List all forms

```
GET /api/forms
```

| Param | Type | Notes |
|-------|------|-------|
| `filter` | string | e.g. `parents.project={project_id}` |
| `exhaustive` | boolean | Return all (admin) |
| `sort` / `limit` / `skip` / `page` / `after_id` | — | Pagination |

```python
forms = fw.get("/api/forms", params={"filter": f"parents.project={project_id}"}).results
```

### Get a form by ID

```
GET /api/forms/{form_id}
```

```python
form = fw.get(f"/api/forms/{form_id}")
# form.form contains the field schema dict
import json
print(json.dumps(dict(form.form), indent=2))
```

### Create a form

```
POST /api/forms
```

Body: `viewer` (enum: `OHIF | Form | OHIF_V3`), `parent` (object), `form` (object — the field schema).

```python
form = fw.post("/api/forms", json={
    "viewer": "OHIF_V3",
    "parent": {"type": "project", "id": project_id},
    "form": {
        "title": "My Study Form",
        "description": "Reads for study XYZ",
        "defaults": {},
        "fields": [ ... ]   # see form-schema.md
    }
})
form_id = form._id
```

### Update a form

```
PUT /api/forms/{form_id}
```

Same body shape as create. Replaces the entire form definition.

```python
form = fw.get(f"/api/forms/{form_id}")
form_dict = dict(form)
# Modify form_dict["form"]["fields"] as needed
fw.put(f"/api/forms/{form_id}", json=form_dict)
```

### Delete a form

```
DELETE /api/forms/{form_id}
```

### Get all responses for a form

```
GET /api/forms/{form_id}/responses
```

Returns all submitted form responses for this form across all tasks.

```python
responses = fw.get(f"/api/forms/{form_id}/responses").results
for r in responses:
    print(r.task_id, r.response_data)
```

---

## Form Responses (`/api/formresponses`)

Form responses are the submitted answers. Each response links to a `form_id` and `task_id`.

### List all form responses

```
GET /api/formresponses
```

| Param | Type | Notes |
|-------|------|-------|
| `filter` | string | e.g. `task_id={task_id}` or `form_id={form_id}` |
| `exhaustive` | boolean | Admin: return all |
| `sort` / `limit` / `skip` / `page` / `after_id` | — | Pagination |

```python
responses = fw.get(
    "/api/formresponses",
    params={"filter": f"task_id={task_id}"}
).results
```

### Get a specific form response

```
GET /api/formresponses/{form_response_id}
```

```python
resp = fw.get(f"/api/formresponses/{form_response_id}")
print(resp.response_data)   # flat dict: {"field_key": "value", ...}
print(resp.task_id)
print(resp.form_id)
```

### Create a form response (manual submission)

```
POST /api/formresponses
```

Body: `form_id`, `parent` (object), `task_id`, `response_data` (object — flat key/value dict).

```python
resp = fw.post("/api/formresponses", json={
    "form_id": form_id,
    "task_id": task_id,
    "parent": {"type": "project", "id": project_id},
    "response_data": {
        "scan_result": "positive",
        "regions": {"Frontal": True, "Parietal": False}
    }
})
```

### Update a form response

```
PUT /api/formresponses/{form_response_id}
```

Body: `form_id`, `task_id`, `response_data`.

### Delete a form response

```
DELETE /api/formresponses/{form_response_id}
```

### Response data shape

`response_data` is a flat dict of `field_key → value`. Value type depends on field type:

| Field type | Value type | Example |
|------------|-----------|---------|
| radio | string | `"elevated"` |
| dropdown/select | string | `"incongruency"` |
| checkboxes/selectboxes | object (key → bool) | `{"Frontal": true, "Parietal": false}` |
| textfield / text | string | `"Patient had prior history..."` |
| textarea | string | `"Long text..."` |

Only fields that were answered appear. Conditionally hidden fields that were never shown
will have no entry. Fields that were shown but left blank may appear with `null` or `""`.

---

## Viewer Configs (`/api/viewerconfigs`)

A ViewerConfig controls the OHIF viewer appearance: layout, tools, overlays, annotation labels.

### List all viewer configs

```
GET /api/viewerconfigs
```

```python
vcs = fw.get("/api/viewerconfigs", params={"filter": f"parents.project={project_id}"}).results
```

### Get a viewer config

```
GET /api/viewerconfigs/{viewer_config_id}
```

```python
vc = fw.get(f"/api/viewerconfigs/{viewer_config_id}")
```

### Get the raw config dict

```
GET /api/viewerconfigs/{viewer_config_id}/config
```

Returns just the `config` object (the viewer settings JSON).

```python
raw_config = fw.get(f"/api/viewerconfigs/{viewer_config_id}/config")
```

### Create a viewer config

```
POST /api/viewerconfigs
```

Body: `name` (string), `viewer` (enum: `OHIF | Form | OHIF_V3`), `config` (object).

```python
vc = fw.post("/api/viewerconfigs", json={
    "name": "pet-read-viewer",
    "viewer": "OHIF_V3",
    "config": {
        "showStudyList": False,
        "evaluatePerformance": True,
        "enableSegmentationPanel": False,
        "toolbar": {
            "Annotate": {"except": ["Annotate"]},
            "Measure": {"except": ["Length", "Bidirectional", "Angle"]}
        },
        "mouseActions": [
            {"toolName": "Zoom", "button": "middle"},
            {"toolName": "Pan", "button": "right"},
            {"toolName": "Wwwc", "button": "left"},
            {"toolName": "StackScrollMouseWheel", "button": "wheel"}
        ],
        "labels": [
            {"label": "Frontal", "value": "Frontal", "color": "rgba(255,0,0,0.5)"},
            {"label": "Parietal", "value": "Parietal", "color": "rgba(0,255,222,0.5)"}
        ],
        "layouts": [ ... ],
        "overlay": { ... }
    }
})
viewer_config_id = vc._id
```

### Update a viewer config

```
PUT /api/viewerconfigs/{viewer_config_id}
```

Same body as create.

### Delete a viewer config

```
DELETE /api/viewerconfigs/{viewer_config_id}
```
