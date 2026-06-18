# Flywheel Transfer API (/xfer/) — Schedules

Service: `xfer`  |  Tag: `Schedules`  |  Generated from OpenAPI spec.

## `GET /xfer/schedules`

**List schedules**

List schedules.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/schedules/{schedule_id}`

**Retrieve a schedule**

Retrieve a schedule.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `schedule_id` | path | yes | `string` |  |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `authorization` | header | no | `string` |  |

---

## `PATCH /xfer/schedules/{schedule_id}`

**Update a schedule**

Update a schedule.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `schedule_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(active: any, start: any, end: any, cron: any)

---
