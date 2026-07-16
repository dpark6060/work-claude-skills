---
type: API Endpoint Schema
title: Core API — Reports
description: Flywheel Core API (/api/) endpoint schemas covering reports (usage, access, and site activity).
tags: [flywheel, core-api, reports]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — reports

Service: `core`  |  Tag: `reports`  |  Generated from OpenAPI spec.

## `GET /api/report/accesslog`

**Get a report of access log entries for the given parameters**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `csv` | query | no | `boolean` | Set to download a csv file instead of json |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return |
| `skip` | query | no | `integer` | The number of entries to skip |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `start_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the start time of the report |
| `end_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the end time of the report |
| `user` | query | no | `string` | User id of the target user |
| `subject` | query | no | `string` | Limit the report to the subject code of subject accessed |
| `project` | query | no | `string` | Limit the report to the project id |
| `access_types` | query | no | `array[enum(role_change | user_role_change | add_permission | modify_permission | delete_container | view_annotation | view_container | view_subject | ...)]` | The list of access_types to filter logs |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `GET /api/report/accesslog/types`

**Get the list of types of access log entries**

---

## `GET /api/report/daily-usage`

**Get a daily usage report for the given month.**

If no year/month pair is given, the current month will be used.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `year` | query | no | `integer` | The year portion of the date |
| `month` | query | no | `integer` | The month portion of the date |
| `group` | query | no | `string` | Limit the report to the given group id |
| `project` | query | no | `string` | Limit the report to the given project id |

---

## `GET /api/report/daily-usage-range` *(deprecated)*

**DEPRECATED - Use /reports/usage-summary instead**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `start_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the start time of the report |
| `end_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the end time of the report |
| `group` | query | no | `string` | Limit the report to the given group id |
| `project` | query | no | `string` | Limit the report to the given project id |

---

## `GET /api/report/legacy-usage` *(deprecated)*

**Get a usage report for the site grouped by month or project**

This report is DEPRECATED and will be removed in a future release

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `type` | query | yes | `string` | The type of usage report to generate |
| `start_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the start time of the report |
| `end_date` | query | no | `string(date-time)` | An ISO formatted timestamp for the end time of the report |

---

## `GET /api/report/project`

**Get project report**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `projects` | query | no | `array[string]` | Specify multiple times to include projects in the report |
| `start_date` | query | no | `string(date-time)` | Report start date |
| `end_date` | query | no | `string(date-time)` | Report end date |

---

## `GET /api/report/site`

**Get the site report**

---

## `GET /api/report/usage`

**Get a usage report for the given month.**

If no year/month pair is given, the current month will be used.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `year` | query | no | `integer` | The year portion of the date |
| `month` | query | no | `integer` | The month portion of the date |
| `project` | query | no | `string` | Project to filter to |

---

## `GET /api/report/usage-summary`

**Get aggregated usage data**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `start_date` | query | no | `string(date)` |  |
| `end_date` | query | no | `string(date)` |  |
| `group` | query | no | `string` |  |
| `project` | query | no | `string` |  |
| `group_by` | query | no | `enum(month | none)` |  |
| `limit` | query | no | `integer` |  |
| `skip` | query | no | `integer` |  |
| `csv` | query | no | `boolean` |  |

---

## `GET /api/report/usage/availability`

**Get year/month combinations where report data is available.**

Get year/month combinations where report data is available.
Returns:
    Returns the list of months where report data is available

---

## `GET /api/report/usage/collect`

**Collect daily usage statistics.**

Collects usage statistics for the selected day (or yesterday if no day is given)

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `year` | query | no | `integer` | The year portion of the date |
| `month` | query | no | `integer` | The month portion of the date |
| `day` | query | no | `integer` | The day portion of the date |

---
