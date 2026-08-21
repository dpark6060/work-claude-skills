---
type: Reference
title: GEAR Board Fields
description: Field ids, issue-type ids, priority ids, and option ids for the GEAR Jira project, with the live call to re-derive them when they drift.
tags: [atlassian, jira, gear, fields, custom-fields]
timestamp: 2026-08-17T00:00:00Z
---

# GEAR Board Fields

Ids for Jira project **GEAR** ("Scientific Solutions", project id `10020`,
`projectTypeKey: software`, simplified/team-managed). Access setup and cloudId:
`mcp-access.md`.

> **These drift.** Options get added, screens change. Re-derive with
> `getJiraIssueTypeMetaWithFields` (`requiredFieldsOnly: false`) before any create or
> edit rather than trusting this page — it is a map, not an authority. Values below
> confirmed live 2026-08-17.

## Contents
- Issue types
- Custom fields
- Priorities
- Customer/s options
- Re-deriving

---

## Issue types

| Name | Id | Hierarchy | Notes |
|---|---|---|---|
| Epic | `10021` | 1 | |
| Task | `10020` | 0 | |
| Story | `10029` | 0 | Description says "when an existing gear is being upgraded" |
| Bug | `10030` | 0 | |
| Spike | `10098` | 0 | "Deep dive... to surface actionable issues" |
| Vulnerability | `11318` | 0 | |
| Subtask | `10022` | −1 | |

---

## Custom fields

| Field | Id | Type |
|---|---|---|
| Sprint | `customfield_10021` | greenhopper sprint (array) |
| Rank | `customfield_10022` | lexo-rank |
| Start date | `customfield_10015` | date |
| Flagged | `customfield_10027` | multicheckbox — `Impediment` = `10019` |
| **Customer/s** | `customfield_10108` | multiselect (see below) |
| **Acceptance Criteria** | `customfield_11394` | textarea |
| Zendesk Ticket IDs | `customfield_11292` | textarea |
| Zendesk Ticket Count | `customfield_11293` | number |
| Development | `customfield_10000` | dev-integration (read-only in practice) |
| Design | `customfield_11286` | design-integration |
| Vulnerability | `customfield_11296` | vulnerability-integration |

**Only `project` and `summary` are actually required** to create a GEAR issue. The
create screen exposes 24 fields total; everything else is optional, including
Customer/s and Acceptance Criteria. `priority` has a default (`Medium`).

---

## Priorities

Standard: `Blocker` `10001`, `Urgent` `1`, `High` `2`, `Medium` `3` (default),
`Low` `4`.

The board also carries sentiment-style priorities that are **not** severity —
`Advocate` `11008`, `Positive` `11009`, `Neutral` `11010`, `Negative` `11011`,
`Escalated` `11012`. Don't set these thinking they mean urgency.

---

## Customer/s options

`customfield_10108` is a multiselect with ~150 options — too many and too volatile to
mirror here. Fetch the current list from `getJiraIssueTypeMetaWithFields`.

Ones that recur in this account's work:

| Customer | Option id |
|---|---|
| GE HealthCare | `11867` |
| UWash - NACC | `10319` |
| UPenn | `10225` |
| UCalLosAngeles (UCLA) | `10245` |
| UCalSanFran (UCSF) - TrackTBI | `10217` |
| UCalSanFran (UCSF) - ADCC | `10215` |
| FloreyInst | `10176` |
| UNewSouthWales (UNSW) | `10224` |
| USoCal - DNI (USCDNI) | `10226` |
| Emory University | `11798` |
| Internal | `11626` |

Naming is inconsistent by design — abbreviations sit in parentheses (`UCalSanFran
(UCSF)`), some customers are split per lab or per cloud (`Stanford - Yeatman`,
`BayerGermany (Bayer GCP)` vs `BayerGermany  (FW GCP)`, note the double space). Match
on the option **id**, never on a name you reconstructed.

---

## Re-deriving

```
getJiraProjectIssueTypesMetadata  cloudId=<id> projectIdOrKey=GEAR
getJiraIssueTypeMetaWithFields    cloudId=<id> projectIdOrKey=GEAR \
                                  issueTypeId=10029 requiredFieldsOnly=false
```

`requiredFieldsOnly` defaults to **true** and will return only `project` + `summary`,
which looks like a broken response if you were expecting the full screen. Set it to
`false`. Also cheap: `getJiraIssue` on a real ticket with `expand: "names"` gives the
`customfield_XXXXX` → label map for fields actually in use.
