---
type: API Endpoint Schema
title: Core API — Roles
description: Flywheel Core API (/api/) endpoint schemas covering site roles.
tags: [flywheel, core-api, roles]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — roles

Service: `core`  |  Tag: `roles`  |  Generated from OpenAPI spec.

## `GET /api/roles`

**Get list of all roles**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/roles`

**Add a new role**

**Request Body** *(required)*
`application/json`: object(label: string, actions: array[enum(containers_view_metadata | containers_create_hierarchy | containers_modify_metadata | containers_delete_hierarchy | containers_delete_project | copy_by_reference | analyses_view_metadata | analyses_create_sdk | ...)])

---

## `GET /api/roles/actions`

**Get Actions**

---

## `DELETE /api/roles/{role_id}`

**Delete the role**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `role_id` | path | yes | `string` | The ID of the role |

---

## `GET /api/roles/{role_id}`

**Return the role identified by the RoleId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `role_id` | path | yes | `string` | The ID of the role |

---

## `PUT /api/roles/{role_id}`

**Update the role identified by RoleId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `role_id` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(label: string, actions: array[enum(containers_view_metadata | containers_create_hierarchy | containers_modify_metadata | containers_delete_hierarchy | containers_delete_project | copy_by_reference | analyses_view_metadata | analyses_create_sdk | ...)])

---
