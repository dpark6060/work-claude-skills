---
name: fw-reader-tasks
description: >
  Use this skill for any task involving Flywheel Reader Tasks (also called Task-Based Workflows
  or Tasks Manager). Trigger on questions or requests about: creating or modifying read task
  protocols, building or editing form JSON (field types, required fields, conditional/branching
  logic), creating or managing tasks and assignments, retrieving form responses or annotations,
  working with staffing pools, cloning tasks, reporting on task completion, compliance /
  21 CFR Part 11 requirements, or anything involving /api/readertasks, /api/read_task_protocols,
  /api/forms, /api/formresponses, or /api/viewerconfigs. Also use this skill when a client
  asks "can Flywheel do X with reader tasks?" or wants to understand reader task capabilities
  and limitations. Also triggers when user asks how to assign readers, set up blind reads,
  manage reading workflows, or questions about reader study infrastructure — even if they
  don't say "reader task" explicitly.
  MANDATORY TRIGGERS: reader task, read task, reading protocol, task protocol, OHIF,
  form JSON, task assignment, form response, annotation, reader study, 21 CFR Part 11,
  staffing pool, /api/readertasks, /api/read_task_protocols, /api/forms
---

# Reader Tasks Skill

## Before Starting

Read and **summarize** (don't just scan) `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`.
Summarizing forces you to internalize what has and hasn't worked in previous runs.

## After Finishing

If this session produced anything worth capturing, append to the relevant file:
- `.learnings/LEARNINGS.md` — a non-obvious API behavior, version quirk, or workflow adjustment
- `.learnings/ERRORS.md` — a failure, wrong assumption, or undocumented gotcha and how it was fixed

Don't write an entry if nothing went wrong and nothing surprising happened.

---

## ⚡ Version Routing — READ THIS FIRST

Flywheel has **two incompatible** reader task systems. Determine which version you're
working with before doing anything else:

### How to Identify the Version

| Signal | Version |
|--------|---------|
| Top-level key `form.fields` in form JSON | **V3 (Tasks Manager)** |
| Top-level key `studyForm.components` in form JSON | **V2 (Legacy)** |
| `viewer: "OHIF_V3"` in task or form | **V3** |
| `viewer: "OHIF"` in task or form | **V2** |
| Mentions Tasks Manager, staffing pools, e-signatures, completion tags | Likely **V3** |
| Mentions formio, Viewer Protocol, `validate.required` | Likely **V2** |
| Client says "legacy" | **V2** |
| New project / greenfield | **V3** (always recommend V3 for new work) |

### Version-Specific References

Once you know the version, load the correct references:

**For V3 work → read:**
- `references/v3/form-schema-v3.md` — field types, `showWhen`, `requiredWhenVisible`, validation, e-signature config, completion tags
- `references/v3/viewer-config-v3.md` — OHIF_V3 viewer settings, measurement labels, file browser

**For V2 work → read:**
- `references/v2/form-schema-v2.md` — formio components, `conditional.json`, the `required` gotcha, `info` type, hidden field behavior
- `references/v2/viewer-config-v2.md` — OHIF viewer settings, overlays, hanging protocols, hotkeys, toolbar

**For API work (either version) → read:**
- `references/common/api-reader-tasks.md` — all `/api/readertasks` endpoints
- `references/common/api-protocols.md` — all `/api/read_task_protocols` endpoints
- `references/common/api-forms.md` — `/api/forms`, `/api/formresponses`, `/api/viewerconfigs`

**If the version is unclear**, ask the user. If you have the form JSON, check the top-level
key. If you have a task object, check the `viewer` field.

---

## What Are Reader Tasks?

Reader Tasks (also called "Task-Based Workflows" or "Tasks Manager") are structured review
workflows for clinical trials and reader studies. They allow a team to assign radiologists
(or other readers) to review imaging data, fill out a structured form, optionally draw
annotations, and sign off — all with full audit trails.

**Core use cases:** PET/MRI/CT clinical reads, multi-reader blinded studies, guided annotation
workflows, 21 CFR Part 11–compliant data collection.

---

## The Four Objects to Understand

Reader tasks are built from four linked objects. Getting this model right prevents most
confusion:

```
ViewerConfig ─┐
              ├─→ Protocol ─→ Task (assigned to a user/pool, linked to a container)
Form ─────────┘
```

| Object | API prefix | Role |
|--------|-----------|------|
| **Form** | `/api/forms` | Defines the questions a reader answers. Contains the JSON field schema. |
| **ViewerConfig** | `/api/viewerconfigs` | Configures the OHIF image viewer (layout, tools, overlays, labels). |
| **Protocol** | `/api/read_task_protocols` | Joins a Form + ViewerConfig. The unit you assign tasks from. |
| **Task** | `/api/readertasks` | One assignment: a reader + a container (session/acquisition/file) + a protocol. |

Form responses land in `/api/formresponses`. Annotations are stored separately and retrieved
via `/api/readertasks/{task_id}/annotations`.

---

## Task Lifecycle (Both Versions)

```
Todo → In_Progress → Complete
  ↘               ↗
       Cancelled
```

- **Todo**: Created, not yet opened.
- **In_Progress**: Opened in viewer; draft auto-saved.
- **Complete**: Submitted — creates an immutable record. Cannot be changed.
- **Cancelled**: Removed from workflow; visible for audit only.

Tasks cannot skip directly from Todo → Complete.

---

## Key Differences Between V2 and V3

| Dimension | V2 (Legacy) | V3 (Tasks Manager) |
|-----------|-------------|---------------------|
| Viewer | OHIF (V2) | OHIF_V3 |
| Form schema | formio — `studyForm.components` | Custom — `form.fields` |
| Required fields | `validate: { required: true }` | `requiredWhenVisible: true` |
| Conditional logic | `conditional.json` | `showWhen` |
| Multi-select type | `selectboxes` | `checkboxes` |
| Options key | `values` | `options` |
| E-signatures | Not validated | MFA-verified, 21 CFR Part 11 |
| Protocol versioning | Manual (duplicate + edit) | Built-in (immutable, auto-versioned) |
| Validated Instance | Not compatible | Compatible |
| Staffing pools | Not supported | Supported |
| Completion tags | Not supported | Supported |
| Task reports | API only | Built-in CSV reports |
| Metadata display | `info` field type | `paragraph` / viewer overlays |

**V2 and V3 are not compatible.** Existing V2 tasks, annotations, and history cannot be
migrated to V3. Migration means starting fresh.

---

## Common Workflows & Code Patterns

Assumes `fw` is an initialized `FWClient`. See the `fw-client` skill for client setup.

### Look up a project ID

```python
result = fw.post("/api/lookup", json={"path": ["group_label", "project_label"]})
project_id = result._id
```

### List protocols for a project

```python
protocols = fw.get(
    "/api/read_task_protocols",
    params={"filter": f"parents.project={project_id}"}
).results
```

### Create a form + viewer config + protocol (V3)

```python
# 1. Create the form
form = fw.post("/api/forms", json={
    "viewer": "OHIF_V3",
    "parent": {"type": "project", "id": project_id},
    "form": {
        "title": "My Study Form",
        "description": "...",
        "defaults": {},
        "fields": [ ... ]   # see references/v3/form-schema-v3.md
    }
})
form_id = form._id

# 2. Create the viewer config
vc = fw.post("/api/viewerconfigs", json={
    "name": "My Viewer Config",
    "viewer": "OHIF_V3",
    "config": { "showStudyList": False, ... }
})
viewer_config_id = vc._id

# 3. Create the protocol
protocol = fw.post("/api/read_task_protocols", json={
    "label": "my-protocol-v1",
    "description": "Initial version",
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "parent": {"type": "project", "id": project_id}
})
protocol_id = protocol._id
```

### Create a form + viewer config + protocol (V2)

```python
# Same API endpoints — only the JSON content and viewer enum differ
form = fw.post("/api/forms", json={
    "viewer": "OHIF",           # "OHIF" for V2, not "OHIF_V3"
    "parent": {"type": "project", "id": project_id},
    "studyForm": {
        "components": [ ... ]   # see references/v2/form-schema-v2.md
    }
})
form_id = form._id

vc = fw.post("/api/viewerconfigs", json={
    "name": "My Viewer Config",
    "viewer": "OHIF",
    "config": { ... }           # see references/v2/viewer-config-v2.md
})
viewer_config_id = vc._id

# Protocol creation is identical
protocol = fw.post("/api/read_task_protocols", json={
    "label": "my-protocol-v1",
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "parent": {"type": "project", "id": project_id}
})
```

### Create a batch of tasks (both versions)

```python
tasks = fw.post("/api/readertasks/batch", json={
    "assignees": ["reader@example.com"],
    "parent_type": "session",            # "session", "acquisition", or "file"
    "parent_tag_filter": {
        "include": ["ready-for-read"],
        "exclude": []
    },
    "viewer": "OHIF_V3",                 # or "OHIF" for V2
    "task_type": "R",
    "project_id": project_id,
    "protocol_id": protocol_id,
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "due_date": "2025-06-01",
    "tags": [],
    "allow_duplicates": False
})
```

### Clone tasks to a second reader

```python
task_ids = [t._id for t in tasks]
cloned = fw.post("/api/readertasks/batch/clone", json={
    "project_id": project_id,
    "task_ids": task_ids,
    "assignees": ["second-reader@example.com"]
})
```

### Get form responses

```python
# Via form (all responses for a form)
responses = fw.get(f"/api/forms/{form_id}/responses").results

# Via formresponses endpoint (filterable)
responses = fw.get(
    "/api/formresponses",
    params={"filter": f"task_id={task_id}"}
).results

# Response data shape
for r in responses:
    print(r.task_id, r.response_data)  # response_data is a flat dict of field_key → value
```

### Get annotations for a task

```python
annotations = fw.get(f"/api/readertasks/{task_id}/annotations").results
```

---

## Key Limits & Gotchas (Both Versions)

- **Protocols are versioned** — V3 enforces this (immutable once published); V2 allows in-place edits but best practice is to version manually.
- **V2 and V3 are not compatible** — existing assignments, annotations, and history cannot be migrated.
- **Staffing pools** (V3 only) — for bulk tasks, assigning to a pool rather than an individual allows any pool member to claim the task.
- **`allow_duplicates: false`** — prevents creating tasks for containers that already have a task from the same protocol. Usually leave this false.
- **Pagination** — most list endpoints return a `results` array; large result sets need cursor pagination via `after_id` or `exhaustive=true`.
- **Hidden field values are preserved** — in both V2 and V3, when conditional logic hides a field, previously entered values persist in `response_data`. This is intentional (Core 17.3.0 fix). Clearing requires post-processing or a platform change.

---

## Reference Files

Load these when you need full detail. **Pick the version-specific files that match your task.**

### Version-Specific

| File | Version | Content |
|------|---------|---------|
| `references/v3/form-schema-v3.md` | V3 | Field types, `showWhen`, `requiredWhenVisible`, validation, e-sig, completion tags, full example |
| `references/v3/viewer-config-v3.md` | V3 | OHIF_V3 viewer settings, measurement labels, file browser scope |
| `references/v2/form-schema-v2.md` | V2 | Formio components, `conditional.json`, `required` gotcha, `info` type, hidden field behavior, full example |
| `references/v2/viewer-config-v2.md` | V2 | OHIF viewer settings, overlays, hanging protocols, hotkeys, toolbar, layouts |

### Common (Shared API — Both Versions)

| File | Content |
|------|---------|
| `references/common/api-reader-tasks.md` | Full endpoint reference for `/api/readertasks/*` |
| `references/common/api-protocols.md` | Full endpoint reference for `/api/read_task_protocols/*` |
| `references/common/api-forms.md` | Full endpoint reference for `/api/forms/*`, `/api/formresponses/*`, `/api/viewerconfigs/*` |

Also see the `fw-client` skill for `FWClient` instantiation, pagination patterns, error handling,
and other general API patterns.

---

## Legacy Files (Superseded)

The following files in `references/` are from the original combined skill and are superseded
by the version-split files above. They remain for backward compatibility but should not be
used for new work:
- `references/form-schema.md` → replaced by `references/v3/form-schema-v3.md` + `references/v2/form-schema-v2.md`
- `references/api-reader-tasks.md` → replaced by `references/common/api-reader-tasks.md`
- `references/api-protocols.md` → replaced by `references/common/api-protocols.md`
- `references/api-forms.md` → replaced by `references/common/api-forms.md`
