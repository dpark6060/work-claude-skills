---
type: Runbook
title: "Jira: Find the Epic for a Piece of Work"
description: How to locate the right GEAR epic for a client and component using JQL on the Customer field, rank candidates, and report near-misses instead of guessing.
tags: [jira, epic, jql, customer, search]
timestamp: 2026-08-12T00:00:00Z
---

# Jira: Find the Epic for a Piece of Work

Given a client and a component (usually a gear name), find the epic the work belongs under.
Used by `fw-workorder` phase 2, and any time work needs a parent.

You **report candidates**; you do not silently pick one. Epic choice determines both the
board structure and which Clockify task the time lands on, so a wrong pick is expensive and
invisible.

---

## Step 1 — Query epics for the client

The Customer field is `customfield_10108`. In JQL, reference it as `cf[10108]`.

```
mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId="flywheelio.atlassian.net",
    jql='project = GEAR AND issuetype = Epic AND cf[10108] = "UWash - NACC" ORDER BY updated DESC',
    fields=["key", "summary", "status", "labels"],
    maxResults=100
)
```

**Confirmed working** as of 2026-08-12. The Customer value must be the exact dropdown
option (`UWash - NACC`, not `NACC`).

Expect a lot of results — `UWash - NACC` alone has ~40 epics. Do not assume a short list.

---

## Step 2 — Rank candidates

Epic summaries do not contain gear names. They use the convention `[CLIENT] <Human Name>`:

```
[NACC] REDCap Form Image Processor
[NACC] LONI CSV Metadata Processor
[NACC] LONI Exporter
Pipeline Maintenance & Support
```

So `redcap-processor` → `[NACC] REDCap Form Image Processor` requires matching on stemmed
words, not the literal gear name. Rank by:

1. **Word overlap** between the gear name (split on `-`/`_`) and the epic summary, ignoring
   the `[CLIENT]` prefix and stopwords.
2. **Status** — an `IN PROGRESS` epic outranks a closed one at equal word overlap.
3. **Recency** — `updated DESC` breaks remaining ties.

### Always offer maintenance epics as candidates

Small cross-cutting fixes (a field rename, a config default, a version bump) often belong on
a standing maintenance epic rather than the feature epic for the gear — e.g.
`Pipeline Maintenance & Support` (`GEAR-20969`). Include any epic whose summary contains
`maintenance`, `support`, or `misc` in the candidate list regardless of word overlap, and say
why it is there. A name-only matcher will miss these every time and quietly file maintenance
work under a feature epic.

---

## Step 3 — Report

Per component, return:

| Outcome | Report |
|---|---|
| One strong match | The key, summary, status, and whether it needs reopening |
| Several plausible | All of them, ranked, with the ranking reason — let the caller choose |
| None | Say so explicitly, and list the nearest misses |

**Never create an epic here.** Epic creation is billing-visible: a near-duplicate corrupts
both the board and the Jira→Clockify task sync. No match means the caller asks the user.

---

## Step 4 — Check the sync prerequisites

An epic only produces a Clockify task when it has `SOW` + `Hourly` (or `SOW` + `Fixed`)
labels, a Customer, and a status other than `New Request`. Report any matched epic missing
these — the caller will need them fixed before time can be logged against it. Fixing them is
in [transition-issue.md](transition-issue.md); the sync itself is documented in the
`clockify` skill's `references/flywheel-workflow.md`.

Common real states seen on the GEAR board:

```
labels: ["Hourly", "SOW"]           → syncs
labels: ["Hourly", "NACC", "SOW"]   → syncs
labels: []                          → will NOT sync, needs fixing
status: "New Request"               → will NOT sync regardless of labels
```
