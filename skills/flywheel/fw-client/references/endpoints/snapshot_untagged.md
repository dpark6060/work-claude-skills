# Flywheel Snapshot API (/snapshot/) — untagged

Service: `snapshot`  |  Tag: `untagged`  |  Generated from OpenAPI spec.

## `GET /healthz`

**Check Health**

---

## `GET /snapshot/projects/{project_id}/snapshots`

**List Snapshots**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `filter` | query | no | `any` | The filter to apply. (e.g. label=my-label,created>2018-09-22) |
| `sort` | query | no | `any` | The sort fields and order.(e.g. label:asc,created:desc) |
| `limit` | query | no | `any` | The maximum number of entries to return |
| `skip` | query | no | `any` | The number of entries to skip |
| `page` | query | no | `any` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `any` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /snapshot/projects/{project_id}/snapshots`

**Create Snapshot**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `DELETE /snapshot/projects/{project_id}/snapshots/{snapshot_id}`

**Delete Snapshot**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

---

## `GET /snapshot/projects/{project_id}/snapshots/{snapshot_id}`

**Download Snapshot**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

---

## `POST /snapshot/projects/{project_id}/snapshots/{snapshot_id}/access_log`

**Write Access Log**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(origin: object, destination: object)

---

## `GET /snapshot/projects/{project_id}/snapshots/{snapshot_id}/detail`

**Get Snapshot Detail**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

---

## `GET /snapshot/projects/{project_id}/subjects/{snapshot_id}`

**Download Subjects**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

---
