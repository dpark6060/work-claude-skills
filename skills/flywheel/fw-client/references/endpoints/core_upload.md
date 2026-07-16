---
type: API Endpoint Schema
title: Core API — Upload
description: Flywheel Core API (/api/) endpoint schemas covering upload endpoints (label, UID, and reaper uploads).
tags: [flywheel, core-api, upload]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — upload

Service: `core`  |  Tag: `upload`  |  Generated from OpenAPI spec.

## `POST /api/upload/complete-azure-multipart`

**Complete Azure Multipart Upload**

Complete Azure multipart signed url upload.

**Request Body** *(required)*
`application/json`: object(provider_id: string, uuid: string, block_ids: array[string])

---

## `POST /api/upload/complete-s3-multipart`

**Complete S3 multipart signed url upload**

Complete S3 uploads exceeding 5GB and create the final object in the bucket.
Expected an upload id returned previously by the `POST /upload/signed-url` endpoint
and the e-tags returned by S3 after uploaded each file part.

**Request Body** *(required)*
`application/json`: object(provider_id: string, uuid: string, upload_id: string, etags: array[string])

---

## `PUT /api/upload/fs-file`

**Upload file to local filesystem storage provider**

The POST `/api/upload/signed-url` endpoint returns a url with
a jwt token pointing to this endpoint if the storage provider
is a local filesystem then the file can be uploaded simply by sending
the file content in the body of the payload. The destination storage
provider and the file path are encoded in the jwt token.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `token` | query | yes | `string` | Upload token |

**Request Body** *(required)*
`application/json`: string(binary)

---

## `POST /api/upload/label`

**Multipart form upload with N file fields, each with their desired filename.**

### Default behavior:
> For technical reasons, no form field names can be repeated. Instead, use
  (file1, file2) and so forth.

> A non-file form field called "metadata" is also required, which must be
  a string containing JSON.

> See ``api/schemas/input/labelupload.json`` for the format of this metadata.

### Signed URL upload with ``ticket``
> Upload a single file directly to the storage backend. The workflow is the following:

  - Send a request with an empty ``?ticket=`` query parameter t ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `preserve_metadata` | query | no | `boolean` |  |
| `ticket` | query | no | `string` | Use empty value to get a ticket, and provide the ticket id to finalize the upload |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `content-type` | header | no | `string` |  |

**Request Body**
`multipart/form-data`: object(files: string(binary), metadata: object)

---

## `POST /api/upload/reaper`

**Bottom-up UID matching of Multipart form upload with N file fields, each with their desired filename.**

### Default behavior:

> Upload data, allowing users to move sessions during scans without causing new data to be
  created in referenced project/group.

### Evaluation Order:

* If a matching acquisition UID is found anywhere on the system, the related files will be placed under that acquisition.
* **OR** If a matching session UID is found, a new acquistion is created with the specified UID under that Session UID.
* **OR** If a matching group ID and project label are found, a new session and ac ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `preserve_metadata` | query | no | `boolean` |  |
| `ticket` | query | no | `string` | Use empty value to get a ticket, and provide the ticket id to finalize the upload |
| `uid_placement` | query | no | `boolean` |  |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `content-type` | header | no | `string` |  |

**Request Body**
`multipart/form-data`: object(files: string(binary), metadata: object)

---

## `POST /api/upload/signed-url`

**Create new signed upload URL**

Return a signed upload URL for the requested storage provider_id.
Multiple URLs are returned for S3 uploads exceeding 5GB.

**Request Body** *(required)*
`application/json`: object(provider_id: string, size: integer)

---

## `POST /api/upload/signed-url/cleanup`

**Cleanup unused file blob previously uploaded using signed URL**

**Request Body** *(required)*
`application/json`: object(provider_id: string, uuid: string)

---

## `POST /api/upload/uid`

**Multipart form upload with N file fields, each with their desired filename.**

### Default behavior:
> Same behavior as /api/upload/label,
  except the metadata field must be uid format
  See ``api/schemas/input/uidupload.json`` for the format of this metadata.

### Signed URL upload with ``ticket``
> Upload a single file directly to the storage backend. The workflow is the following:

  - Send a request with an empty ``?ticket=`` query parameter to get an upload ticket and URL
  - Upload the file using a PUT request to the upload URL
  - Once done, send a POST request to  ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `preserve_metadata` | query | no | `boolean` |  |
| `ticket` | query | no | `string` | Use empty value to get a ticket, and provide the ticket id to finalize the upload |
| `id` | query | no | `string` |  |
| `level` | query | no | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `job` | query | no | `string` |  |
| `content-type` | header | no | `string` |  |

**Request Body**
`multipart/form-data`: object(files: string(binary), metadata: object)

---
