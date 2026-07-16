---
type: API Endpoint Schema
title: Core API — Read Task Protocols
description: Flywheel Core API (/api/) endpoint schemas covering reader-task protocols.
tags: [flywheel, core-api, read-task-protocols]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — read_task_protocols

Service: `core`  |  Tag: `read_task_protocols`  |  Generated from OpenAPI spec.

## `GET /api/read_task_protocols`

**Find All Protocols**

Get all protocol route

Args:
    request: Request object
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    include_deleted: Flag whether to return deleted protocols
    auth_session: Authentication session


Returns:
    Page: The Page output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` |  |
| `include_deleted` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/read_task_protocols`

**Create**

Create read_task_protocol route

Args:
    request: Request object
    protocol_input: The input body for creating a protocol
    auth_session: Authentication session

Returns:
    ReadTaskProtocol: The inserted protocol

**Request Body** *(required)*
`application/json`: object(label: string, description: string, form_id: string, viewer_config_id: string, parent: object)

---

## `DELETE /api/read_task_protocols/{protocol_id}`

**Delete**

Delete protocol by id route

Args:
    request: Request object
    protocol_id: The protocol id to delete
    auth_session: Authentication session

Returns:
    DeletedResult: DeletedResult model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `protocol_id` | path | yes | `string` |  |

---

## `GET /api/read_task_protocols/{protocol_id}`

**Get By Id**

Get protocol by id route

Args:
    request: Request object
    protocol_id: The protocol id to get
    include_deleted: Flag whether to return deleted protocol
    auth_session: Authentication session

Returns:
    ReadTaskProtocolOutput: The protocol output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `protocol_id` | path | yes | `string` |  |
| `include_deleted` | query | no | `boolean` |  |

---

## `PUT /api/read_task_protocols/{protocol_id}`

**Modify**

Modify protocol by id route

Args:
    request: Request object
    protocol_id: The protocol id to modify
    protocol: The protocol to modify
    auth_session: Authentication session

Returns:
    ReadTaskProtocolOutput: The protocol  modified output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `protocol_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(label: string, description: string, form_id: string, viewer_config_id: string, parent: object)

---

## `GET /api/read_task_protocols/{protocol_id}/dry_run_delete`

**Dry Run Delete**

Get all in progress or todo tasks related to protocol_id which would be deleted.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `protocol_id` | path | yes | `string` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---
