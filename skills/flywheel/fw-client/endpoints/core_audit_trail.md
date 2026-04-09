# Flywheel Core API (/api/) — audit_trail

Service: `core`  |  Tag: `audit_trail`  |  Generated from OpenAPI spec.

## `GET /api/audit-trail/reports`

**List Audit Trail Reports**

List Audit Trail Reports.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/audit-trail/reports`

**Starts generation of an Audit Trail Report**

Start generation of a new Audit Trail Report.

**Request Body** *(required)*
`application/json`: object(project_id: string, subject_ids: array[string], label: string, status: enum(pending | complete | failed | in_progress | canceled), created: string(date-time))

---

## `DELETE /api/audit-trail/reports/{report_id}`

**Deletes an Audit Trail Report**

Delete an Audit Trail Report

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `report_id` | path | yes | `string` |  |

---

## `PATCH /api/audit-trail/reports/{report_id}`

**Modify an Audit Trail Report**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `report_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(status: enum(pending | complete | failed | in_progress | canceled))

---

## `GET /api/audit-trail/reports/{report_id}/csv`

**Download Audit Trail Report**

Download Audit Trail Reports

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `report_id` | path | yes | `string` |  |

---
