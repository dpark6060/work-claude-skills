---
type: API Endpoint Schema
title: Core API — Permissions
description: Flywheel Core API (/api/) endpoint schemas covering container permissions and role assignment.
tags: [flywheel, core-api, permissions]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — permissions

Service: `core`  |  Tag: `permissions`  |  Generated from OpenAPI spec.

## `PUT /api/permissions/check`

**Check Actions**

Validates that the authenticated user has permission to perform the requested
action.

This check is made against all projects in the project_id list, and the status code
indicates the result:

422 - Invalid action or no project ids provided
401 - No authorization information provided
403 - User is missing permission on one or more projects
204 - User is authorized to perform the requested action on all projects

**Request Body** *(required)*
`application/json`: array[object]

---

## `GET /api/permissions/check/{action}`

**Check Single Action**

Validates that the authenticated user has permission to perform the requested
action.

This check is made against all projects in the project_id list, and the status code
indicates the result:

422 - Invalid action or no project ids provided
401 - No authorization information provided
403 - User is missing permission on one or more projects
204 - User is authorized to perform the requested action on all projects

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `action` | path | yes | `any` |  |
| `project_id` | query | yes | `array[string]` | The list of project ids to check for action |

---

## `GET /api/permissions/self`

**Get User Permissions**

---
