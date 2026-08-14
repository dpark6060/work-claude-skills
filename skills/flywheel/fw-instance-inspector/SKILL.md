---
name: fw-instance-inspector
description: >
  Investigate live data on a Flywheel instance — pull container metadata, file info,
  file contents, job configs, and job logs. Use even when the user doesn't say
  "Flywheel" explicitly, if they're asking about a gear job, a subject/session/file,
  or why something failed on a running site.
  MANDATORY TRIGGERS: inspect, investigate, pull data, check file, look at job,
  job config, job logs, why did this gear fail, debug job, trace error, what did
  the gear see, container metadata, subject session acquisition, Flywheel URL,
  fw-client, fw.get
version: 1.0.0
tags:
  - flywheel
  - investigation
  - sdk
  - jobs
allowed-tools:
  - Bash
  - Read
  - Write
---

# Flywheel Instance Inspector

You are investigating live data on a Flywheel instance. Your job is to pull and examine data. See Safety Rules at the bottom before writing any code.

---

## Setup

### API Key
**Read `~/.fw/config.yml` `profiles:` first.** It maps profile name → host + key for
every site there's a key for (`ge`/`fwge`, `nacc`, `naccsb`, `upenn`, `uw`, `ucsf`, …).
Match the host in the Flywheel URL you were given to a profile, and use that profile's
`api_key` value (already in `host:key` form). Never declare "no API key for instance X"
before checking that file, and never ask the user for an env var before checking it.

Full profile inventory, how to read the file without PyYAML, host→profile gotchas, and
client-construction rules: **`~/.claude/skills/shared/flywheel/instance-access.md`**.

Env vars are the fallback when a profile can't be used (common names: `NACC_API`,
`FW_API_KEY`, `API_KEY`). Never hardcode a key, and never print or write one.

```python
import os
import flywheel

api_key = os.environ["NACC_API"]  # or the api_key value from the matching ~/.fw profile
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

## Subject Investigation Pattern
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

## Before Starting

Read and summarize `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`. Summarizing (not just reading) forces you to internalize what has and hasn't worked in previous runs.

## After Finishing

If this session produced anything worth capturing, append to the relevant file:
- **.learnings/LEARNINGS.md** — a pattern that worked, a non-obvious SDK behavior, or a workflow adjustment that improved the result.
- **.learnings/ERRORS.md** — a failure, an error, or a wrong assumption and how it was fixed.

Don't write an entry if nothing went wrong and nothing surprising happened.

---

## Safety Rules

- **No writes.** Do not call `fw.modify_*`, `container.update_info()`, `fw.add_*`, or any POST/PUT/DELETE unless explicitly instructed.
- **Use `.reload()`** before reading `.info` — slim containers don't include it.
- **IDs from URLs** are 24-char hex strings. Pull them directly; don't search by label unless the ID isn't available.
- **Print `repr(value)`** when inspecting data values — it shows the type clearly (`'None'` vs `None`).
