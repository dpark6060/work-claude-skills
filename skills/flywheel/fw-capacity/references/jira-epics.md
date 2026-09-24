---
type: Procedure Reference
title: Jira Epic Scoping and Estimate Parsing
description: Which epics enter the forecast, and how to extract a trustworthy remaining estimate from each one.
tags: [capacity, jira, estimates, epics]
timestamp: 2026-09-17T00:00:00Z
---

# Jira Epic Scoping and Estimate Parsing

> **Load when:** selecting epics for the forecast or reading an estimate off one.

Cloud id: `27a9c1e5-5c70-4dad-a559-80493dd1429d`. Everything here is read-only.

# Selecting epics

```
assignee = currentUser() AND issuetype = Epic AND statusCategory != Done ORDER BY duedate ASC
```

Request `key, summary, status, duedate, labels, description`. That returns roughly 14 epics, and
several are unforecastable noise. Split them into three groups:

| Group | Test | Treatment |
|---|---|---|
| **Forecast** | `IN PROGRESS`/`REQUIREMENTS DEVELOPMENT`, or due within ~a quarter | Full arithmetic |
| **Overdue** | Due date already passed | Reported first, no forecast — the date is gone |
| **Excluded** | `ON HOLD`, no due date, or due date long past and clearly dormant | Listed by key and reason only |

As of 2026-09-17 the excluded set includes `SSEIN-210` (due 2022-09-30), `GEAR-5006`, `GEAR-6209`,
and `GEAR-7350` — all ON HOLD or stale. **List them, never drop them silently.** A dormant epic
reappearing in the forecast is how a quarter gets quietly overcommitted.

# Estimates

**Never use `timeoriginalestimate` or `aggregatetimeoriginalestimate`.** They're 0 on most epics and
wrong on the rest. Requesting them at all invites accidental use.

The real estimate is a structured block in the epic description:

```markdown
## Estimate: 53 h (S)

27 h spent (Clockify, 2026-08-03 to 2026-09-03), 26 h remaining.

* Build: 33 h
* Testing against GE sample data: 7 h
* Documentation, configuration on the GE site, deployment: 8 h
```

Parse, in priority order:

1. `N h remaining` → **remaining estimate**. Most accurate; already reconciled against Clockify.
2. `## Estimate: N h` minus `N h spent` when no explicit remaining figure appears.
3. `## Estimate: N h` alone when nothing records spend.
4. The bullet breakdown — also the **scope-reduction menu** for tradeoffs. Quote real lines and
   their hours; don't invent cuttable work.

The parenthesised letter (`(S)`) is the t-shirt size, carried inline. The separate `T-Shirt Size`
Jira field is JQL-queryable but the MCP won't return custom fields by display name, so resolve its
`customfield_*` id once and cache it in `cache/field-map.json` rather than hardcoding an
instance-specific id in this file.

T-shirt fallback bands, used **only** when no estimate block exists:

| Size | Hours |
|---|---|
| XS | 8 |
| S | 40 |
| M | 80 |
| L | 160 |
| XL | 320 |

These are coarse by design. Any epic forecast off a t-shirt band gets flagged as low-confidence in
the report.

# Client attribution

Each epic maps to one capacity-plan initiative via [client-map.md](client-map.md). Signals, in
order: `labels` (`GE-HealthCare`, `4DV`), then the summary prefix (`[NACC]`, `[GE-AVS]`), then the
epic's parent or component.

An epic mapping to no initiative is a **gap worth reporting**: either the capacity plan doesn't
cover work you're committed to, or the map needs an alias. Both matter. Don't silently bucket it
into Internal.

The `SOW` and `Hourly` labels describe the contract type, not the client. They never identify an
initiative.

# Status blocks

Many epics also carry a `## Status (YYYY-MM-DD)` section naming blockers:

```
Blocked: GEAR-15168, deployment model, waiting on GE since 2026-08-25.
```

A blocked epic's forecast is fiction — the clock isn't running. Surface the blocker and its age
next to the date verdict instead of presenting a clean finish date.
