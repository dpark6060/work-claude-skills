---
type: API Endpoint Schema
title: Core API — Subjects
description: Flywheel Core API (/api/) endpoint schemas covering subject containers.
tags: [flywheel, core-api, subjects]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — subjects

Service: `core`  |  Tag: `subjects`  |  Generated from OpenAPI spec.

## `DELETE /api/subjects`

**Delete multiple subjects by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/subjects`

**Get a list of subjects**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `join` | query | no | `enum(origin)` | join file origins |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/subjects`

**Create a new subject**

**Request Body** *(required)*
`application/json`: object(firstname: string, lastname: string, sex: string, cohort: enum(Control | Study), date_of_birth: string(date-time), ...)

---

## `POST /api/subjects/master-code`

**Request a master subject code for the given patient**

The workflow is the following.
  - send `patient_id` (e.g., MRN) and/or `first_name`, `last_name`, `date_of_birth`
  - indicate whether to use `patient_id` for identification or `first_name`, `last_name`, `date_of_birth`
    by the `use_patient_id` field
  - the response will contain a master subject code
  - if you send the same identifying information again, you will receive the same code

Note that if you received a MSC code for example by just providing the `patient_id`, you can save more in ...

**Request Body** *(required)*
`application/json`: any

---

## `GET /api/subjects/master-code/{code}`

**Verify that the given master subject code exists or not**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `code` | path | yes | `string` | code id |

---

## `GET /api/subjects/{cid}/analyses`

**Get analyses for a(n) subject.**

Returns analyses that directly belong to this resource.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
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

## `POST /api/subjects/{cid}/analyses`

**Create an analysis and upload files.**

When query param "job" is "true", send JSON to create an analysis and job.  Otherwise, multipart/form-data to upload files and create an analysis.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `job` | query | no | `boolean` | returns job_id instead of analysis.id |

**Request Body** *(required)*
`application/json`: any

---

## `DELETE /api/subjects/{cid}/analyses/{analysis_id}`

**Delete an analysis**

Delete an analysis for a container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | Provide a reason for the deletion |

---

## `GET /api/subjects/{cid}/analyses/{analysis_id}`

**Get an analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |
| `inflate_job` | query | no | `boolean` | Return job as an object instead of an id |
| `join_avatars` | query | no | `boolean` |  |
| `join` | query | no | `enum(origin)` |  |

---

## `PUT /api/subjects/{cid}/analyses/{analysis_id}`

**Modify an analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(description: string, label: string)

---

## `POST /api/subjects/{cid}/analyses/{analysis_id}/files` *(deprecated)*

**Upload an output file to an analysis.**

Upload an output file to an analysis

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |
| `ticket` | query | no | `string` |  |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `content-type` | header | no | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(file: string(binary), metadata: any)

---

## `GET /api/subjects/{cid}/analyses/{analysis_id}/files/{filename}` *(deprecated)*

**Download analysis outputs with filter.**

If "ticket" query param is included and not empty, download outputs.
If "ticket" query param is included and empty, create a ticket for matching outputs in the analysis.
If no "ticket" query param is included, outputs will be downloaded directly.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `filename` | path | yes | `string` | filename to download (get tar of all if empty) |
| `ticket` | query | no | `string` | ticket id of the outputs to download |
| `info` | query | no | `boolean` | If the file is a zipfile, return a json response of zipfile member information |
| `member` | query | no | `string` | The filename of a zipfile member to download rather than the entire file |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `GET /api/subjects/{cid}/analyses/{analysis_id}/files/{filename}/info` *(deprecated)*

**Get file info from a(n) subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `GET /api/subjects/{cid}/analyses/{analysis_id}/inputs/{filename}` *(deprecated)*

**Download analysis inputs with filter.**

If "ticket" query param is included and not empty, download inputs.
If "ticket" query param is included and empty, create a ticket for matching inputs in the analysis.
If no "ticket" query param is included, inputs will be downloaded directly.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `filename` | path | yes | `string` | filename to download (get tar of all if empty) |
| `ticket` | query | no | `string` | 24-char hex ticket id |
| `info` | query | no | `boolean` | get file info only |
| `member` | query | no | `string` | get zipfile member |
| `view` | query | no | `boolean` | feature flag for view/download |
| `range` | header | no | `string` | byte ranges to return |
| `x-accept-feature` | header | no | `array[string]` | redirect header |

---

## `GET /api/subjects/{cid}/analyses/{analysis_id}/inputs/{filename}/info` *(deprecated)*

**Get file info from a(n) subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `DELETE /api/subjects/{cid}/analyses/{analysis_id}/notes/{note_id}`

**Remove a note from a(n) subject analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `note_id` | path | yes | `string` | 24-char hex note id |

---

## `DELETE /api/subjects/{cid}/files/{filename}`

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

## `PUT /api/subjects/{cid}/files/{filename}`

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

## `PATCH /api/subjects/{cid}/files/{filename}/classification`

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

## `GET /api/subjects/{cid}/files/{filename}/info`

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `PATCH /api/subjects/{cid}/files/{filename}/info`

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

## `PATCH /api/subjects/{cid}/info`

**Update or replace info for a(n) subject.**

Update or replace info for a(n) subject.
Keys that contain '$' or '.' will be sanitized in the
process of being updated on the container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `GET /api/subjects/{cid}/inputs/{filename}/info` *(deprecated)*

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `DELETE /api/subjects/{cid}/notes/{note_id}`

**Remove a note from a(n) subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `GET /api/subjects/{cid}/notes/{note_id}`

**Get a note of a(n) subject.**

Get a note of a(n) subject

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `PUT /api/subjects/{cid}/notes/{note_id}`

**Update a note of a(n) subject.**

Update a note of a(n) subject

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `DELETE /api/subjects/{cid}/tags`

**Delete multiple tags from a(n) subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `PATCH /api/subjects/{cid}/tags`

**Add multiple tags to a(n) subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `POST /api/subjects/{cid}/tags`

**Add a tag to a(n) subject.**

Propagates changes to projects, sessions and acquisitions

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `DELETE /api/subjects/{cid}/tags/{value}`

**Delete a tag**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `GET /api/subjects/{cid}/tags/{value}`

**Get the value of a tag, by name.**

Get the value of a tag, by name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `PUT /api/subjects/{cid}/tags/{value}`

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

## `GET /api/subjects/{cid}/{sub_cname}/analyses`

**Get nested analyses from subjects**

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

## `POST /api/subjects/{container_id}/analyses/{analysis_id}/notes`

**Add a note to a(n) subject analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `POST /api/subjects/{container_id}/files`

**Upload a file to a(n) subject.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |
| `preserve_metadata` | query | no | `boolean` |  |
| `ticket` | query | no | `string` |  |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `x-accept-feature` | header | no | `array[string]` | redirect header |
| `content-type` | header | no | `string` |  |

**Request Body** *(required)*
`multipart/form-data`: object(file: string(binary), metadata: any)

---

## `GET /api/subjects/{container_id}/files/{file_name}`

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

## `POST /api/subjects/{container_id}/notes`

**Add a note to a(n) subject.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `DELETE /api/subjects/{subject_id}`

**Delete a subject**

Read-write project permissions are required to delete a subject.
Admin project permissions are required if the subject or it's acquisitions contain
data uploaded by sources other than users and jobs.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `subject_id` | path | yes | `string` | 24-char hex subject id |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

---

## `GET /api/subjects/{subject_id}`

**Get a single subject**

Get an subject by its id

Args:
    subject_id: The id of the subject
    join: Attribute to join on
    join_avatars: Join the user avatars for permissions
    auth_session: The auth session

Returns:
    SubjectOutput

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `subject_id` | path | yes | `string` | 24-char hex subject id |
| `join` | query | no | `enum(origin)` | join file origins |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `PUT /api/subjects/{subject_id}`

**Update a subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `subject_id` | path | yes | `string` | 24-char hex subject id |

**Request Body** *(required)*
`application/json`: object(firstname: string, lastname: string, sex: string, cohort: enum(Control | Study), date_of_birth: string(date-time), ...)

---

## `POST /api/subjects/{subject_id}/copy`

**Smart copy a subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `subject_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(dst_subject_label: string, dst_project_id: string, filter: object)

---

## `GET /api/subjects/{subject_id}/sessions`

**List sessions of a subject**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `subject_id` | path | yes | `string` | 24-char hex subject id |
| `join` | query | no | `enum(origin)` | join file origins |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---
