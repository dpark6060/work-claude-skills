---
type: Runbook
title: "Jira: Write a Flywheel Bug Report"
description: The required sections of a Flywheel bug report (summary, reproduction code, expected, observed, environment) and how to write the reproduction script so someone else can run it.
tags: [jira, bug, bug-report, flywheel, sdk]
timestamp: 2026-09-16T00:00:00Z
---

# Jira: Write a Flywheel Bug Report

Use this for the **description body** of a Bug ticket. Ticket fields, sprint, labels, and
the create call itself are in [create-ticket.md](create-ticket.md).

## Inputs

Ask for whichever of these is missing:
1. A brief plain-language description of the bug.
2. The exact command or code that triggers it.
3. The exact output observed.

If you need SDK documentation for a specific object or call, ask for it rather than guessing.

## Output sections

1. **Summary** — one sentence, 255 characters max. This is the ticket title.
2. **Steps to reproduce** — a few sentences describing the conditions, then a runnable
   script (see below).
3. **Expected behavior**
4. **Observed behavior** — paste the actual output or error verbatim.
5. **Environment** — leave as placeholders for the reporter to fill:
    - OS:
    - Python Version:
    - Flywheel Instance Version:
    - Flywheel SDK Version:

Present the report as a draft in chat for the user to confirm before creating the ticket.

## Writing the reproduction script

### Client
Put the API key in a variable the tester can change. The code does not have to execute as-is.

```python
import flywheel
API_KEY = "<API_KEY>"
fw = flywheel.Client(API_KEY)
```

### Containers
If the bug is tied to a specific project, use the IDs from the prompt. Otherwise, for a
**non-destructive** call (nothing altered or deleted), grab any example containers:

```python
project = fw.projects.find_first()
subject = project.subjects.find_first()
file = subject.files[0]
```

For a **destructive** call, create your own containers so the tester never touches real data:

```python
project = fw.add_project("test_project")
subject = project.add_subject("test_subject")
```

A fake file when one is needed:

```python
import io
file_contents = "abc"
with io.StringIO(file_contents) as fd:
    fsize = len(file_contents)
    f = fw.upload_file_to_container(parent.id, flywheel.FileSpec(name, fd, size=fsize))
```

If no live objects are needed, build dummies from the SDK API models instead.

Include cleanup code for anything the script creates, **commented out**, so the tester deletes
it when they choose to.

Example IDs in the script follow
`~/.claude/skills/shared/flywheel/sdk-example-conventions.md`; finder queries follow
`~/.claude/skills/shared/flywheel/finder-behaviors.md`.
