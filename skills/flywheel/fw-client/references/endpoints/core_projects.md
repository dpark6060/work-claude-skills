# Flywheel Core API (/api/) — projects

Service: `core`  |  Tag: `projects`  |  Generated from OpenAPI spec.

## `DELETE /api/projects`

**Delete multiple projects by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/projects`

**Get a list of projects**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `counts` | query | no | `boolean` | Append the count of subjects in each project |
| `stats` | query | no | `boolean` | Return the status of subjects and sessions in each project |
| `join_avatars` | query | no | `boolean` | Return the joined avatars of the permissions |
| `join` | query | no | `enum(origin)` |  |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/projects`

**Create a new project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `inherit` | query | no | `boolean` | Inherit permissions from the group permission template |

**Request Body** *(required)*
`application/json`: object(label: string, description: string, group: string, editions: object, providers: object, ...)

---

## `GET /api/projects/catalog-list`

**Catalog List**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `search_string` | query | no | `string` | Include only results containing the search string |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `GET /api/projects/catalog-list-filter-options`

**Get all filter options for sharing a project**

---

## `GET /api/projects/groups`

**List all groups which have a project in them**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | returns exhaustive list if correct permissions |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `GET /api/projects/labels`

**Get a list of projects labels**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `include_deleted` | query | no | `boolean` | Include deleted projects |

---

## `POST /api/projects/recalc`

**Recalculate all sessions against their project templates.**

Iterates all projects that have a session template.
Recalculate if projects' sessions satisfy the template.
Returns list of modified session ids.

---

## `GET /api/projects/{cid}/analyses`

**Get analyses for a(n) project.**

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

## `POST /api/projects/{cid}/analyses`

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

## `DELETE /api/projects/{cid}/analyses/{analysis_id}`

**Delete an analysis**

Delete an analysis for a container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | Provide a reason for the deletion |

---

## `GET /api/projects/{cid}/analyses/{analysis_id}`

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

## `PUT /api/projects/{cid}/analyses/{analysis_id}`

**Modify an analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(description: string, label: string)

---

## `POST /api/projects/{cid}/analyses/{analysis_id}/files` *(deprecated)*

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

## `GET /api/projects/{cid}/analyses/{analysis_id}/files/{filename}` *(deprecated)*

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

## `GET /api/projects/{cid}/analyses/{analysis_id}/files/{filename}/info` *(deprecated)*

**Get file info from a(n) project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `GET /api/projects/{cid}/analyses/{analysis_id}/inputs/{filename}` *(deprecated)*

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

## `GET /api/projects/{cid}/analyses/{analysis_id}/inputs/{filename}/info` *(deprecated)*

**Get file info from a(n) project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `DELETE /api/projects/{cid}/analyses/{analysis_id}/notes/{note_id}`

**Remove a note from a(n) project analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |
| `note_id` | path | yes | `string` | 24-char hex note id |

---

## `DELETE /api/projects/{cid}/files/{filename}`

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

## `PUT /api/projects/{cid}/files/{filename}`

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

## `PATCH /api/projects/{cid}/files/{filename}/classification`

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

## `GET /api/projects/{cid}/files/{filename}/info`

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `PATCH /api/projects/{cid}/files/{filename}/info`

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

## `PATCH /api/projects/{cid}/info`

**Update or replace info for a(n) project.**

Update or replace info for a(n) project.
Keys that contain '$' or '.' will be sanitized in the
process of being updated on the container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `GET /api/projects/{cid}/inputs/{filename}/info` *(deprecated)*

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `DELETE /api/projects/{cid}/notes/{note_id}`

**Remove a note from a(n) project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `GET /api/projects/{cid}/notes/{note_id}`

**Get a note of a(n) project.**

Get a note of a(n) project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `PUT /api/projects/{cid}/notes/{note_id}`

**Update a note of a(n) project.**

Update a note of a(n) project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `GET /api/projects/{cid}/settings/deid_profile`

**Get deid_profile for project**

Route for getting deid profile hierarchy

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

---

## `DELETE /api/projects/{cid}/tags`

**Delete multiple tags from a(n) project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `PATCH /api/projects/{cid}/tags`

**Add multiple tags to a(n) project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `POST /api/projects/{cid}/tags`

**Add a tag to a(n) project.**

Propagates changes to projects, sessions and acquisitions

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `DELETE /api/projects/{cid}/tags/{value}`

**Delete a tag**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `GET /api/projects/{cid}/tags/{value}`

**Get the value of a tag, by name.**

Get the value of a tag, by name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `PUT /api/projects/{cid}/tags/{value}`

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

## `GET /api/projects/{cid}/{sub_cname}/analyses`

**Get nested analyses from projects**

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

## `POST /api/projects/{container_id}/analyses/{analysis_id}/notes`

**Add a note to a(n) project analysis.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` | 24-char hex id |
| `analysis_id` | path | yes | `string` | 24-char hex analysis id |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `POST /api/projects/{container_id}/files`

**Upload a file to a(n) project.**

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

## `GET /api/projects/{container_id}/files/{file_name}`

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

## `POST /api/projects/{container_id}/notes`

**Add a note to a(n) project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `GET /api/projects/{container_id}/settings`

**Get a(n) project settings**

Route for getting settings from a a(n) project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

---

## `PUT /api/projects/{container_id}/settings`

**Modify a(n) project settings**

Route for modifying settings for a a(n) project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(viewer_apps: array[object], deid_profile: any, forms: object, external_routing_id: string, sharing: object, ...)

---

## `DELETE /api/projects/{project_id}`

**Delete a project**

Delete a project.

Only site admins and users with "admin" project permissions may delete a project.

When background=true, the deletion is performed asynchronously in the background (returns 202).
Use GET /{project_id}/delete-status to check the deletion progress.

When background=false, the deletion is performed synchronously (returns 200).

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` | A reason for deletion when audit-trail is enabled |
| `background` | query | no | `boolean` | Perform deletion in the background |

---

## `GET /api/projects/{project_id}`

**Get a single project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `join` | query | no | `enum(origin)` |  |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `PUT /api/projects/{project_id}`

**Update a project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(label: string, group: string, description: string, editions: object, providers: object, ...)

---

## `GET /api/projects/{project_id}/acquisitions`

**List all acquisitions for the given project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `collection_id` | query | no | `string` |  |
| `exhaustive` | query | no | `boolean` |  |
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

## `GET /api/projects/{project_id}/copies`

**Copy By Reference List**

Return ids of project copy ids

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `POST /api/projects/{project_id}/copy`

**Copy By Reference**

Copy a project and its descendants to a new project tree

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(group_id: string, project_label: string, snapshot_id: string, filter: object)

---

## `GET /api/projects/{project_id}/copy/{snapshot_id}/status`

**Copy By Reference Status**

Return status of a project copy operation

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `snapshot_id` | path | yes | `string` |  |

---

## `GET /api/projects/{project_id}/delete-status`

**Get project deletion status**

Get the status of a project deletion running in the background.

Returns the current deletion status and any failure reason if the deletion failed.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `GET /api/projects/{project_id}/jobs`

**Find Jobs**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/projects/{project_id}/ldap-sync`

**Sync Permissions**

Synchronize project permissions based on LDAP update payload

Args:
    project_id: The id of the project
    sync_update: The LDAP sync update (users or sync error)
    auth_session: The auth session

Returns:
    LdapSyncResult: The no. of users created/granted/revoked

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(users: array[object], error: string)

---

## `POST /api/projects/{project_id}/lock`

**Project Lock**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `x-mfa-code` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(reason: enum(data_review | regulatory_audit | research_suspended | study_closed | other))

---

## `GET /api/projects/{project_id}/packfile-end`

**End a packfile upload**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `token` | query | yes | `string` |  |
| `metadata` | query | yes | `string` | Metadata object as a JSON-encoded string |
| `file_count` | query | yes | `integer` | Number of files uploaded into this packfile. |

---

## `POST /api/projects/{project_id}/packfile-end`

**Post Packfile End**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `token` | query | yes | `string` |  |
| `metadata` | query | yes | `string` |  |
| `file_count` | query | yes | `integer` | Total number of files uploaded |
| `content-type` | header | no | `string` |  |

---

## `POST /api/projects/{project_id}/packfile-start`

**Start a packfile upload to project**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `POST /api/projects/{project_id}/permissions`

**Add a permission**

Add user to a project

Args:
    project_id: The id of the project
    permission: The permission to add
    auth_session: The auth session

Returns:
    RolePermissionOutput: The added permission

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(_id: string, role_ids: array[string])

---

## `DELETE /api/projects/{project_id}/permissions/{uid}`

**Delete a permission**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `uid` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `GET /api/projects/{project_id}/permissions/{uid}`

**List a user's permissions for this project.**

Get a user's permission from a project

Args:
    project_id: The id of the project
    uid: The id of the user
    auth_session: The auth session

Returns:
    RolePermissionOutput: The permission

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `uid` | path | yes | `string` |  |

---

## `PUT /api/projects/{project_id}/permissions/{uid}`

**Update a user's permission for this project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `uid` | path | yes | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

**Request Body** *(required)*
`application/json`: object(role_ids: array[string])

---

## `POST /api/projects/{project_id}/recalc`

**Currently does nothing--will eventually calculate if sessions in the project satisfy the template.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `GET /api/projects/{project_id}/rules`

**List all rules for a project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `POST /api/projects/{project_id}/rules`

**Create a new rule for a project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(project_id: string, gear_id: string, role_id: string, name: string, config: object, ...)

---

## `DELETE /api/projects/{project_id}/rules/{rule_id}`

**Remove a project rule.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `rule_id` | path | yes | `string` |  |

---

## `GET /api/projects/{project_id}/rules/{rule_id}`

**Get a project rule.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `rule_id` | path | yes | `string` |  |

---

## `PUT /api/projects/{project_id}/rules/{rule_id}`

**Update a rule on a project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `rule_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(gear_id: string, role_id: string, name: string, config: object, fixed_inputs: array[any], ...)

---

## `GET /api/projects/{project_id}/sessions`

**List all sessions for the given project.**

Returns a page of sessions by their parent

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` | 24-char hex subject id |
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

## `GET /api/projects/{project_id}/subjects`

**List all subjects for the given project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
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

## `DELETE /api/projects/{project_id}/template`

**Remove the session template for a project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

---

## `POST /api/projects/{project_id}/template`

**Set the session template for a project.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(templates: array[object])

---

## `POST /api/projects/{project_id}/unlock`

**Project Unlock**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `x-mfa-code` | header | no | `string` |  |

---

## `POST /api/projects/{project_id}/upsert-file`

**Upsert File**

Create or update sub[ses[acq]] containers and file under the given project.

This endpoint is a combination of `POST /projects/{id}/upsert-hierarchy` and
`POST /files` endpoints for reduced import request overhead.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `force_update` | query | no | `boolean` |  |
| `cleanup_on_conflict` | query | no | `boolean` |  |
| `uid_scope` | query | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(origin: object, source: object, subject: object, session: object, acquisition: object, ...)

---

## `POST /api/projects/{project_id}/upsert-hierarchy`

**Create or update subject, session and acquisition containers in the project.**

Create, update or just return an existing container sub-hierarchy as-is for the
given project. Useful for efficient and highly parallel automated imports using
device authN, based on common routing fields such as id, uid and label.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `uid_scope` | query | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(origin: object, source: object, subject: object, session: object, acquisition: object)

---
