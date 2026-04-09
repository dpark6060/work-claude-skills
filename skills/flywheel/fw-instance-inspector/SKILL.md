---
name: fw-instance-inspector
description: Investigate live data on a Flywheel instance. Use when the user wants to inspect container metadata, file info, file contents, or job details on a running Flywheel site. Triggers on phrases like "pull the data from Flywheel", "check this file on Flywheel", "what does this job's config look like", "inspect this subject/session/file", "look at the raw data", "pull down this file".
version: 1.0.0
tags:
  - flywheel
  - investigation
  - sdk
  - jobs
---

# Flywheel Instance Inspector

You are investigating live data on a Flywheel instance. Your job is to pull and examine data — not to modify it.

**CRITICAL: Never modify any data on Flywheel. Read-only only. Do not call any PUT, POST, PATCH, or DELETE endpoints unless the user explicitly asks for a write operation and confirms it.**

---

## Setup

### API Key
Always read the API key from an environment variable. Never hardcode it. Ask the user which env var holds the key if not stated. Common names: `NACC_API`, `FW_API_KEY`, `API_KEY`.

```python
import os
import flywheel

api_key = os.environ["NACC_API"]  # adjust var name as needed
fw = flywheel.Client(api_key)
```

If you also need `fw-client` for endpoints the SDK doesn't expose (jobs logs, config, etc.):
```python
from fw_client import FWClient
fw_http = FWClient(api_key)
```

### Running Scripts
Write investigation scripts to the working directory the user specifies. Run them with `uv run python <script.py>` from the project root. If no working directory is given, use the current project directory.

---

## Container Navigation

Flywheel container hierarchy: **Group → Project → Subject → Session → Acquisition → File**

### Getting containers by ID
IDs appear in Flywheel URLs as 24-character hex strings (e.g. `63a37161e087afb85232a588`).

```python
project  = fw.get("63a37161e087afb85232a588")
subject  = fw.get("5f2a1b3c4d5e6f7a8b9c0d1e")
session  = fw.get("69b3862da150d9bf039b10e3")
```

### Finding containers by label
```python
project = fw.projects.find_first("label=my-project")
subject = project.subjects.find_first("label=NACC813352")
session = subject.sessions.find_first("label=my-session")
```

### Listing children
```python
for subject in project.subjects.iter():
    print(subject.label)

for session in subject.sessions.iter():
    print(session.label, session.id)

for acq in session.acquisitions.iter():
    acq = acq.reload()
    for f in acq.files:
        print(f.name)
```

### Always reload before accessing metadata
SDK list results are "slim" — they may omit fields. Call `.reload()` to get the full object:
```python
session = session.reload()
subject = subject.reload()
```

---

## Inspecting File Info

`file.info` contains custom metadata set on the file. This is the most common thing to inspect.

```python
session = fw.get("69b3862da150d9bf039b10e3").reload()

for f in session.files:
    if f.name == "target_file.json":
        print(f"File: {f.name}")
        print(f"Info keys: {list(f.info.keys())}")

        # Drill into nested info
        forms = f.info.get("forms", {}).get("json", {})
        print(f"c19cospx = {repr(forms.get('c19cospx'))}")
        print(f"type     = {type(forms.get('c19cospx')).__name__}")
```

### Counting None vs "None" across fields
Useful for understanding the scope of a data issue:
```python
none_str = sum(1 for v in forms.values() if v == "None")
none_null = sum(1 for v in forms.values() if v is None)
print(f"String 'None': {none_str}, actual null: {none_null}")
```

### Downloading a file locally
```python
local_path = "/tmp/target_file.json"
session.download_file_to_filename("target_file.json", local_path)

import json
with open(local_path) as f:
    data = json.load(f)
print(data)
```

---

## Inspecting Jobs

Use `fw-client` for jobs — the SDK's job support is limited.

### Get a job by ID
```python
job = fw_http.get(f"/api/jobs/{job_id}")
print(f"State:   {job.state}")
print(f"Gear:    {job.gear_info.name} {job.gear_info.version}")
print(f"Created: {job.created}")
```

### Get a job's full config (inputs, config values, destination)
```python
config = fw_http.get(f"/api/jobs/{job_id}/config.json")
print(f"Inputs:      {list(config.inputs.keys())}")
print(f"Config:      {dict(config.config)}")
print(f"Destination: {config.destination.type} {config.destination.id}")
```

### Get job logs
```python
# Plain text (most readable for investigation)
logs = fw_http.get(f"/api/jobs/{job_id}/logs/text", raw=True)
print(logs.text)

# Structured log entries
logs = fw_http.get(f"/api/jobs/{job_id}/logs")
for entry in logs:
    print(f"[{entry.fd}] {entry.msg}")
```

### Find jobs for a project
```python
jobs = fw_http.get(
    "/api/jobs",
    params={
        "filter": f"parents.project={project_id}",
        "sort": "created:desc",
        "limit": 20,
    }
)
for job in jobs:
    print(f"{job._id}  {job.state:10s}  {job.gear_info.name}")
```

### Find jobs for a specific gear
```python
jobs = fw_http.get(
    "/api/jobs",
    params={
        "filter": f"gear_info.name=fw-parquet-etl,parents.project={project_id}",
        "sort": "created:desc",
        "limit": 10,
    }
)
```

### Get job container details (inputs with resolved container info)
```python
detail = fw_http.get(f"/api/jobs/{job_id}/detail")
```

---

## Common Investigation Patterns

### "What does this file's info look like?"
1. Get the session/container by ID from the URL
2. Reload it
3. Find the file by name in `.files`
4. Print `file.info` or drill into nested keys

### "Why does this gear produce wrong output?"
1. Get the job ID from the user (from the Flywheel UI URL or logs)
2. Pull `config.json` to see exact inputs and config used
3. Pull logs text to see what the gear reported
4. Pull the input file's info to compare against the output

### "What happened to a specific subject?"
```python
subject = fw.get(subject_id).reload()
print(f"Label: {subject.label}")
print(f"Info:  {subject.info}")
for session in subject.sessions.iter():
    session = session.reload()
    print(f"  Session: {session.label} ({session.id})")
    for f in session.files:
        print(f"    File: {f.name}")
```

---

## Safety Rules

- **No writes.** Do not call `fw.modify_*`, `container.update_info()`, `fw.add_*`, or any POST/PUT/DELETE unless explicitly instructed.
- **Use `.reload()`** before reading `.info` — slim containers don't include it.
- **IDs from URLs** are 24-char hex strings. Pull them directly; don't search by label unless the ID isn't available.
- **Print `repr(value)`** when inspecting data values — it shows the type clearly (`'None'` vs `None`).
