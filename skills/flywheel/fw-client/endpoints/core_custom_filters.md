# Flywheel Core API (/api/) — custom_filters

Service: `core`  |  Tag: `custom_filters`  |  Generated from OpenAPI spec.

## `GET /api/custom_filters`

**Get all custom filters for user**

Retrieves all custom filters for the authenticated user's origin

Args:
    pagination: Pagination parameters for the query
    auth_session: The user auth session for permission checks

Returns:
    Page[Filter]: A paginated list of custom filters matching the user's origin

Raises:
    BusinessLogicError: when auth session does not have user privilege

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/custom_filters`

**Create a custom filter for user**

Creates a custom filter for the user

Args:
    filter_input: The input model for creating a filter
    auth_session: The user auth session for permission Checks

Returns:
    Filter: A customer saved filter

Raises:
    BusinessLogicError: when auth session does not have user set

**Request Body** *(required)*
`application/json`: object(filter: any, view: enum(tasks), label: string)

---

## `DELETE /api/custom_filters/{custom_filter_id}`

**Delete a custom filter for user**

Deletes a custom filter for the authenticated user

Args:
    custom_filter_id: The ID of the filter to delete
    auth_session: The user auth session for permission checks

Returns:
    DeletedResult: Result indicating the number of deleted filters

Raises:
    BusinessLogicError: when auth session does not have user privilege
    ResourceNotFound: when the filter doesn't exist
    PermissionError: when the filter doesn't belong to the user's origin

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `custom_filter_id` | path | yes | `string` |  |

---

## `PUT /api/custom_filters/{custom_filter_id}`

**Update a custom filter for user**

Updates an existing custom filter

Args:
    custom_filter_id: The ID of the filter to update
    filter_input: The input model for updating a filter
    auth_session: The user auth session for permission checks

Returns:
    Filter: The updated custom filter

Raises:
    BusinessLogicError: when auth session does not have user privilege or origin mismatch

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `custom_filter_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(filter: any, view: enum(tasks), label: string)

---
