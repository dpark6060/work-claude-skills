# Job Operations Guide

Reference for querying, filtering, and bulk-modifying Flywheel jobs via fw-client.
Full endpoint schemas are in [`endpoints/core_jobs.md`](../endpoints/core_jobs.md).

---

## Querying Jobs

`GET /api/jobs` returns all jobs. Use the `filter` parameter to narrow results.

```python
# All jobs (use limit + pagination for large result sets)
jobs = fw.get("/api/jobs", params={"limit": 100})

# Filter by state
jobs = fw.get("/api/jobs", params={"filter": "state=pending", "limit": 1000})
```

### Filter Syntax

The `filter` parameter is a **comma-separated string**; all conditions are ANDed.

```python
# Single filter
params={"filter": "state=pending"}

# Multiple filters — comma-separated
params={"filter": "parents.project=<project_id>,state=pending"}
params={"filter": f"gear_id={gear_id},state=failed"}
```

Supported filter keys:

| Key | Example | Description |
|---|---|---|
| `state` | `state=pending` | `pending`, `running`, `failed`, `complete`, `cancelled` |
| `parents.project` | `parents.project=<project_id>` | Jobs whose destination is within a project |
| `parents.group` | `parents.group=<group_id>` | Jobs within a group |
| `gear_id` | `gear_id=<gear_id>` | Jobs for a specific gear |
| `tags` | `tags=my-tag` | Jobs tagged with a value |
| `origin.id` | `origin.id=<user_id>` | Jobs submitted by a specific user |

### Paginating Large Result Sets

Use `after_id` cursor pagination for result sets that exceed your `limit`:

```python
job_ids = []
params = {"filter": "state=pending", "limit": 1000}

while True:
    response = fw.get("/api/jobs", params=params)
    page = response.results if hasattr(response, "results") else list(response or [])
    if not page:
        break
    job_ids.extend(job._id for job in page)
    if len(page) < params["limit"]:
        break
    params["after_id"] = page[-1]._id
```

---

## Cancelling Jobs

Only `pending` and `running` jobs can be cancelled. Terminal states (`complete`, `failed`,
`cancelled`) are rejected by the state machine.

### Single Job

```python
fw.put(f"/api/jobs/{job_id}", json={"state": "cancelled"})
```

### Bulk Cancel

`PUT /api/jobs/cancel/bulk` accepts an array of job IDs and cancels them in one request.
This is the preferred approach for cancelling more than a handful of jobs.

```python
fw.put("/api/jobs/cancel/bulk", json={"jobs": job_ids})
```

- Jobs already in a terminal state are silently skipped — no error.
- There is no partial-failure response; the call either succeeds or raises an HTTP error.
- No documented limit on array size, but keep individual requests under ~5 000 IDs as a
  practical ceiling.

### Combining Filter + Bulk Cancel

Collect IDs with pagination, then cancel in one shot:

```python
job_ids = []
params = {"filter": "state=pending", "limit": 1000}  # adjust filter as needed

while True:
    response = fw.get("/api/jobs", params=params)
    page = response.results if hasattr(response, "results") else list(response or [])
    if not page:
        break
    job_ids.extend(job._id for job in page)
    if len(page) < params["limit"]:
        break
    params["after_id"] = page[-1]._id

if job_ids:
    fw.put("/api/jobs/cancel/bulk", json={"jobs": job_ids})
    print(f"Cancelled {len(job_ids)} jobs")
```

---

## Batch-Level Cancel

If jobs were created via `POST /api/batch/{batch_id}/run`, you can cancel the entire batch
without listing individual job IDs:

```python
fw.post(f"/api/batch/{batch_id}/cancel")
```

Cancels all still-pending jobs in the batch and moves any running batch jobs to `cancelled`.
Returns the number of jobs cancelled. See [`endpoints/core_batch.md`](../endpoints/core_batch.md)
for full schema.
