# Flywheel Transfer API (/xfer/) — Rule Sets

Service: `xfer`  |  Tag: `Rule Sets`  |  Generated from OpenAPI spec.

## `GET /xfer/rule-sets`

**List the available rule sets**

List the available rule sets.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `all` | query | no | `any` |  |
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/rule-sets`

**Create a new rule set**

Create a new rule set.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(name: string, description: any, refs: object, type: enum(import | export), yaml: string, ...)

---

## `GET /xfer/rule-sets/schema`

**Get JSON schemas for rule set spec validation**

Get JSON schemas for rule set spec validation.

---

## `GET /xfer/rule-sets/{rule_set_id}`

**Get a rule set by ID**

Get a rule set by ID.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_set_id` | path | yes | `string` |  |
| `join` | query | no | `array[string]` | Join additional related data using the given `<field>`.<br/> Multiple fields can be passed using comma (`,`) as a separa |
| `authorization` | header | no | `string` |  |

---

## `PATCH /xfer/rule-sets/{rule_set_id}`

**Partially update a rule set and create a new version marked as .latest**

Partially update a rule set and create a new version marked as .latest.

If the payload contains .refs, ref changes are applied on all versions.
If the payload only contains .refs and/or .default, no new version is created.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_set_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(name: any, description: any, refs: any, type: any, yaml: any, ...)

---

## `POST /xfer/rule-sets/{rule_set_id}/archive`

**Archive a rule set and all its versions**

Archive a rule set and all its versions.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_set_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/rule-sets/{rule_set_id}/restore`

**Restore a archived rule set and all its versions**

Restore a archived rule set and all its versions.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_set_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---
