# Flywheel Transfer API (/xfer/) — Upload

Service: `xfer`  |  Tag: `Upload`  |  Generated from OpenAPI spec.

## `POST /xfer/upload`

**Create upload ticket to upload a file**

Create upload ticket to upload a file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `dry_run` | query | no | `boolean` |  |
| `source` | query | no | `string` |  |
| `uid_scope` | query | no | `any` |  |
| `conflict_strategy` | query | no | `enum(skip | update | force_update | review)` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(project: object, subject: any, session: any, acquisition: any, file: object, ...)

---

## `POST /xfer/upload/finish`

**Finish an upload previously initiated by creating an upload ticket**

Finish an upload previously initiated by creating an upload ticket.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(_id: string, etags: array[string])

---

## `POST /xfer/upload/lookup`

**Lookup project to upload to**

Lookup project to upload to.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(group: any, project: any, session: any, external_routing_id: any)

---
