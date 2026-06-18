---
name: fw-client
description: >
  Use to make HTTP API calls to a Flywheel instance via the fw-client Python library.
  Triggers when the user needs to call a Flywheel endpoint directly, work with /api/,
  /xfer/, or /snapshot/ services, handle auth, pagination, file upload/download, error
  handling, or async requests. Also triggers when the Flywheel SDK doesn't expose an
  endpoint the user needs. MANDATORY TRIGGERS: fw-client, FWClient, Flywheel API,
  HTTP request, api_key, /api/, /xfer/, /snapshot/, flywheel endpoint, fw.get, fw.post,
  fw.put, fw.patch
tags:
  - python
  - flywheel
  - fw-client
  - api
  - http
---

# fw-client

## Overview

`fw-client` is a production-hardened Flywheel HTTP JSON API client. It wraps `httpx` with
automatic retries, exponential backoff, and attribute-access on JSON responses. Use it when
the Flywheel Python SDK doesn't expose an endpoint you need, or when you want lower-level
control over API calls.

**Install**: `pip install fw-client`
**Version**: 2.2.0, requires Python >=3.10

---

## API Endpoint Reference

Three services are documented. All reference files live in `references/`.

**Lookup workflow:**
1. Check the relevant index file (one line per endpoint — method, path, tag, summary).
2. If you need full parameter/body schema detail, read the matching `references/endpoints/<service>_<tag>.md`.

### Core API (`/api/`) — 662 endpoints, 48 tags
Index: `references/endpoints_index_core.md`
Tag files: `references/endpoints/core_<tag>.md`
Tags: `acquisitions`, `analyses`, `annotations`, `audit_trail`, `auth`, `batch`, `bulk`,
`change_log`, `collections`, `config`, `containers`, `custom_filters`, `cvat`,
`data_view_executions`, `dataexplorer`, `devices`, `dimse`, `download`, `engine`, `files`,
`form_responses`, `forms`, `gears`, `groups`, `jobs`, `jupyterlab_servers`, `metrics`,
`modalities`, `packfiles`, `permissions`, `projects`, `read_task_protocols`, `reader_tasks`,
`reports`, `resolve`, `roles`, `sessions`, `site`, `storage`, `subjects`, `system`, `tree`,
`uids`, `upload`, `users`, `viewer_configs`, `views`, `container_type`

### Transfer API (`/xfer/`) — 61 endpoints, 9 tags
Index: `references/endpoints_index_xfer.md`
Tag files: `references/endpoints/xfer_<tag>.md`
Tags: `blobs`, `conflicts`, `connectors`, `exports`, `imports`, `rule_sets`, `schedules`,
`storages`, `upload`

### Snapshot API (`/snapshot/`) — 8 endpoints
Index: `references/endpoints_index_snapshot.md`
Tag files: `references/endpoints/snapshot_untagged.md`

Check the relevant index before using an endpoint path — guessing introduces silent bugs when paths or parameters change.

### Operation Guides

For common multi-step patterns that go beyond raw endpoint schemas:

- **[references/guides/job-operations.md](references/guides/job-operations.md)** — Querying jobs with filters, bulk cancel, batch cancel, pagination

---

## Instantiation

### Standard (API key)
```python
from fw_client import FWClient

# Embedded host+key (most common in scripts)
fw = FWClient("site.flywheel.io:your_api_key_here")

# Separate key and base_url
fw = FWClient(api_key=api_key, base_url="https://site.flywheel.io")

# With client name/version in User-Agent (recommended for tools/gears)
fw = FWClient(api_key=api_key, client_name="my-tool", client_version="1.0.0")

# With custom timeout (seconds) — useful for long-running operations
fw = FWClient(api_key=api_key, timeout=300)

# With initial headers (e.g. feature flags)
fw = FWClient(api_key=api_key, headers={"X-Accept-Feature": "Slim-Containers,Exclude-Files"})
```

### From inside a Flywheel gear
```python
# From fw-gear context
fw = FWClient(api_key=context.get_input_path("api-key"))

# From fw-curation curator (self.api_key is available)
fw = FWClient(api_key=self.api_key)
```

### Extracting API key from the Flywheel SDK client
When you only have a `flywheel.Client` and need an `FWClient`:
```python
def get_api_key_from_sdk(sdk_client: flywheel.Client) -> str:
    key = sdk_client._fw.api_client.configuration.api_key["Authorization"]
    raw_host = sdk_client._fw.api_client.configuration.host
    host = raw_host.split("//")[-1].split(":")[0]  # strip https:// and port
    return ":".join([host, key])

fw = FWClient(api_key=get_api_key_from_sdk(sdk_client))
```

### Drone / device authentication
```python
fw = FWClient(
    url="https://site.flywheel.io",
    drone_secret=os.getenv("FW_DRONE_SECRET"),
    device_type="flywheel-utility",
    device_label="my-device",
)
```

### Setting headers after instantiation
```python
fw.headers["x-accept-feature"] = "exclude-files,exclude-analyses,slim-containers"
```

---

## HTTP Methods

All methods are available in sync and async variants (`aget`, `apost`, etc.).

```python
fw.get(url, **kwargs)
fw.post(url, **kwargs)
fw.put(url, **kwargs)
fw.patch(url, **kwargs)
fw.delete(url, **kwargs)
fw.head(url, **kwargs)
```

### Key kwargs
| kwarg | Description |
|---|---|
| `params` | Dict of query parameters |
| `json` | JSON body (dict) |
| `files` | Multipart file upload |
| `content` | Raw body bytes |
| `headers` | Extra request headers |
| `raw=True` | Return raw `httpx.Response` instead of parsed JSON |
| `timeout` | Override timeout for this request |
| `auth` | Per-request auth override (`None` = anonymous) |

---

## Making Requests

### GET with query params
```python
# Inline filter in URL
projects = fw.get("/api/projects?filter=label=my_project")

# As params dict (preferred — handles encoding)
projects = fw.get("/api/projects", params={"filter": 'label="My Project"', "limit": 10})

# Multiple filters — comma-separated within the filter string
tasks = fw.get(
    f"/api/readertasks/project/{project_id}",
    params={"filter": f"assignee={user_id},status=Complete"},
)

# Sort + limit
jobs = fw.get("/api/jobs", params={"filter": filter_str, "limit": 100, "sort": "created:desc"})

# Filter with exhaustive flag (for large result sets)
protocols = fw.get(
    f"/api/read_task_protocols?filter=parents.project={project_id}&exhaustive=false"
)
```

### Cursor pagination (`after_id`)
```python
results = []
params = {"limit": 100, "after_id": None, "filter": f"parents.project={project_id}"}
while True:
    response = fw.get("/api/sessions", params=params)
    page = response.results if hasattr(response, "results") else response
    if not page:
        break
    results.extend(page)
    params["after_id"] = page[-1]._id
```

### Post-then-poll (async server jobs)
```python
# Trigger a long-running server job
fw.post(f"/snapshot/projects/{project_id}/snapshots")

# Poll until complete
import time
while True:
    snapshot = fw.get(f"/snapshot/projects/{project_id}/snapshots/{snap_id}")
    if snapshot["status"] in ("complete", "failed"):
        break
    time.sleep(10)
```

### POST with JSON body
```python
result = fw.post("/api/forms", json=form_data)
form_id = result._id  # responses have attribute access

result = fw.post("/api/read_task_protocols", json={
    "label": "My Protocol",
    "form_id": form_id,
    "viewer_config_id": viewer_config_id,
    "parent": {"type": "project", "id": project_id},
})
```

### PUT with raw response (for status checking)
```python
resp = fw.put(f"/api/site/providers/{provider_id}", json=spec, raw=True)
resp.raise_for_status()
```

### File upload
```python
# Simple multipart upload
with open("file.csv", "rb") as f:
    fw.post(f"/api/projects/{project_id}/files", files=[("file", ("file.csv", f))])

# Signed URL upload (for large files, when core_config has signed_url=True)
signed_url = fw.core_config.get("signed_url", False)
if signed_url:
    payload = {"filenames": [filename], "metadata": {}}
    upload = json.loads(
        fw.post(endpoint, params={"ticket": ""}, json=payload, stream=True).content
    )
    headers = {"Authorization": None, **upload.get("headers", {})}
    fw.put(upload["urls"][filename], headers=headers, data=file_obj)
    fw.post(endpoint, params={"ticket": upload["ticket"]})
```

### File download (with redirect)
```python
# Get signed URL for download
resp = fw.get(f"/api/files/{file_id}/download", raw=True, allow_redirects=False)
signed_url = resp.headers.get("location")
```

### Container lookup by path
```python
# POST to /api/lookup with path segments
result = fw.post("/api/lookup", json={"path": ["group_label", "project_label"]})
```

---

## Response Access

Responses are automatically JSON-parsed and wrapped with attribute access via `attrify`:

```python
user = fw.get("/api/users/self")
print(user.email)          # attribute access
print(user._id)            # underscore fields too
print(user.get("email"))   # dict-style also works

# Paginated responses — results in .results
annotations = fw.get(f"/api/annotations?filter=file_ref.file_id={file_id}")
for ann in annotations.results:
    print(ann.data.toolType)

# List responses — iterate directly
for project in fw.get("/api/projects"):
    print(project.label)
```

Empty responses return `None`, not an empty dict.

---

## Error Handling

```python
from fw_client import FWClient, ClientError, ServerError, ConnectError
from fw_client.errors import NotFound, Conflict, InvalidJSONError

# Import style 2 — errors namespace
from fw_client import FWClient, errors
# then use: errors.NotFound, errors.ClientError, etc.

# Import style 3 — from submodule
from fw_client.errors import ClientError, InvalidJSONError, ServerError

try:
    result = fw.get(f"/api/projects/{project_id}")
except errors.NotFound:
    log.error("Project not found: %s", project_id)
    raise ValueError("Invalid project ID")
except ClientError as exc:
    if exc.status_code == 404:
        return None
    raise
except ServerError as exc:
    log.error("Server error: %s", exc)
    raise
```

Error objects expose: `.status_code`, `.url`, `.method`, `.text`, `.content`, `.response`

---

## URL Namespaces

Flywheel's API spans multiple service prefixes — all routed through the same `FWClient`:

| Prefix | Service |
|---|---|
| `/api/` | Main Flywheel REST API |
| `/xfer/` | Transfer/storage service (exports, storages, upload tickets) |
| `/snapshot/` | Snapshot service |

---

## Common API URL Patterns

```python
fw.get("/api/projects")                                           # list all projects
fw.get(f"/api/projects/{project_id}")                            # project by ID
fw.get(f"/api/projects/{project_id}/sessions?filter=label={label}")  # sessions in project
fw.get("/api/subjects", params={"filter": f"label={label}"})    # subjects
fw.get(f"/api/files/{file_id}/download")                        # file download URL
fw.get("/api/annotations", params={"filter": f"file_ref.file_id={file_id}"})
fw.get("/api/users/self")                                        # current user
fw.get("/api/gears")                                             # list gears
fw.get("/api/roles")                                             # site roles
fw.get("/api/groups")                                            # list groups
fw.get("/api/site/providers")                                    # storage/compute providers
fw.get("/api/site/settings")                                     # site settings
fw.get(f"/xfer/exports/{export_id}/report")                     # export report URL

fw.post("/api/annotations", json=annotation_data)
fw.post("/api/readertasks", json=task_data)
fw.post("/api/read_task_protocols", json=protocol_data)
fw.post("/api/forms", json=form_data)
fw.post("/api/viewerconfigs", json=viewer_config_data)
fw.post("/api/lookup", json={"path": ["group", "project"]})
fw.put(f"/api/groups/{group_id}", json=update_data)
fw.put(f"/api/projects/{project_id}", json=update_data)
fw.put(f"/api/site/settings", json=update_data)

# Transfer/storage service
fw.get("/xfer/storages")                                          # list storages
fw.get(f"/xfer/storage-creds/{storage_id}")                      # storage credentials
fw.get(f"/xfer/exports/{export_id}/report")                      # export report

# Snapshot service
fw.post(f"/snapshot/projects/{project_id}/snapshots")            # trigger snapshot
fw.get(f"/snapshot/projects/{project_id}/snapshots/{snap_id}")   # poll snapshot status
```

---

## Retry & Resilience

Built-in automatic retries on 429, 502, 503, 504. Default: 4 retries with exponential backoff.

```python
# Custom retry config
fw = FWClient(
    api_key=api_key,
    retry_total=10,
    retry_backoff=1.0,
)

# Manual retry wrapper with backoff (for SDK calls mixed with fw_client)
import backoff
from flywheel.rest import ApiException

@backoff.on_exception(backoff.expo, ApiException, max_time=60)
def robust_call(client: FWClient, method: str, endpoint: str, **kwargs):
    return getattr(client, method)(endpoint, **kwargs)
```

---

## Instance Info

```python
fw.core_version             # Flywheel release version string
fw.check_version("1.2.3")  # bool — True if instance >= version
fw.core_config              # full /api/config dict (cached)
fw.check_feature("name")    # bool — feature flag check (cached)
fw.auth_status              # current auth info dict (cached) — includes user_id, origin
fw.baseurl                  # base URL of connected instance
fw.config.baseurl           # also accessible via config object
```

---

## Async Usage

All methods have async counterparts prefixed with `a`:

```python
async def fetch_dataview(client: FWClient, url: str):
    return await client.aget(url)

# Run tasks in parallel
tasks = [asyncio.create_task(fetch_dataview(client, url)) for url in urls]
results = await asyncio.gather(*tasks)
```

---

## Streaming

```python
# Download a file
with fw.stream("GET", f"/api/files/{file_id}/download") as response:
    data = response.raw.read()

# JSONL stream (one JSON object per line)
with fw.stream("GET", "/api/some-stream") as response:
    for obj in response.iter_jsonl():
        process(obj)

# SSE events
with fw.stream("GET", "/api/events") as response:
    for event in response.iter_events():
        print(event.id, event.data)
```

---

## Useful Constants & Utilities

```python
from fw_client import KILOBYTE, MEGABYTE  # 1024, 1048576

# Validate API key format
from fw_client.config import API_KEY_RE
match = API_KEY_RE.match(api_key)
if match:
    host = match.groupdict()["host"]
```

---

## Gotchas

- **Responses return `None` for empty bodies** — don't assume you always get a dict/list back
- **Attribute access is magic** — `res.label` works even though it's a dict under the hood; use `.get("key", default)` when the key might be absent
- **`raw=True`** — needed when you want status codes, headers, or to call `.raise_for_status()` manually
- **Timeout default is `(10, 30)`** (connect, read) — override for large uploads or long-running queries
- **API key length determines auth type** — 57-char keys use `Bearer`, shorter use `scitran-user` (auto-detected)
- **Device auth adds 0-1s random jitter** on first key acquisition (mitigates race conditions); skipped in pytest
- **`core_version`, `core_config`, `auth_status`** are cached properties — only fetched once per client instance
- **`x-accept-feature` header** — can request slim container responses to reduce payload size: `"exclude-files,exclude-analyses,slim-containers,subject-container"`
- **`headers` dict is mutable after construction** — `fw.headers["X-Accept-Feature"] += ",Slim-Containers"` works
- **`/snapshot/` and `/xfer/` prefixes** — not `/api/` — for snapshot and transfer services
- **Cursor pagination via `after_id`** is the correct pattern for large result sets; `exhaustive=true` is a server-side alternative but can time out
- **`read_timeout` / `connect_timeout`** are legacy kwargs; use `timeout=N` (seconds) instead
