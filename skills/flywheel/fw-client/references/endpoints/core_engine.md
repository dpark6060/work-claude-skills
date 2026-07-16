---
type: API Endpoint Schema
title: Core API — Engine
description: Flywheel Core API (/api/) endpoint schemas covering engine endpoints used by gear execution.
tags: [flywheel, core-api, engine]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — engine

Service: `core`  |  Tag: `engine`  |  Generated from OpenAPI spec.

## `POST /api/engine`

**Upload a list of file fields.**

Upload engine

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `level` | query | yes | `enum(group | project | subject | session | acquisition | analysis | file | user | ...)` |  |
| `id` | query | yes | `string` |  |
| `preserve_metadata` | query | no | `boolean` |  |
| `upload_ticket` | query | no | `string` |  |
| `job` | query | no | `string` |  |
| `x-accept-feature` | header | no | `array[any]` |  |
| `content-type` | header | no | `string` |  |

---
