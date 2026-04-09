# Flywheel Core API (/api/) — jobs

Service: `core`  |  Tag: `jobs`  |  Generated from OpenAPI spec.

## `GET /api/jobs`

**Return all jobs**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `include_parent_info` | query | no | `boolean` | Include the parent info for the jobs |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/jobs/add`

**Add a job**

**Request Body** *(required)*
`application/json`: object(attempt: integer, priority: enum(low | medium | high | critical), batch: string, origin: object, compute_provider_id: string, ...)

---

## `POST /api/jobs/ask`

**Ask the queue a question**

Ask the queue a question, receiving work or statistics in return.

**Request Body** *(required)*
`application/json`: object(whitelist: object, blacklist: object, capabilities: array[string], return: object, limit: integer, ...)

---

## `POST /api/jobs/ask/{job_state}`

**Ask job count by state**

Ask the queue for the number of jobs for a given state and query.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_state` | path | yes | `enum(pending | running | failed | complete | cancelled)` |  |

**Request Body** *(required)*
`application/json`: object(whitelist: object, blacklist: object, capabilities: array[string], return: object, limit: integer, ...)

---

## `PUT /api/jobs/cancel/bulk`

**Cancel Jobs**

**Request Body** *(required)*
`application/json`: object(jobs: array[string])

---

## `POST /api/jobs/determine_provider`

**Determine the effective compute provider for a proposed job.**

**Request Body** *(required)*
`application/json`: object(attempt: integer, priority: enum(low | medium | high | critical), batch: string, origin: object, compute_provider_id: string, ...)

---

## `GET /api/jobs/next`

**Get the next job in the queue**

Used by the engine.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `tags` | query | no | `array[string]` |  |
| `tags` | query | no | `array[string]` |  |

---

## `PUT /api/jobs/priority`

**Update a job priority.**

**Request Body** *(required)*
`application/json`: JobPriorityUpdate

---

## `POST /api/jobs/reap`

**Reap stale jobs**

---

## `PUT /api/jobs/retry/bulk`

**Retry Jobs**

**Request Body** *(required)*
`application/json`: object(jobs: array[string])

---

## `GET /api/jobs/stats`

**Get stats about all current jobs**

---

## `GET /api/jobs/{job_id}`

**Get job details**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `PUT /api/jobs/{job_id}`

**Update a job.**

Updates timestamp. Enforces a valid state machine transition, if any. Rejects any change to a job that is not currently in 'pending' or 'running' state. Accepts the same body as /api/jobs/add, except all fields are optional.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(state: enum(pending | running | failed | complete | cancelled), failure_reason: string)

---

## `POST /api/jobs/{job_id}/complete`

**Complete a job, with information**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |
| `job_ticket_id` | query | no | `string` | ticket id for job completion |

**Request Body** *(required)*
`application/json`: object(success: boolean, failure_reason: string, profile: object)

---

## `PUT /api/jobs/{job_id}/complete`

**Complete a job, with information.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |
| `job_ticket_id` | query | no | `string` | ticket id for job completion |

**Request Body** *(required)*
`application/json`: object(success: boolean, failure_reason: string, profile: object)

---

## `GET /api/jobs/{job_id}/config.json`

**Get a job's config**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `GET /api/jobs/{job_id}/detail`

**Get job container details**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `PUT /api/jobs/{job_id}/heartbeat`

**Heartbeat a running job to update its modified timestamp.**

Updates the modified timestamp for a running job without changing its state. Used by engines to keep jobs alive.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `GET /api/jobs/{job_id}/logs`

**Get job logs**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `POST /api/jobs/{job_id}/logs`

**Add logs to a job.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: array[object]

---

## `GET /api/jobs/{job_id}/logs/html`

**Get Logs Html**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `GET /api/jobs/{job_id}/logs/text`

**Get Logs Text**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `POST /api/jobs/{job_id}/prepare-complete`

**Create a ticket for completing a job, with id and status.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `PUT /api/jobs/{job_id}/prepare-complete`

**Create a ticket for completing a job, with id and status.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

---

## `PUT /api/jobs/{job_id}/profile`

**Update profile information on a job. (e.g. machine type, etc)**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(elapsed_time_ms: integer, executor: object, preparation_time_ms: integer, upload_time_ms: integer, versions: object)

---

## `POST /api/jobs/{job_id}/retry`

**Retry a job.**

The job must have a state of 'failed', and must not have already been retried. The failed jobs config is copied to a new job. The ID of the new job is returned.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `job_id` | path | yes | `string` |  |
| `computeProviderId` | query | no | `string` |  |
| `ignoreState` | query | no | `boolean` |  |

---
