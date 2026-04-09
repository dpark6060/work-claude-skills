# Flywheel Core API (/api/) — analyses

Service: `core`  |  Tag: `analyses`  |  Generated from OpenAPI spec.

## `DELETE /api/analyses`

**Delete multiple analyses by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/analyses`

**Find all analyses**

Returns a page of analyses

Args:
    filter (t.Optional[str]):     The filters to apply
    sort (t.List[Tuple[str,int]): Sorting, as a list of (str, int) tuples
    limit (t.Optional[int]):      The maximum number of entries to return
    skip (t.Optional[int]):       The number of entries to skip
    page (t.Optional[int]):       Page number
    after_id (t.Optional[str]):   Id to return results after

Returns:
    Page: if a above argument is not None

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `inflate_job` | query | no | `boolean` | Return job as an object instead of an id |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `DELETE /api/analyses/{analysis_id}`

**Delete an analysis**

Delete an analysis by its id

Args:
    analysis_id: The id of the analysis
    auth_session: The auth session
    delete_reason: The reason for deletion (required when audit-trail is enabled)

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

---

## `GET /api/analyses/{analysis_id}`

**Get an analysis.**

Get an analysis by its id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `inflate_job` | query | no | `boolean` | expand job info |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `join` | query | no | `enum(origin)` |  |

---

## `PUT /api/analyses/{analysis_id}`

**Modify an analysis.**

Modify an analysis by its id

Args:
    analysis_id: The id of the analysis
    analysis_modify: The modifications to make
    auth_session: The auth session

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |

**Request Body** *(required)*
`application/json`: object(description: string, label: string)

---

## `DELETE /api/analyses/{cid}/files/{filename}`

**Delete a file**

A user with read-write or higher permissions on the container may delete files
that were uploaded by users or were the output of jobs. (Specifically, files
whose `origin.type` is either `job` or `user`.)
<br/>
A user with admin permissions on the container may delete any file.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `filename` | path | yes | `string` |  |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | A reason for deletion when audit-trail is enabled |
| `force` | query | no | `boolean` | Force deletion of the file even if some checks fail. Deprecated, will be removed in a future release. |

---

## `GET /api/analyses/{cid}/files/{filename}`

**Download output file from analysis**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container ID |
| `filename` | path | yes | `string` | output file name |
| `ticket` | query | no | `string` | 24-char hex ticket id |
| `info` | query | no | `boolean` | get file info only |
| `member` | query | no | `string` | get zipfile member |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `PUT /api/analyses/{cid}/files/{filename}`

**Modify a file's attributes**

Note: If modifying a file's modality, the current classification will be cleared (except for items in the "Custom" list)

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `filename` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(type: string, modality: string)

---

## `PATCH /api/analyses/{cid}/files/{filename}/classification`

**Update classification for a particular file.**

If replacing a file's classification, the modality can optionally be modified as well.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `filename` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(modality: string, add: object, delete: object, replace: object)

---

## `GET /api/analyses/{cid}/files/{filename}/info`

**Get metadata for an output file of an analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `ctype` | query | no | `enum(acquisitions | analyses | containers | collections | projects | sessions | subjects)` |  |

---

## `PATCH /api/analyses/{cid}/files/{filename}/info`

**Update info for a particular file.**

Modify and return the file 'info' field

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `filename` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `PATCH /api/analyses/{cid}/info`

**Update or replace info for a(n) analysis.**

Update or replace info for a(n) analysis.
Keys that contain '$' or '.' will be sanitized in the
process of being updated on the container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `GET /api/analyses/{cid}/inputs/{filename}` *(deprecated)*

**Download analysis inputs with filter.**

If "ticket" query param is included and not empty, download inputs.
If "ticket" query param is included and empty, create a ticket for matching inputs in the analysis.
If no "ticket" query param is included, inputs will be downloaded directly.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container ID |
| `filename` | path | yes | `string` | input filename |
| `ticket` | query | no | `string` | 24-char hex ticket id |
| `info` | query | no | `boolean` | get file info only |
| `member` | query | no | `string` | get zipfile member |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `GET /api/analyses/{cid}/inputs/{filename}/info` *(deprecated)*

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `DELETE /api/analyses/{cid}/notes/{note_id}`

**Remove a note from a(n) analysis**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `GET /api/analyses/{cid}/notes/{note_id}`

**Get a note of a(n) analysis.**

Get a note of a(n) analysis

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `PUT /api/analyses/{cid}/notes/{note_id}`

**Update a note of a(n) analysis.**

Update a note of a(n) analysis

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `POST /api/analyses/{cid}/tags`

**Add a tag to a(n) analysis.**

Propagates changes to projects, sessions and acquisitions

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `DELETE /api/analyses/{cid}/tags/{value}`

**Delete a tag**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `GET /api/analyses/{cid}/tags/{value}`

**Get the value of a tag, by name.**

Get the value of a tag, by name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `PUT /api/analyses/{cid}/tags/{value}`

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

## `POST /api/analyses/{container_id}/files`

**Upload an output file to an analysis.**

Upload an output file to an analysis

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |
| `ticket` | query | no | `string` |  |
| `preserve_metadata` | query | no | `boolean` |  |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `x-accept-feature` | header | no | `array[string]` | redirect header |
| `content-type` | header | no | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(file: string(binary), metadata: any)

---

## `GET /api/analyses/{container_id}/files/{file_name}`

**Download a file.**

Files can be downloaded directly from this endpoint with a valid "Authorization" header or via a ticket id.

To generate a ticket:
  - Make a request with an empty "ticket" parameter and a valid "Authorization" header. The server will respond with a generated ticket id.
  - Make another request with the received ticket id in the "ticket" parameter. A valid "Authorization" header is no longer required.

When "view" is true, [RFC7233](https://tools.ietf.org/html/rfc7233) range request headers are  ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` | 24-char hex id |
| `file_name` | path | yes | `string` | output file name |
| `ticket` | query | no | `string` | The generated ticket id for the download, or present but empty to generate a ticket id |
| `info` | query | no | `boolean` | If the file is a zipfile, return a json response of zipfile member information |
| `member` | query | no | `string` | The filename of a zipfile member to download rather than the entire file |
| `view` | query | no | `boolean` | If true, the proper "Content-Type" header based on the file's mimetype is set on response If false, the "Content-Type" h |
| `version` | query | no | `integer` | version of the file to download |
| `hash` | query | no | `string` | file hash for comparison |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `GET /api/analyses/{container_id}/info`

**Get Info**

Gets custom info for the specified container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

---

## `GET /api/analyses/{container_id}/input_files/{filename}/info`

**Get metadata for input file(s) for an analysis.**

Get metadata for input file(s) for an analysis. There may be more than one since input filenames are not guaranteed to be unique.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `GET /api/analyses/{container_id}/inputs/{filename}/info` *(deprecated)*

**Get metadata for an input file of an analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `POST /api/analyses/{container_id}/notes`

**Add a note to a(n) analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---
