# Flywheel Core API (/api/) — batch

Service: `core`  |  Tag: `batch`  |  Generated from OpenAPI spec.

## `GET /api/batch`

**Get a list of batch jobs the user has created.**

Requires login.

---

## `POST /api/batch`

**Create a batch job proposal and insert it as 'pending'.**

**Request Body** *(required)*
`application/json`: object(gear_id: string, targets: array[object], target_context: object, priority: enum(low | medium | high | critical), config: object, ...)

---

## `POST /api/batch/jobs`

**Create a batch job proposal from preconstructed jobs and insert it as 'pending'.**

**Request Body** *(required)*
`application/json`: object(jobs: array[object])

---

## `GET /api/batch/{batch_id}`

**Get batch job details.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `batch_id` | path | yes | `string` |  |
| `jobs` | query | no | `boolean` | If true, return job objects instead of job ids |

---

## `POST /api/batch/{batch_id}/cancel`

**Cancel a Job**

Cancels jobs that are still pending, returns number of jobs cancelled.
Moves a 'running' batch job to 'cancelled'.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `batch_id` | path | yes | `string` |  |

---

## `POST /api/batch/{batch_id}/run`

**Launch a job.**

Creates jobs from proposed inputs, returns jobs enqueued.
Moves 'pending' batch job to 'running'.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `batch_id` | path | yes | `string` |  |

---
