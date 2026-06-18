# Flywheel Core API (/api/) — storage

Service: `core`  |  Tag: `storage`  |  Generated from OpenAPI spec.

## `POST /api/storage/files`

**Upload a file directly to storage**

Uploads a file to object storage and creates a record in the storage collection

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | query | yes | `string` |  |
| `origin_type` | query | yes | `enum(user | user_workspace | device | job | system | unknown | gear_rule | task)` |  |
| `origin_id` | query | no | `string` |  |
| `signed_url` | query | no | `boolean` |  |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `content-type` | header | no | `string` |  |

---

## `DELETE /api/storage/files/{storage_file_id}`

**Delete a file from storage**

Delete a file from storage.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_file_id` | path | yes | `string` |  |
| `ignore_storage_errors` | query | no | `boolean` |  |

---

## `GET /api/storage/files/{storage_file_id}`

**Download a file from storage**

Download a file from storage.

This endpoint should either redirect to a signed url, or stream the results.
It does not support: Zip Member Access, Tickets, Range Reads

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_file_id` | path | yes | `string` |  |
| `filename` | query | no | `string` |  |
| `ticket` | query | no | `string` |  |
| `content_type` | query | no | `string` |  |
| `content_encoding` | query | no | `string` |  |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `POST /api/storage/files/{storage_file_id}/ticket`

**Create a ticket for unauthenticated download**

Create a ticket to download a file from storage.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `storage_file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(filename: string, origin: object)

---
