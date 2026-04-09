# Flywheel Core API (/api/) — files

Service: `core`  |  Tag: `files`  |  Generated from OpenAPI spec.

## `DELETE /api/files`

**Delete multiple files by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/files`

**Return all files**

Get metadata of all current user files

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

## `POST /api/files`

**Upsert a File**

Create or update a file

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `force_update` | query | no | `boolean` |  |

**Request Body** *(required)*
`application/json`: object(provider_id: string, uuid: string, path: string, reference: boolean, client_hash: string, ...)

---

## `DELETE /api/files/` *(deprecated)*

**Delete Many**

Delete multiple files. Deprecated, use delete_files_by_ids instead.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | A reason for deletion when audit-trail is enabled |
| `force` | query | no | `boolean` | Force deletion of the file even if some checks fail. Deprecated, will be removed in a future release. |

**Request Body** *(required)*
`application/json`: array[string]

---

## `DELETE /api/files/{file_id}`

**Delete a File**

A user with read-write or higher permissions on the container may delete files
that were uploaded by users or were the output of jobs. (Specifically, files
whose `origin.type` is either `job` or `user`.)
<br/>
A user with admin permissions on the container may delete any file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` | Version of the file to delete (defaults to current version) |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | A reason for deletion when audit-trail is enabled |
| `force` | query | no | `boolean` | Force deletion of the file even if some checks fail. Deprecated, will be removed in a future release. |

---

## `GET /api/files/{file_id}`

**Get File**

Get file details

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |

---

## `PUT /api/files/{file_id}`

**Modify**

Modify some metadata of most recent version of a file

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(type: string, modality: string)

---

## `PUT /api/files/{file_id}/classification`

**Modify Classification**

Modify classification of most recent file version

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(modality: string, add: object, delete: object, replace: object)

---

## `GET /api/files/{file_id}/download`

**Download**

Download a file's contents (full or byte ranges).
Use auth or ticket in handler.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` | version of the file to download |
| `ticket` | query | no | `string` | 24-char hex ticket id |
| `info` | query | no | `boolean` | get file info only |
| `member` | query | no | `string` | get zipfile member |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | features header |

---

## `GET /api/files/{file_id}/info`

**Get Info**

Get info dict for any file version.
Returns:
    dict of key/value pairs

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |

---

## `PATCH /api/files/{file_id}/info`

**Modify Info**

Add info to most recent file version, adding items or replacing some existing ones.
Parameters:
    info (dict) -- key/value pairs to add
Returns:
    dict added

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body**
`application/json`: object

---

## `PUT /api/files/{file_id}/info`

**Replace Info**

Add info to most recent file version, replacing all existing values.
Parameters:
    info (dict) -- all key/value pairs to populate info
Returns:
    dict added

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body**
`application/json`: object

---

## `POST /api/files/{file_id}/move`

**Move and/or rename a file**

Move a file to a new container and/or give it a new name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(container_reference: object, name: string, run_gear_rules: boolean)

---

## `POST /api/files/{file_id}/restore`

**Restore a File**

Restore a specific version of a file as the active version. This will create a new version which will be identical to the restored version.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | yes | `integer` |  |
| `evaluate_gear_rules` | query | yes | `boolean` | Specify if gear rules should be reevaluated on the newly created file version |

---

## `GET /api/files/{file_id}/signed_url`

**Get Signed Url**

Return signed URL string from provider for this file

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `view` | query | no | `boolean` | feature flag for view/download |

---

## `DELETE /api/files/{file_id}/tags`

**Remove the specified tags from most recent file version**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body**
`application/json`: array[string]

---

## `GET /api/files/{file_id}/tags`

**Return a file tags, from any version**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |

---

## `PATCH /api/files/{file_id}/tags`

**Add list of tags on a file.**

Add the tags on a file to the list of tags

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `PUT /api/files/{file_id}/tags`

**Set list of tags on a file.**

Set the tags on a file to the list of tags provided

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `POST /api/files/{file_id}/ticket`

**Get Ticket Stub**

Get download ticket

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `view` | query | no | `boolean` | feature flag for view/download |

---

## `GET /api/files/{file_id}/ticket/{ticket_id}/validate`

**Validate Ticket**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `ticket_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |

---

## `GET /api/files/{file_id}/version/{version}/download/{filename}`

**Engine Download**

Download a file's contents (full or byte ranges).
Use auth or ticket in handler.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | path | yes | `integer` |  |
| `filename` | path | yes | `string` |  |
| `ticket` | query | no | `string` |  |
| `info` | query | no | `boolean` | get file info only |
| `member` | query | no | `string` | get zipfile member |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` |  |
| `x-accept-feature` | header | no | `array[string]` | features header |

---

## `GET /api/files/{file_id}/versions`

**Get Versions**

Get file version details

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |

---

## `GET /api/files/{file_id}/zip_info`

**Get Zip Info**

Get info on zipfile

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `ticket` | query | no | `string` |  |

---

## `GET /api/files/{file_id}/zip_member/{member}`

**Get Zip Member**

Download contents of <member> member of zipfile

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `file_id` | path | yes | `string` |  |
| `member` | path | yes | `string` |  |
| `version` | query | no | `integer` |  |
| `view` | query | no | `boolean` | feature flag for view/download |
| `ticket` | query | no | `string` |  |

---
