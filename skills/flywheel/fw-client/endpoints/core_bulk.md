# Flywheel Core API (/api/) — bulk

Service: `core`  |  Tag: `bulk`  |  Generated from OpenAPI spec.

## `POST /api/bulk/add/tags`

**Add Tags**

Adds a bulk list of tags to a list of containers

**Request Body** *(required)*
`application/json`: object(containers: array[object], tags: array[string])

---

## `POST /api/bulk/copy/{cname}` *(deprecated)*

**Copy**

See '/move/sessions'

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cname` | path | yes | `string` |  |

---

## `POST /api/bulk/delete/readertasks`

**Delete Reader Task Bulk**

Router to delete reader_task

Args:
    request: Request object
    auth_session: Authentication session
    delete_reader_tasks: BulkReaderTaskDelete object

Returns:
    BulkOutputErrors: The bulk output errors

**Request Body** *(required)*
`application/json`: object(task_ids: array[string])

---

## `POST /api/bulk/delete/{cname}` *(deprecated)*

**Delete**

See '/move/sessions'

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cname` | path | yes | `string` |  |

---

## `POST /api/bulk/move/acquisitions`

**Move Acquisitions**

**Request Body** *(required)*
`application/json`: object(destination_container_type: enum(sessions | subjects | projects), sources: array[string], destinations: array[string], conflict_mode: enum(skip | move | dry), remove_source: boolean)

---

## `POST /api/bulk/move/sessions`

**Perform a bulk move of sessions to either a subject or project**

Move sessions

**Request Body** *(required)*
`application/json`: object(destination_container_type: enum(sessions | subjects | projects), sources: array[string], destinations: array[string], conflict_mode: enum(skip | move | dry), remove_source: boolean)

---

## `POST /api/bulk/move/subjects` *(deprecated)*

**Move Subjects**

(post handlers.bulkhandler.bulk)

**Request Body** *(required)*
`application/json`: object(destination_container_type: enum(sessions | subjects | projects), sources: array[string], destinations: array[string], conflict_mode: enum(skip | move | dry), remove_source: boolean)

---

## `POST /api/bulk/remove/tags`

**Remove Tags**

Removes a list of tags from a list of containers

**Request Body** *(required)*
`application/json`: object(containers: array[object], tags: array[string])

---
