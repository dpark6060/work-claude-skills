# Flywheel Core API (/api/) — jupyterlab_servers

Service: `core`  |  Tag: `jupyterlab_servers`  |  Generated from OpenAPI spec.

## `GET /api/jupyterlab_servers`

**Find All**

Find all jupyterlab servers.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | query | yes | `string` |  |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/jupyterlab_servers`

**Create Jupyterlab Server**

Create jupyterlab server.

**Request Body** *(required)*
`application/json`: object(project_id: string, label: string, external_storage_id: string)

---

## `GET /api/jupyterlab_servers/server_options`

**Get Server Options**

Get list of server options for jupyterlab servers.

---

## `POST /api/jupyterlab_servers/server_options`

**Create Server Options**

Create a server option for jupyterlab server.

**Request Body** *(required)*
`application/json`: object(name: string, label: string, cpu_guarantee: integer, cpu_limit: integer, mem_guarantee: integer, ...)

---

## `DELETE /api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}`

**Delete Server Options**

Delete server options by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_option_id` | path | yes | `string` |  |

---

## `GET /api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}`

**Get Server Option By Id**

Find a server option by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_option_id` | path | yes | `string` |  |

---

## `PUT /api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}`

**Modify Server Options**

Modify server options.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_option_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(name: string, label: string, cpu_guarantee: integer, cpu_limit: integer, mem_guarantee: integer, ...)

---

## `GET /api/jupyterlab_servers/status`

**Get Status By Ids**

Get jupyterlab server status by ids.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `id` | query | yes | `array[string]` |  |

---

## `DELETE /api/jupyterlab_servers/{jupyterlab_server_id}`

**Delete**

Delete jupyterlab server by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

---

## `GET /api/jupyterlab_servers/{jupyterlab_server_id}`

**Get jupyterlab server**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

---

## `PUT /api/jupyterlab_servers/{jupyterlab_server_id}`

**Update a jupyterlab server**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(label: string, last_modified_by: object, deleted: string(date-time), external_storage_id: string, latest_version: integer)

---

## `GET /api/jupyterlab_servers/{jupyterlab_server_id}/data`

**Download Jupyterlab Server Data**

Upload jupyterlab server data as a zip file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `view` | query | no | `boolean` |  |
| `ticket_id` | query | no | `string` |  |

---

## `POST /api/jupyterlab_servers/{jupyterlab_server_id}/data`

**Upload Jupyterlab Server Data**

Upload jupyterlab server data as a zip file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(jupyterlab_server_file: string)

---

## `GET /api/jupyterlab_servers/{jupyterlab_server_id}/data/ticket`

**Get Jupyterlab Server Download Ticket**

Upload jupyterlab server data as a zip file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `view` | query | no | `boolean` |  |

---

## `PUT /api/jupyterlab_servers/{jupyterlab_server_id}/start`

**Start By Id**

Start jupyterlab server by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(server_options_id: string)

---

## `PUT /api/jupyterlab_servers/{jupyterlab_server_id}/stop`

**Stop By Id**

Stop jupyterlab server by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |

---

## `GET /api/jupyterlab_servers/{jupyterlab_server_id}/users/{user_id}/system`

**Get Server System Info**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `jupyterlab_server_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---
