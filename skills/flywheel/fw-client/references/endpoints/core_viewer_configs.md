---
type: API Endpoint Schema
title: Core API — Viewer Configs
description: Flywheel Core API (/api/) endpoint schemas covering viewer configurations.
tags: [flywheel, core-api, viewer-configs]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — viewer_configs

Service: `core`  |  Tag: `viewer_configs`  |  Generated from OpenAPI spec.

## `GET /api/viewerconfigs`

**Find all viewer configs**

Handler to get all viewer_config

Args:
    pagination: The Pagination object
    auth_session: Authentication session

Returns:
    Page: The Page output

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

## `POST /api/viewerconfigs`

**Create viewer config**

Handler to create viewer_config

Args:
    viewer_config_input: The viewer_config to insert
    auth_session: Authentication session

Returns:
    ViewerConfig: The inserted viewer configuration

**Request Body** *(required)*
`application/json`: object(name: string, config: object, viewer: enum(OHIF | Form | OHIF_V3))

---

## `DELETE /api/viewerconfigs/{viewer_config_id}`

**Delete viewer config**

Handler to delete viewer_config

Args:
    viewer_config_id: The viewer_config_id to delete
    auth_session: Authentication session

Returns:
    DeletedResult: DeletedResult model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `viewer_config_id` | path | yes | `string` |  |

---

## `GET /api/viewerconfigs/{viewer_config_id}`

**Get viewer config**

Handler to get viewer_config

Args:
    viewer_config_id: The viewer_config_id to get
    auth_session: Authentication session

Returns:
    ViewerConfigOutput: The viewer configuration output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `viewer_config_id` | path | yes | `string` |  |

---

## `PUT /api/viewerconfigs/{viewer_config_id}`

**Modify viewer config**

Handler to modify viewer_config

Args:
    viewer_config_id: The viewer_config_id to modify
    viewer_config_patch: The new viewer config data
    auth_session: Authentication session

Returns:
    ViewerConfigOutput: The modified viewer configuration output for given id

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `viewer_config_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(name: string, config: object, viewer: enum(OHIF | Form | OHIF_V3))

---

## `GET /api/viewerconfigs/{viewer_config_id}/config`

**Get raw config of viewer_config**

Handler to get raw config of viewer_config

Args:
    viewer_config_id: The viewer_config_id to get
    auth_session: Authentication session

Returns:
    Dict: The viewer configuration dictionary

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `viewer_config_id` | path | yes | `string` |  |

---
