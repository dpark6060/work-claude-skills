---
type: Procedure Reference
title: Calendar Productive-Time Analysis
description: How to pull the quarter's Outlook calendar, classify meetings per client, and derive real productive hours.
tags: [capacity, outlook, calendar, meetings]
timestamp: 2026-09-17T00:00:00Z
---

# Calendar Productive-Time Analysis

> **Load when:** computing productive hours or attributing meeting load to a client.

Produces two numbers: **productive hours per week**, and **meeting hours per client**. The first
feeds weeks-to-finish; the second feeds allocation burn.

# Pulling the quarter

`outlook_calendar_search` with `query: "*"`, `afterDateTime` = quarter start, `beforeDateTime` =
quarter end, `order: "oldest"`.

Traps that will bite:

- **25 events per page, hard cap.** A quarter runs to several hundred. Follow `nextOffset` until it
  stops appearing. Stopping at page one undercounts meeting load by an order of magnitude and makes
  the whole report optimistic.
- **`start`/`end` are `{dateTime, timeZone}` wall-clock pairs**, not UTC. Do not re-interpret
  `dateTime` as UTC — that shifts events across day boundaries and corrupts per-week totals.
- **Recurring series expand into individual occurrences.** Good — count them individually. But a
  series that ended mid-quarter still returns its past occurrences only, so don't extrapolate it
  forward.
- **Declined and cancelled events still come back.** Check the response status and drop anything
  declined; those hours are real working time.
- **All-day events are usually PTO or holidays**, not meetings. Route them to `pto_days`, and don't
  also count them as 8 meeting hours.

# Classification

Every event lands in exactly one bucket:

| Bucket | Signal | Effect |
|---|---|---|
| Client meeting | External attendee domain, or client name/prefix in subject | Burns that client's allocation; **zero throughput** |
| Internal — attributable | Subject or attendees tie it to one client's work | Same as above |
| Internal — general | Team syncs, all-hands, 1:1s, retros | Reduces productive time; charged to Internal, not a client |
| PTO / holiday | All-day, or subject matches PTO patterns | Removes the day from the quarter entirely |
| Focus / hold | Self-organized blocks with no other attendees | **Not a meeting.** Leave in productive time. |

Match client names via [client-map.md](client-map.md) — attendee email domain first, then subject
prefix, then the client's aliases. An event matching nothing is "internal — general"; if that
bucket exceeds ~25% of meeting load, list the top unmatched subjects in the report so the map can
be corrected.

# Deriving the numbers

```
meeting_hours_c   = Σ duration of events classified to client c
meeting_hours_int = Σ duration of internal-general events
pto_days          = count of PTO/holiday days (de-duplicated against workbook holidays)

real_productive   = (working_days − holidays − pto_days) × 8
                    − Σ meeting_hours_* − admin_hours
```

**Don't double-count holidays.** The workbook already subtracts its own holiday count. Only add
calendar PTO days that aren't already in that number.

Per-client productive share — the denominator for weeks-to-finish:

```
P_c = A_c − meeting_hours_c
```

Allocated hours minus the meeting time that burns them. `P_c` can go negative when a client is
nearly all standing meetings; that's a real finding — report it as "no build time left on this
client", not as a division-by-zero error.

# Reporting

Always give the report these three, in this order:

1. Total meeting hours for the quarter, and what fraction of raw available time that is.
2. The per-client split, so it's visible which client is consuming allocation without producing.
3. The largest recurring series by total quarterly cost — that's where tradeoff hours come from.
