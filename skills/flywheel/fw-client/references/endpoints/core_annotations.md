---
type: API Endpoint Schema
title: Core API — Annotations
description: Flywheel Core API (/api/) endpoint schemas covering image and file annotations.
tags: [flywheel, core-api, annotations]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — annotations

Service: `core`  |  Tag: `annotations`  |  Generated from OpenAPI spec.

## `GET /api/annotations`

**Get all annotations associated with a file**

Handler to find all annotations associated with a file.

Args:
    pagination: Pagination object
    exhaustive:  Get all annotations; requires admin
    auth_session: Authentication session

Returns:
    Page: The page output

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

## `POST /api/annotations`

**Add an annotation**

Create annotation handler

Args:
    annotation_input: The input body for creating a annotation
    auth_session: Authentication session

Returns:
    Annotation: The created annotation

**Request Body** *(required)*
`application/json`: object(file_id: string, task_id: string, data: any, viewer_format: enum(ohif_react | ohif_v3 | ohif_unknown))

---

## `GET /api/annotations/counts`

**Get annotation count**

Gets annotation counts.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | query | yes | `string` |  |

---

## `DELETE /api/annotations/{annotation_id}`

**Delete an annotation**

Handler to delete annotation by id.

Args:
    annotation_id: The id of the annotation to delete
    auth_session: Authentication session

Returns:
    DeletedResult: The DeletedResult object

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` | 24-char hex annotation id |

---

## `GET /api/annotations/{annotation_id}`

**Get annotation by ID**

Get annotation by id handler.

Args:
    annotation_id: The id of the annotation to get
    auth_session: Authentication session

Returns:
    AnnotationOutput: The annotation output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` | 24-char hex annotation id |

---

## `PUT /api/annotations/{annotation_id}`

**Modify an annotation**

Handler to modify annotation by id.

Args:
    annotation_id: The id of the annotation to modify
    annotation_modify_input: The annotation modification input
    auth_session: Authentication session

Returns:
    AnnotationOutput: The annotation output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` | 24-char hex annotation id |

**Request Body** *(required)*
`application/json`: object(data: any)

---

## `GET /api/v3/annotations`

**Get all annotations**

Route to get all annotations

Args:
    request: Request object
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    join_origin: Whether or not to join origins, default is false
    exhaustive: Return full list if correct permissions
    exclude_deleted: if True, exclude deleted annotations fr ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `join_origin` | query | no | `boolean` |  |
| `exhaustive` | query | no | `boolean` |  |
| `exclude_deleted` | query | no | `boolean` |  |
| `exclude_replaced` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/v3/annotations`

**Create a new Annotation**

Router to create annotation

**Request Body** *(required)*
`multipart/form-data`: object(data: object, file: string)

---

## `POST /api/v3/annotations/count`

**Count annotations**

Route to count annotations

Args:
    request: Request object
    count_input: Input containers to count by
    filters: any filters provided in the `filters` query parameter
    auth_session: Authentication session

Returns:
    AnnotationCountOutput: The count output

Raises:
    ResourceNotFound: no reference file found with the given file ID or version
    PermissionError: not able to do action

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |

**Request Body** *(required)*
`application/json`: object(files: array[object], acquisitions: array[string], sessions: array[string], subjects: array[string])

---

## `GET /api/v3/annotations/delete_reasons`

**Get Delete Reasons**

Get annotation delete reasons route

Returns:
    dict[str, str]: Human readable form of annotation v3 delete reasons

---

## `DELETE /api/v3/annotations/{annotation_id}`

**Delete**

Route to delete annotation by id.

Args:
    request: Request object
    annotation_id: The id of the annotation to delete
    auth_session: Authentication session
    delete_reason: Reason why the annotation was deleted (required in environments where audit trail is enabled)

Returns:
    DeletedResult: The DeletedResult object

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` | 24-char hex annotation id |
| `delete_reason` | query | no | `enum(incorrect_measurement | incorrect_measurement_type | incorrect_label | obsolete_annotation_after_updated_clinical_information | adjudication_or_consensus_adjustment | annotation_contains_phi | corrective_action_after_audit | regulatory_submission_preparation | ...)` | Reason why the annotation was deleted (required in environments where audit trail is enabled) |

---

## `GET /api/v3/annotations/{annotation_id}`

**Get By Id**

Get annotation by _id route

Args:
    request: Request object
    _id: The _id of the annotation to get
    auth_session: Authentication session

Returns:
    Annotation: The annotation output for given id

Raises:
    ResourceNotFound: no annotation found with the given ID

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |

---

## `POST /api/v3/annotations/{annotation_id}`

**Create a new version of an Annotation**

Router to create annotation

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(data: object, file: string)

---

## `PUT /api/v3/annotations/{annotation_id}`

**Modify**

Update a draft annotation

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(data: object, file: string)

---

## `GET /api/v3/annotations/{annotation_id}/file`

**Get File By Annotation Id**

Get most recent annotation file data by annotation id route

Args:
    request: Request object
    annotation_id: The annotation id
    auth_session: Authentication session

Returns:
    FileData: read and returned in router

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |

---

## `GET /api/v3/annotations/{annotation_id}/versions`

**Get All Versions**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |
| `exhaustive` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `DELETE /api/v3/annotations/{annotation_id}/versions/{version}`

**Delete Version**

Route to delete annotation by id and version.

Args:
    request: Request object
    annotation_id: The id of the annotation to delete
    version: Version number
    auth_session: Authentication session
    delete_reason: Reason why the annotation was deleted (required in environments where audit trail is enabled)

Returns:
    DeletedResult: The DeletedResult object

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` | 24-char hex annotation id |
| `version` | path | yes | `integer` |  |
| `delete_reason` | query | no | `enum(incorrect_measurement | incorrect_measurement_type | incorrect_label | obsolete_annotation_after_updated_clinical_information | adjudication_or_consensus_adjustment | annotation_contains_phi | corrective_action_after_audit | regulatory_submission_preparation | ...)` | Reason why the annotation was deleted (required in environments where audit trail is enabled) |

---

## `GET /api/v3/annotations/{annotation_id}/versions/{version}`

**Get Version**

Get annotation by _id route

Args:
    request: Request object
    annotation_id: The _id of the annotation to get
    version: Version number
    auth_session: Authentication session

Returns:
    Annotation: The annotation output for given id

Raises:
    ResourceNotFound: no annotation found with the given ID

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |
| `version` | path | yes | `integer` |  |

---

## `GET /api/v3/annotations/{annotation_id}/versions/{version}/file`

**Get File Version**

Get most recent annotation file data by annotation id route

Args:
    request: Request object
    annotation_id: The annotation id
    version: Version number
    auth_session: Authentication session

Returns:
    FileData: read and returned in router

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |
| `version` | path | yes | `integer` |  |

---

## `POST /api/v3/annotations/{annotation_id}/versions/{version}/restore`

**Restore Version**

Restore annotation by annotation_id and version route

Args:
    request: Request object
    annotation_id: The annotation_id of the annotation to get
    version: Version number
    auth_session: Authentication session

Returns:
    Annotation: The restored annotation output for given annotation_id and version

Raises:
    ResourceNotFound: no annotation found with the given ID and version

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `annotation_id` | path | yes | `string` |  |
| `version` | path | yes | `integer` |  |

---
