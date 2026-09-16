---
type: Reference
title: Flywheel SDK Finder / Filter Behaviors
description: Confirmed quoting and filter rules for fw.<containers>.find() — when to quote, never quote parent filters, booleans on parents always return nothing, groups use _id.
tags: [flywheel, sdk, finder, filter, gotchas]
timestamp: 2026-09-16T00:00:00Z
---

# Flywheel SDK Finder / Filter Behaviors

Reference for `fw.<containers>.find()` and `fw.<containers>.find_first()` queries. These rules reflect confirmed SDK behaviors and known gotchas — deviating from them causes silent failures (empty results, no error raised).

---

## Quoting String Values

### Direct container filters

When filtering on a property of the container you are directly searching for (e.g. `label=`, `info.*=`), string values MAY always be quoted. Fully numeric string values MUST be quoted — without quotes they are treated as integers and the filter fails.

```python
# Correct — numeric label quoted
fw.sessions.find("label=\"20201224\"")

# Correct — string label quoted (also works unquoted, but quoting is safe)
fw.sessions.find("label=\"MySession\"")

# Wrong — numeric label unquoted, returns no results
fw.sessions.find("label=20201224")
```

### Parent container filters

When filtering on a property of a **parent** container (e.g. `parents.subject=`, `subject.label=`, `session.info.*=`), values must **never** be quoted. Quoting a parent filter value always breaks the filter and returns no results, with no error raised.

```python
# Correct — parent property unquoted
fw.acquisitions.find("parents.subject=abc123")
fw.acquisitions.find("label=My_T1,session.info.sessid=test")

# Wrong — parent property quoted, silently returns 0 results
fw.acquisitions.find("parents.subject=\"abc123\"")
fw.acquisitions.find("label=My_T1,session.info.sessid=\"test\"")
```

---

## Boolean Values on Parent Containers

Filtering on a boolean metadata value on a **parent** container always returns 0 results, even when matches exist. This is a known SDK limitation with no fix on the filter side.

```python
# Works — string metadata value on parent
fw.acquisitions.find("label=My_T1,session.info.sessid=test")

# Fails silently — boolean metadata value on parent
fw.acquisitions.find("label=My_T1,session.info.passQA=true")
```

**Workaround**: fetch the parent container first, check the boolean in Python, then query child containers.

```python
session = fw.get_session(session_id)
if session.info.get("passQA"):
    acquisitions = session.acquisitions()
```

---

## Group IDs

Group container IDs must use `_id` in finder filters. All other container types use `id`.

```python
# Correct for groups
fw.projects.find("group._id=my-group")

# Correct for other containers (sessions, subjects, etc.)
fw.acquisitions.find("id=abc123def456abc123def456")
```

---

## Summary Table

| Scenario | Quote value? |
|---|---|
| Direct filter on string value | Optional (safe to quote) |
| Direct filter on numeric string value | Required |
| Parent container filter — any value | Never |
| Boolean metadata on parent container | Avoid — use Python filter instead |
| Group `id` field | Use `_id`, not `id` |
