# Flywheel Transfer API (/xfer/) — Connectors

Service: `xfer`  |  Tag: `Connectors`  |  Generated from OpenAPI spec.

## `GET /xfer/connectors`

**List the registered connectors**

List the registered connectors.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> **Filterable fields:** - `disabled`  **Filter operators:**  |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `PUT /xfer/connectors/self/info`

**Set connector info like version and fs-mounts**

Set connector info like version and fs-mounts.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(version: any, fs_mounts: any, aws_role_arn: any, azure_tenant_id: any, azure_client_id: any, ...)

---

## `GET /xfer/connectors/{connector_id}`

**Retrieve a connector by id**

Retrieve a connector by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `connector_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---
