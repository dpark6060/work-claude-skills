# Flywheel Core API (/api/) — {container_type}

Service: `core`  |  Tag: `{container_type}`  |  Generated from OpenAPI spec.

## `PATCH /api/{container_type}/info/cleanup/{path}`

**Remove a custom field from all applicable containers**

Clean up a custom field from all containers of a type.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_type` | path | yes | `enum(acquisitions | analyses | collections | containers | projects | sessions | subjects | files)` |  |
| `path` | path | yes | `string` | The dot-separated custom field name to delete |

---
