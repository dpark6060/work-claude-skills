---
type: API Endpoint Schema
title: Core API — Groups
description: Flywheel Core API (/api/) endpoint schemas covering group containers.
tags: [flywheel, core-api, groups]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — groups

Service: `core`  |  Tag: `groups`  |  Generated from OpenAPI spec.

## `DELETE /api/groups`

**Delete multiple groups by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/groups`

**List all groups**

Find all groups.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/groups`

**Add a group**

Create a new group.

**Request Body** *(required)*
`application/json`: object(_id: string, label: string, providers: object, editions: object)

---

## `GET /api/groups/{cid}/settings/deid_profile`

**Get deid_profile for group**

Route for getting deid profile hierarchy

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

---

## `DELETE /api/groups/{cid}/tags`

**Delete multiple tags from a(n) group**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `PATCH /api/groups/{cid}/tags`

**Add multiple tags to a(n) group**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `POST /api/groups/{cid}/tags`

**Add a tag to a(n) group.**

Propagates changes to projects, sessions and acquisitions

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `DELETE /api/groups/{cid}/tags/{value}`

**Delete a tag**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `GET /api/groups/{cid}/tags/{value}`

**Get the value of a tag, by name.**

Get the value of a tag, by name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `PUT /api/groups/{cid}/tags/{value}`

**Rename a tag.**

Rename a tag

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `GET /api/groups/{cid}/{sub_cname}/analyses`

**Get nested analyses from groups**

Get analyses for a container and its children.
Parameters
    container_type                container type
    container_id (str)            container id
    sub_cname (SubContainerType)  sub-container name or "all"
    pagination                    "skip", "limit", "filter", "after_id", "page"
    inflate_job (bool)            add full job to analysis job field
    join_avatars (bool)           add names and avatars to files and notes
    join (JoinType)               multiple uses
Returns
     ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `sub_cname` | path | yes | `enum(acquisitions | all | analyses | collections | groups | projects | sessions | subjects)` |  |
| `inflate_job` | query | no | `boolean` |  |
| `join_avatars` | query | no | `boolean` |  |
| `join` | query | no | `enum(origin)` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `GET /api/groups/{container_id}/settings`

**Get a(n) group settings**

Route for getting settings from a a(n) group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

---

## `PUT /api/groups/{container_id}/settings`

**Modify a(n) group settings**

Route for modifying settings for a a(n) group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(viewer_apps: array[object], deid_profile: any, forms: object, external_routing_id: string)

---

## `DELETE /api/groups/{group_id}`

**Delete group**

Delete a group.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

---

## `GET /api/groups/{group_id}`

**Get group info**

Get a group by ID.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

---

## `PUT /api/groups/{group_id}`

**Update group**

Modify a group.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(label: string, providers: object, editions: object, modified: string(date-time))

---

## `POST /api/groups/{group_id}/permissions`

**Add a permission**

Adds permission to the group

Args:
    group_id: the id of the group
    permission: The access permission
    auth_session: The auth session of the user

Returns
    AccessPermissionOutput: The added permission

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(_id: string, access: enum(ro | rw | admin))

---

## `POST /api/groups/{group_id}/permissions/templates`

**Add a permission template**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `propagate` | query | no | `boolean` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(_id: string, role_ids: array[string])

---

## `DELETE /api/groups/{group_id}/permissions/templates/{user_id}`

**Delete a permission**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |
| `propagate` | query | no | `boolean` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `GET /api/groups/{group_id}/permissions/templates/{user_id}`

**List a user's permissions for this group.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---

## `PUT /api/groups/{group_id}/permissions/templates/{user_id}`

**Update a user's permission for this group.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |
| `propagate` | query | no | `boolean` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(role_ids: array[string])

---

## `DELETE /api/groups/{group_id}/permissions/{user_id}`

**Delete a permission**

Deletes a permission from the group

Args:
    group_id: the id of the group
    user_id: The id of the user
    auth_session: The auth session of the user

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---

## `GET /api/groups/{group_id}/permissions/{user_id}`

**List a user's permissions for this group.**

List a user's permissions for this group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---

## `PUT /api/groups/{group_id}/permissions/{user_id}`

**Update a user's permission for this group.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(access: enum(ro | rw | admin))

---

## `GET /api/groups/{group_id}/projects`

**Get all projects in a group**

Get projects for a group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `GET /api/groups/{group_id}/roles`

**Get list of group roles**

Gets all group roles

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

---

## `POST /api/groups/{group_id}/roles`

**Add a role to the pool of roles in a group**

Add a group role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(_id: string)

---

## `DELETE /api/groups/{group_id}/roles/{role_id}`

**Remove the role from the group**

Delete a group role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `role_id` | path | yes | `string` |  |

---

## `GET /api/groups/{group_id}/roles/{role_id}`

**Return the role identified by the RoleId**

Get a group role.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `group_id` | path | yes | `string` |  |
| `role_id` | path | yes | `string` |  |

---
