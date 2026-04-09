# Flywheel Core API (/api/) — uids

Service: `core`  |  Tag: `uids`  |  Generated from OpenAPI spec.

## `POST /api/uids`

**Check for existence of UIDs system-wide**

Check if any of the given list of UIDs exist in the system

**Request Body** *(required)*
`application/json`: any

---

## `POST /api/uids/projects`

**Check uids with projects**

Check if any of the given list of UIDs exist in the system and return a project_id
indexed dict

**Request Body** *(required)*
`application/json`: any

---
