---
type: API Endpoint Schema
title: Transfer API — Blobs
description: Flywheel Transfer API (/xfer/) endpoint schemas covering blob upload sessions and blob entries.
tags: [flywheel, xfer-api, blobs]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Transfer API (/xfer/) — Blobs

Service: `xfer`  |  Tag: `Blobs`  |  Generated from OpenAPI spec.

## `POST /xfer/blob-sessions`

**Create blob session to upload files into**

Create blob session to upload files into.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(project_id: string, label: any, local_path: any)

---

## `DELETE /xfer/blob-sessions/{session_id}`

**Delete blob session and all related blob**

Delete blob session and all related blob.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `session_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/blob-sessions/{session_id}`

**Get blob session by id**

Get blob session by id.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `session_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/blob-sessions/{session_id}/finish`

**Mark blob session as complete**

Mark blob session as complete.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `session_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/blobs`

**List blobs**

List blobs.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `before_id` | query | no | `any` | Page token / item ID to show results before. |
| `after_id` | query | no | `any` | Page token / item ID to show results after. |
| `limit` | query | no | `integer` | Page size / number of results to display per page. |
| `filter` | query | no | `array[string]` | Filter results using a `<field><op><value>` expression.<br/> Multiple filters can be passed using comma (`,`) as a separ |
| `sort` | query | no | `string` | Sort results by the given `<field>[:<order>]`.  Multiple sort fields can be passed using comma (`,`) as a separator (e.g |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/blobs`

**Create blob entry for uploading a file to storage**

Create blob entry for uploading a file to storage.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `multipart` | query | no | `boolean` |  |
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(project_id: any, blob_session_id: any, path: string, file_id: any, seq_no: any, ...)

---

## `POST /xfer/blobs/batch-delete` *(deprecated)*

**Delete a batch of blobs**

Delete a batch of blobs.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

**Request Body** *(required)*
`application/json`: object(batch: array[object])

---

## `DELETE /xfer/blobs/{blob_id}`

**Delete blob**

Delete blob.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `blob_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `GET /xfer/blobs/{blob_id}`

**Get blob**

Get blob.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `blob_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/blobs/{blob_id}/download`

**Generate pre-signed download URL for a blob in storage**

Generate pre-signed download URL for a blob in storage.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `blob_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

---

## `POST /xfer/blobs/{blob_id}/finish`

**Finalize blob upload**

Finalize blob upload.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `blob_id` | path | yes | `string` |  |
| `authorization` | header | no | `string` |  |

**Request Body**
`application/json`: any

---

## `POST /xfer/blobs/{blob_id}/upload`

**Generate pre-signed upload URL for a blob or blob part in storage**

Generate pre-signed upload URL for a blob or blob part in storage.

- Clients must send the binary data to the returned `upload_url` via PUT
- The request headers must be (and only be) `x-ms-blob-type: BlockBlob`
- If the response contains an `ETag` header, the client must save it
  for each uploaded part then send it to xfer within the finish request

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `blob_id` | path | yes | `string` |  |
| `part` | query | no | `any` |  |
| `authorization` | header | no | `string` |  |

---
