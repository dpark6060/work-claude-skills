# Flywheel Core API (/api/) — forms

Service: `core`  |  Tag: `forms`  |  Generated from OpenAPI spec.

## `GET /api/forms`

**Get all forms**

Route to get all forms

Args:
    request: Request object
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    exhaustive: Return full list if correct permissions
    auth_session: Authentication session

Returns:
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

## `POST /api/forms`

**Create**

Router to create form

Args:
    request: Request object
    form_input: The input body for creating a form
    auth_session: Authentication session

Returns:
    FormOutput: The created form

**Request Body** *(required)*
`application/json`: object(viewer: enum(OHIF | Form | OHIF_V3), parent: object, form: object)

---

## `DELETE /api/forms/{form_id}`

**Delete**

Route to delete form by id.

Args:
    request: Request object
    form_id: The id of the form to delete
    auth_session: Authentication session

Returns:
    DeletedResult: The DeletedResult object

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_id` | path | yes | `string` | 24-char hex form id |

---

## `GET /api/forms/{form_id}`

**Get By Id**

Route to get form by id.

Args:
    request: Request object
    form_id: The id of the form to get
    auth_session: Authentication session

Returns:
    FormOutput: The form output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_id` | path | yes | `string` | 24-char hex form id |

---

## `PUT /api/forms/{form_id}`

**Modify**

Route to modify form by id.

Args:
    request: Request object
    form_id: The id of the form to modify
    form_modify_input: The form modification input
    auth_session: Authentication session

Returns:
    FormOutput: The form output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_id` | path | yes | `string` | 24-char hex form id |

**Request Body** *(required)*
`application/json`: object(viewer: enum(OHIF | Form | OHIF_V3), parent: object, form: object)

---

## `GET /api/forms/{form_id}/responses`

**Find All Responses By Form Id**

Router to get all form_responses for a form

Args:
    request: Request object
    form_id: The form id to get its responses
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    auth_session: Authentication session

Returns:
    Page:  The page model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `form_id` | path | yes | `string` | 24-char hex form id |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---
