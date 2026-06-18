# Flywheel Core API (/api/) — devices

Service: `core`  |  Tag: `devices`  |  Generated from OpenAPI spec.

## `GET /api/devices`

**List all devices.**

Requires login.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `join_keys` | query | no | `boolean` | Return device key. Admins only |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/devices`

**Create a new device.**

Will create a new device record together with an api key.
Request must be an admin request.

**Request Body** *(required)*
`application/json`: object(label: string, type: string, storage_config: object)

---

## `GET /api/devices/self`

**Get current device.**

---

## `PUT /api/devices/self`

**Modify a device's type, name, interval, info or set errors.**

Will modify the device record of the device making the request.
Type may only be set once if not already specified at creation.
Request must be a drone request.

**Request Body** *(required)*
`application/json`: object(type: string, version: string, interval: integer, errors: array[string], info: object)

---

## `GET /api/devices/status`

**Get status for all known devices.**

ok - missing - error - unknown

---

## `DELETE /api/devices/{device_id}`

**Delete a device**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `device_id` | path | yes | `string` |  |

---

## `GET /api/devices/{device_id}`

**Get device details**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `device_id` | path | yes | `string` |  |

---

## `PUT /api/devices/{device_id}`

**Update a device**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `device_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(disabled: boolean, storage_config: object)

---

## `POST /api/devices/{device_id}/key`

**Generate device API key**

Regenerate device API key

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `device_id` | path | yes | `string` |  |

**Request Body**
`application/json`: object(label: string, expires_at: string(date-time))

---

## `DELETE /api/devices/{device_id}/key/{key_id}`

**Delete Device Key**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `device_id` | path | yes | `string` |  |
| `key_id` | path | yes | `string` |  |

---
