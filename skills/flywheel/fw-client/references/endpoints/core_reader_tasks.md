---
type: API Endpoint Schema
title: Core API — Reader Tasks
description: Flywheel Core API (/api/) endpoint schemas covering reader tasks (task-based workflows).
tags: [flywheel, core-api, reader-tasks]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — reader_tasks

Service: `core`  |  Tag: `reader_tasks`  |  Generated from OpenAPI spec.

## `GET /api/readertasks`

**Find All Tasks**

Router to get all reader_tasks

    Args:
    request: Request object
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    exhaustive: bool representing returning everything to client
    auth_session: Authentication session

Returns:
    Page: The page output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/readertasks`

**Create**

Router to create reader_task

**Request Body** *(required)*
`application/json`: object(assignee: string, parent: object, status: enum(Todo | In_progress | Complete), form_id: string, viewer: enum(OHIF | Form | OHIF_V3), ...)

---

## `POST /api/readertasks/batch`

**Create_batch**

Router to create batch reader_task

Args:
    request: Request object
    task_batch: The task batch input
    auth_session: Authentication session

Returns:
    List[TaskOutput]: List of TaskOutput

**Request Body** *(required)*
`application/json`: object(assignees: array[string], parent_type: enum(group | project | subject | session | acquisition | analysis | file | user | ...), project_id: string, parent_tag_filter: object, viewer: enum(OHIF | Form | OHIF_V3), ...)

---

## `POST /api/readertasks/batch/clone`

**Create batch of clone tasks**

Router to create batch of reader_task clones

Args:
    request: Request object
    clone_batch_input: The task clone batch input
    auth_session: Authentication session

Returns:
    TaskCloneBatchOutput: The TaskCloneBatchOutput model

**Request Body** *(required)*
`application/json`: object(project_id: string, task_ids: array[string], assignees: array[string])

---

## `POST /api/readertasks/batch/dryrun`

**Get details about a dry run of a given batch input**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_status` | query | no | `enum(Todo | In_progress | Complete)` |  |

**Request Body** *(required)*
`application/json`: object(assignees: array[string], parent_type: enum(group | project | subject | session | acquisition | analysis | file | user | ...), project_id: string, parent_tag_filter: object, viewer: enum(OHIF | Form | OHIF_V3), ...)

---

## `POST /api/readertasks/batch/duplicates`

**Return a list of potential duplicates of the provided batch of tasks**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_status` | query | no | `enum(Todo | In_progress | Complete)` |  |
| `sort` | query | no | `string` | The sort fields and order.(e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return |
| `skip` | query | no | `integer` | The number of entries to skip |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

**Request Body** *(required)*
`application/json`: object(assignees: array[string], parent_type: enum(group | project | subject | session | acquisition | analysis | file | user | ...), project_id: string, parent_tag_filter: object, viewer: enum(OHIF | Form | OHIF_V3), ...)

---

## `POST /api/readertasks/batch/parents`

**Count containers that match the provided filter**

Router for counting potential parents to batch tasks, given the provided
task_parents_filter

Args:
    request: Request object
    task_parents_filter: TaskParentsFilter object describing the filter
        criteria for potential parent documents
    auth_session: Authentication session

Returns:
    dict in the format of {"matching": <int representing count of matching
        potential parent objects>}

**Request Body** *(required)*
`application/json`: object(project_id: string, parent_type: enum(group | project | subject | session | acquisition | analysis | file | user | ...), include_tags: array[string], exclude_tags: array[string])

---

## `GET /api/readertasks/project/{project_id}`

**Find All**

Router to get all reader_tasks for a project

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `project_id` | path | yes | `string` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `GET /api/readertasks/task_types`

**Get Reader Task Types**

Router to get task types

Args:
    request: Request object
    auth_session: Authentication session

Returns:
    Task type dict: task type dict

---

## `DELETE /api/readertasks/{task_id}`

**Delete**

Router to delete reader_task

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |

---

## `GET /api/readertasks/{task_id}`

**Get By Id**

Router to get reader_task

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |

---

## `PUT /api/readertasks/{task_id}`

**Modify**

Router to modify reader_task

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(assignee: string, status: enum(Todo | In_progress | Complete), form_id: string, viewer: enum(OHIF | Form | OHIF_V3), viewer_config_id: string, ...)

---

## `GET /api/readertasks/{task_id}/annotations`

**Get all annotations for a reader task**

Route to get annotations by reader task id.

Args:
    request: Request object
    task_id: The id of reader task
    filter: Filter to apply
    sort: The sort fields and order
    limit: The maximum number of entries to return
    skip: The number of entries to skip
    page: The page number (i.e. skip limit*page entries)
    after_id: Paginate after the given id
    auth_session: Authentication session

Returns:
    Page: The page output

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `GET /api/readertasks/{task_id}/details`

**Get Reader Task Details**

Router to get task related all details

Args:
    request: Request object
    task_id: The id of the reader task
    auth_session: Authentication session

Returns:
    ReaderTaskDetails: The ReaderTaskDetails model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |

---

## `GET /api/readertasks/{task_id}/launch_viewer`

**Get Task Viewer Context**

Router to get task viewer context

Args:
    request: Request object
    task_id: The id of the reader task
    auth_session: Authentication session

Returns:
    TaskContextData: The TaskContextData model

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `task_id` | path | yes | `string` |  |

---
