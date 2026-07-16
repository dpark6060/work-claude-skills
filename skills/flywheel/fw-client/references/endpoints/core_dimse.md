---
type: API Endpoint Schema
title: Core API — Dimse
description: Flywheel Core API (/api/) endpoint schemas covering DIMSE (DICOM network) services.
tags: [flywheel, core-api, dimse]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — dimse

Service: `core`  |  Tag: `dimse`  |  Generated from OpenAPI spec.

## `GET /api/dimse/projects`

**List all DIMSE project AETs**

Will list all DIMSE AETs referring to a Flywheel project.
Project AETs can be used to issue C-FIND and C-MOVE on Flywheel projects.
Requires login and admin privilege.

---

## `POST /api/dimse/projects`

**Create a new DIMSE project AET**

Will create a new DIMSE AET that refers to a Flywheel project.
AETs can only be created by admins and use drone access via DIMSE.

**Request Body** *(required)*
`application/json`: object(aet: string, created: string(date-time), creator: string, project_id: string)

---

## `DELETE /api/dimse/projects/{project_aet}`

**Delete a DIMSE project AET**

Delete DIMSE project by AET.
AETs can only be deleted by admins.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_aet` | path | yes | `string` |  |

---

## `GET /api/dimse/projects/{project_aet}`

**Get DIMSE project AET**

Get DIMSE project by AET, id or project id.
Requires admin privilege.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_aet` | path | yes | `string` |  |

---

## `GET /api/dimse/services`

**List all DIMSE services AETs**

Will list all DIMSE AETs referring to external DICOM nodes.
Requires login and admin privilege.

---

## `POST /api/dimse/services`

**Create a new DIMSE service AET**

Will create a new DIMSE AET that refers to an external DICOM node.
Service AETs can be used to issue C-MOVEs to from project AETs. Requires login.
AETs can only be created by admins.

**Request Body** *(required)*
`application/json`: any

---

## `DELETE /api/dimse/services/{service_aet}`

**Delete a DIMSE service AET**

Delete DIMSE service by AET.
AETs can only be deleted by admins.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `service_aet` | path | yes | `string` |  |

---

## `GET /api/dimse/services/{service_aet}`

**Get DIMSE service by AET or id**

Get a DIMSE service.
Requires login and admin privilege.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `service_aet` | path | yes | `string` |  |

---
