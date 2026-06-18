# Flywheel Core API (/api/) — change_log

Service: `core`  |  Tag: `change_log`  |  Generated from OpenAPI spec.

## `GET /api/changes/{container_type}/{container_id}`

**Get Change Log**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_type` | path | yes | `enum(project | subject | session | acquisition | analysis | file | device | master_subject_code | ...)` |  |
| `container_id` | path | yes | `string` |  |
| `version` | query | no | `integer` | Optional version if retrieving logs for file |

---

## `GET /api/changes/{container_type}/{container_id}/fields/{field}`

**Get change logs by specific field, in reverse chronological order**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_type` | path | yes | `enum(project | subject | session | acquisition | analysis | file | device | master_subject_code | ...)` |  |
| `container_id` | path | yes | `string` |  |
| `field` | path | yes | `string` |  |
| `version` | query | no | `integer` | Optional version if retrieving logs for file |

---
