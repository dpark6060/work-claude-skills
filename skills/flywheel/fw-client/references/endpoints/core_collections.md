---
type: API Endpoint Schema
title: Core API — Collections
description: Flywheel Core API (/api/) endpoint schemas covering collections — curated cross-project groupings of sessions and acquisitions.
tags: [flywheel, core-api, collections]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — collections

Service: `core`  |  Tag: `collections`  |  Generated from OpenAPI spec.

## `DELETE /api/collections`

**Delete multiple collections by ID list**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `GET /api/collections`

**List all collections.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` |  |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `join_files` | query | no | `boolean` |  |
| `join` | query | no | `enum(origin)` |  |
| `stats` | query | no | `boolean` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `user_id` | query | no | `string` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `POST /api/collections`

**Create a collection**

**Request Body** *(required)*
`application/json`: object(label: string, info: object, description: string)

---

## `GET /api/collections/curators`

**List all curators of collections**

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

## `GET /api/collections/{cid}/analyses/{analysis_id}/files/{filename}/info` *(deprecated)*

**Get file info from a(n) collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `GET /api/collections/{cid}/analyses/{analysis_id}/inputs/{filename}/info` *(deprecated)*

**Get file info from a(n) collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |
| `analysis_id` | path | yes | `string` | Analysis Id |

---

## `DELETE /api/collections/{cid}/files/{filename}`

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

## `PUT /api/collections/{cid}/files/{filename}`

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

## `PATCH /api/collections/{cid}/files/{filename}/classification`

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

## `GET /api/collections/{cid}/files/{filename}/info`

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `PATCH /api/collections/{cid}/files/{filename}/info`

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

## `PATCH /api/collections/{cid}/info`

**Update or replace info for a(n) collection.**

Update or replace info for a(n) collection.
Keys that contain '$' or '.' will be sanitized in the
process of being updated on the container.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(set: object, delete: array[string], replace: object)

---

## `GET /api/collections/{cid}/inputs/{filename}/info` *(deprecated)*

**Get info for a particular file.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` | Container Id |
| `filename` | path | yes | `string` |  |

---

## `DELETE /api/collections/{cid}/notes/{note_id}`

**Remove a note from a(n) collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `GET /api/collections/{cid}/notes/{note_id}`

**Get a note of a(n) collection.**

Get a note of a(n) collection

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

---

## `PUT /api/collections/{cid}/notes/{note_id}`

**Update a note of a(n) collection.**

Update a note of a(n) collection

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `note_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---

## `DELETE /api/collections/{cid}/tags`

**Delete multiple tags from a(n) collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `PATCH /api/collections/{cid}/tags`

**Add multiple tags to a(n) collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[string]

---

## `POST /api/collections/{cid}/tags`

**Add a tag to a(n) collection.**

Propagates changes to projects, sessions and acquisitions

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(value: string)

---

## `DELETE /api/collections/{cid}/tags/{value}`

**Delete a tag**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `GET /api/collections/{cid}/tags/{value}`

**Get the value of a tag, by name.**

Get the value of a tag, by name

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `cid` | path | yes | `string` |  |
| `value` | path | yes | `string` | The tag to interact with |

---

## `PUT /api/collections/{cid}/tags/{value}`

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

## `DELETE /api/collections/{collection_id}`

**Delete a collection**

Delete Collections.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |

---

## `GET /api/collections/{collection_id}`

**Retrieve a single collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `join_avatars` | query | no | `boolean` | add name and avatar to notes |
| `join` | query | no | `enum(origin)` |  |
| `x-accept-feature` | header | no | `array[any]` |  |

---

## `PUT /api/collections/{collection_id}`

**Update a collection and its contents**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(contents: object, label: string, info: object, description: string)

---

## `GET /api/collections/{collection_id}/acquisitions`

**List acquisitions in a collection**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `session` | query | no | `string` | The id of a session, to which the acquisitions returned will be restricted |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/collections/{collection_id}/permissions`

**Add a permission**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(_id: string, access: enum(ro | rw | admin))

---

## `DELETE /api/collections/{collection_id}/permissions/{user_id}`

**Delete a permission**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---

## `GET /api/collections/{collection_id}/permissions/{user_id}`

**List a user's permissions for this group.**

List a user's permissions for this group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

---

## `PUT /api/collections/{collection_id}/permissions/{user_id}`

**Update a user's permission for this group.**

Update a users permission for this group

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `user_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(access: enum(ro | rw | admin))

---

## `GET /api/collections/{collection_id}/sessions`

**List sessions in a collection**

List sessions in a collection.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `collection_id` | path | yes | `string` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/collections/{container_id}/files`

**Upload a file to a(n) collection.**

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

## `GET /api/collections/{container_id}/files/{file_name}`

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

## `POST /api/collections/{container_id}/notes`

**Add a note to a(n) collection.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `container_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(text: string)

---
