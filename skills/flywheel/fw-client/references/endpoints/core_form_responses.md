---
type: API Endpoint Schema
title: Core API — Form Responses
description: Flywheel Core API (/api/) endpoint schemas covering form responses.
tags: [flywheel, core-api, form-responses]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — form_responses

Service: `core`  |  Tag: `form_responses`  |  Generated from OpenAPI spec.

## `GET /api/formresponses`

**Find all form responses**

Handler to find all form_responses.

Args:
    pagination: Pagination object
    exhaustive:  Get all form_responses; requires admin
    auth_session: Authentication session

Returns:for
    Page: The page output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/formresponses`

**Add a form response**

Handler to create form response

Args:
    form_response_input: The form response to insert
    auth_session: Authentication session

Returns:
    FormResponseOutput: The inserted form response

**Request Body** *(required)*
`application/json`: object(form_id: string, parent: object, task_id: string, response_data: object)

---

## `DELETE /api/formresponses/{form_response_id}`

**Delete a form response**

Handler to delete form_response

Args:
    form_response_id: The form_response_id to delete
    auth_session: Authentication session

Returns:
    DeletedResult: DeletedResult model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_response_id` | path | yes | `string` |  |

---

## `GET /api/formresponses/{form_response_id}`

**Get a form response**

Handler to get form_response

Args:
    form_response_id: The form_response_id to get
    auth_session: Authentication session

Returns:
    FormResponseOutput: The form response output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_response_id` | path | yes | `string` |  |

---

## `PUT /api/formresponses/{form_response_id}`

**Modify a form response**

Handler to modify form_response

Args:
    form_response_id: The form response_id to modify
    form_response_patch: The new form response data
    auth_session: Authentication session

Returns:
    FormResponseOutput: The modified form response output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_response_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(form_id: string, task_id: string, response_data: object)

---
