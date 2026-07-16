---
type: API Endpoint Schema
title: Core API — Users
description: Flywheel Core API (/api/) endpoint schemas covering user accounts.
tags: [flywheel, core-api, users]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — users

Service: `core`  |  Tag: `users`  |  Generated from OpenAPI spec.

## `GET /api/users`

**Return a list of all users**

Gets all users with pagination

Args:

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

## `POST /api/users`

**Add a new user**

**Request Body** *(required)*
`application/json`: object(_id: string, firstname: string, lastname: string, email: string, password: string, ...)

---

## `GET /api/users/self`

**Get information about the current user**

Gets the current user

Args:
    auth_session (AuthSession): session from incoming request
Returns:
    CurrentUserOutput: Pydantic model for client side user data

---

## `GET /api/users/self/avatar`

**Get the avatar of the current user**

Gets avatar of current user

Args:
    auth_session (AuthSession): session from incoming request
Returns:
    str: url of avatar

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `default` | query | no | `string` |  |

---

## `GET /api/users/self/info`

**Get info of the current user**

Gets user info fields.

Args:
    fields (str): csv of arbitrary keys to look for in user info
    auth_session (AuthSession): session from incoming request
Returns:
    dict: arbitrary data matching the provided csv values

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `fields` | query | no | `string` | Get only the specified fields from user's info. Accept multiple fields separated by comma. |

---

## `PATCH /api/users/self/info`

**Update or replace info for the current user.**

Modifies user info fields

Args:
    info (Info): Model representing arbitrary data
    auth_session (AuthSession): session from incoming request
Returns:
    None

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `POST /api/users/self/info` *(deprecated)*

**Update or replace info for the current user.**

Modifies user info fields

Args:
    info (Info): Model representing arbitrary data
    auth_session (AuthSession): session from incoming request
Returns:
    None

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `GET /api/users/self/jobs`

**Return list of jobs created by the current user**

Gets jobs assigned to user with optional gear name regex

Args:
    gear_name (str): name of gear to filter by
    auth_session (AuthSession): session from incoming request
Returns:
    list: List of jobs linked to the user

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `gear` | query | no | `string` | Gear name. Get only the jobs which are related to a specific gear. |
| `exhaustive` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/users/self/key`

**Generates user api key**

Generate user api key for the current user.

**Request Body** *(required)*
`application/json`: object(label: string, expires_at: string(date-time))

---

## `DELETE /api/users/self/key/{id_}`

**Delete User Api Key**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `id_` | path | yes | `string` |  |

---

## `DELETE /api/users/self/mfa-setups`

**Delete Mfa Setup**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `x-mfa-code` | header | yes | `string` |  |

---

## `GET /api/users/self/mfa-setups`

**Get Mfa Setups**

---

## `PATCH /api/users/self/mfa-setups`

**Update Mfa Setup**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `x-mfa-code` | header | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(channel: enum(sms | call | totp), verified: boolean, phone_number: string)

---

## `POST /api/users/self/mfa-setups`

**Create Mfa Setup**

**Request Body** *(required)*
`application/json`: object(channel: enum(sms | call | totp), verified: boolean, phone_number: string)

---

## `POST /api/users/self/mfa-verifications`

**Create Mfa Verification**

---

## `PUT /api/users/self/preferences`

**Change user preferences**

**Request Body** *(required)*
`application/json`: object(job_log_columns: array[enum(gear_name | user | group | project | subject | session | created | completed | ...)], tasks_columns_disabled: array[enum(project | task_id | task_type | container | assignee | creator | created | due | ...)], task_manager_columns: array[enum(task_id | created | status | priority | due_date | assignee | project | protocol_label | ...)], task_manager_column_sort_order: array[any])

---

## `POST /api/users/self/visited_projects/{project_id}`

**Add project id to list of users recently visited projects**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` | Id of the project to add to recently visited list for current user |

---

## `PUT /api/users/sync/{cid}`

**Sync a center user to enterprise (Sync service use ONLY)**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(email: string, given_name: string, family_name: string, disabled: boolean, auth0id: string, ...)

---

## `DELETE /api/users/{UserId}`

**Delete a user**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `UserId` | path | yes | `string` |  |

---

## `PUT /api/users/{uid}`

**Update the specified user**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `clear_permissions` | query | no | `boolean` |  |

**Request Body** *(required)*
`application/json`: object(firstname: string, lastname: string, email: string, avatars: object, avatar: string, ...)

---

## `GET /api/users/{uid}/acquisitions`

**Get all acquisitions that belong to the given user.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `GET /api/users/{uid}/groups`

**List all groups the specified user is a member of**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `GET /api/users/{uid}/projects`

**Get all projects that belong to the given user.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/users/{uid}/reset-registration` *(deprecated)*

**Reset User Registration**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |

---

## `GET /api/users/{uid}/sessions`

**Get all sessions that belong to the given user.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `GET /api/users/{uid}/{cname}` *(deprecated)*

**Get All For User**

Get all for user

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `uid` | path | yes | `string` |  |
| `cname` | path | yes | `string` |  |

---

## `GET /api/users/{user_id}`

**Get information about the specified user**

Get user by id

Args:
    uid (str): string matching uid pattern
Returns:
    UserOutput: Pydantic model for sending data to client

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `user_id` | path | yes | `string` |  |
| `include_deleted` | query | no | `boolean` |  |

---

## `GET /api/users/{user_id}/avatar`

**Get the avatar of the specified user**

gets avatar of user and redirects to it

Args:
    user_id (str): user id matching user_id regex
Returns:
    RedirectResponse: redirects user to avatar
Raises (ResourceNotFound): Raises 404 if no user avatar

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `user_id` | path | yes | `string` |  |
| `default` | query | no | `string` |  |

---

## `GET /api/users/{user_id}/collections`

**Get all collections that belong to the given user.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `user_id` | path | yes | `string` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---
