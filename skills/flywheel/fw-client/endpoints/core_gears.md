# Flywheel Core API (/api/) — gears

Service: `core`  |  Tag: `gears`  |  Generated from OpenAPI spec.

## `GET /api/gears`

**List all gears**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | query | no | `string` |  |
| `all_versions` | query | no | `boolean` | return all versions of each gear |
| `include_invalid` | query | no | `boolean` | return gears with the 'invalid' flag set |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `GET /api/gears/my-tickets`

**Retrieve all gear tickets for the current user**

---

## `POST /api/gears/prepare-add`

**Prepare a gear upload**

**Request Body** *(required)*
`application/json`: object(category: enum(analysis | converter | utility | classifier | qa), gear: object, exchange: object, created: string(date-time), modified: string(date-time), ...)

---

## `POST /api/gears/save`

**Report the result of a gear upload and save the ticket**

**Request Body** *(required)*
`application/json`: object(ticket: string, repo: string, pointer: string)

---

## `GET /api/gears/temp/{gear_id}`

**Download**

get jobs.handlers.GearHandlers.download

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |

---

## `GET /api/gears/ticket/{ticket_id}`

**Retrieve a specific gear ticket**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `ticket_id` | path | yes | `string` |  |

---

## `DELETE /api/gears/{gear_id}` *(deprecated)*

**Delete a gear (not recommended)**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` | Id of the gear to interact with |

---

## `GET /api/gears/{gear_id}`

**Retrieve details about a specific gear**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |

---

## `GET /api/gears/{gear_id}/context/{container_name}/{container_id}`

**Get context values for the given gear and container.**

Ref: https://github.com/flywheel-io/gears/tree/master/spec#contextual-values

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |
| `container_name` | path | yes | `string` |  |
| `container_id` | path | yes | `string` |  |

---

## `POST /api/gears/{gear_id}/disable`

**Disable**

post jobs.handlers.GearHandlers.disable

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |

---

## `POST /api/gears/{gear_id}/enable`

**Enable**

post jobs.handlers.GearHandlers.enable

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |

---

## `GET /api/gears/{gear_id}/invocation`

**Get a schema for invoking a gear**

Get a schema for invoking a gear.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` |  |

---

## `GET /api/gears/{gear_id}/suggest/{container_name}/{container_id}`

**Get files with input suggestions, parent containers, and child containers for the given container.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_id` | path | yes | `string` | Id of the gear to interact with |
| `container_name` | path | yes | `string` | Type of the container to interact with |
| `container_id` | path | yes | `string` | Id of the container to interact with |
| `filter` | query | no | `string` |  |
| `sort` | query | no | `string` |  |
| `limit` | query | no | `integer` |  |
| `skip` | query | no | `integer` |  |
| `page` | query | no | `integer` |  |
| `include` | query | no | `array[string]` | Include only "children" or "files" |
| `collection` | query | no | `string` | Get suggestions for a collection |

---

## `POST /api/gears/{gear_name}`

**Create or update a gear.**

If no existing gear is found, one will be created
Otherwise, the specified gear will be updated

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` | Name of the gear to interact with |

**Request Body** *(required)*
`application/json`: object(category: enum(analysis | converter | utility | classifier | qa), gear: object, exchange: object, created: string(date-time), modified: string(date-time), ...)

---

## `DELETE /api/gears/{gear_name}/permissions`

**Delete permissions of the given gear**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` |  |

---

## `PUT /api/gears/{gear_name}/permissions`

**Replace permissions for the given gear**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` | Name of the gear to interact with |

**Request Body** *(required)*
`application/json`: object(users: array[string], projects: array[string])

---

## `PUT /api/gears/{gear_name}/permissions/{permission_type}`

**Add an individual permission to the given gear**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` | Name of the gear to interact with |
| `permission_type` | path | yes | `enum(projects | users)` |  |

**Request Body** *(required)*
`application/json`: object(id: string)

---

## `DELETE /api/gears/{gear_name}/permissions/{permission_type}/{permission_id}`

**Delete an individual permission of the given gear**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` |  |
| `permission_type` | path | yes | `enum(projects | users)` |  |
| `permission_id` | path | yes | `string` |  |

---

## `GET /api/gears/{gear_name}/series`

**Get gear series.**

Gets the series for the gear by its name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` |  |

---

## `PUT /api/gears/{gear_name}/series`

**Update a gear series**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear_name` | path | yes | `string` | Name of the gear series to modify |

**Request Body** *(required)*
`application/json`: object(is_restricted: boolean)

---
