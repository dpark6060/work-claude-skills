# Clockify Skill Learnings

Observations from real usage. Summarize this file at the start of each session — don't just read it.

---

<!-- Entry format:
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: OPEN/RESOLVED
**Area:** which part of the skill
**Summary:** one-line description
**Details:** what happened
**Suggested action:** what to do differently
-->

## [2026-05-22] | Priority: HIGH | Status: RESOLVED
**Area:** SDK method discovery / pagination
**Summary:** SDK has `get_current_workspace_projects` and `get_workplace_clients` (not `get_projects`/`get_clients`); both return only the first page by default.
**Details:** Bulk-fill workflows that need to find a client/project by name will silently miss matches because the default response is capped at 50 items. The Clockify class's documented method names differ from what the skill README implies.
**Suggested action:** When searching across all clients/projects, page manually via `cl.client.make_call(endpoint=..., params={"page": N, "page-size": 200})` and loop until the page returns fewer items than the page size. Don't rely on the SDK wrapper methods for full-workspace scans.

## [2026-05-22] | Priority: MED | Status: RESOLVED
**Area:** Bulk entry posting workflow
**Summary:** For multi-week schedules, batching all entries into a single script and posting sequentially is much faster than per-entry MCP calls, and the SDK is well-behaved enough that overlap pre-checks aren't needed if the schedule is built around a fresh inventory.
**Details:** Posted 73 entries across 3 weeks in one script run with zero failures. The key was pulling the existing-entry inventory once up-front, then designing slots that avoid existing entries by construction.
**Suggested action:** For bulk fills (>10 entries), inventory existing entries once, design the full schedule to avoid them, then post in a single script. Reserve `check_overlap.py` for one-off entries where the user-provided times might collide with existing work.

## [2026-06-11] | Priority: HIGH | Status: RESOLVED
**Area:** batch_submit.py / archived tasks
**Summary:** Clockify rejects entries posted to tasks marked DONE with a vague 400 ("Can't save, required fields are missing or archived"); the workspace cache does not record task status, so stale caches happily resolve to archived tasks.
**Details:** A 45-entry batch posted 41/45; the 4 failures all targeted NACC tasks GEAR-7726 and GEAR-7047, which had been set to DONE in Clockify after the May 22 cache was built. Verified live via `GET workspaces/{ws}/projects/{pid}/tasks?is-active=false` (status=DONE). Active sibling task GEAR-7595 posted fine.
**Suggested action:** Before a bulk fill that targets ticket-specific tasks, spot-check that those tasks are still ACTIVE on the live API (one call per project, `is-active=false` shows the archived set). For work on a Jira ticket whose Clockify task is DONE, fall back to an evergreen task ('Customer Engagement', 'Support', 'Other') and keep the ticket ref in the description. New helper: `scripts/print_failures.py INTENT_JSON [LOG]` maps batch_submit failure output back to the intent entries (pipe-friendly, reads stdin).

## [2026-06-11] | Priority: HIGH | Status: RESOLVED
**Area:** Calendar integration / day-fill workflow
**Summary:** Clockify's public API cannot see the Outlook events shown in its UI (all calendar endpoints 404); the Microsoft 365 MCP connector (`mcp__claude_ai_Microsoft_365__outlook_calendar_search`) reads the user's Outlook directly and is now the mandatory first step for day fills.
**Details:** Probed workspaces/{ws}/calendar, /calendar/events, user calendar-events, /integrations - all 404 with code 3000. The M365 search returns meetings plus context Clockify lacks: cancellations (isCancelled), Lunch and Focus Time blocks, tentative status, and a daily "Outside working hours" oof event. First use immediately caught a billable NACC sync entry logged for a meeting that had been canceled to preserve contract hours.
**Suggested action:** Follow the "Day fills: calendar-first scheduling (MANDATORY)" section in SKILL.md: calendar first, skip canceled, meetings by client (internal -> SSE Admin/Team Meetings, client-related -> client's Project Management task), coding inside the oof window, top up to exactly 8.00h/day with one SSE Admin/Other entry at end of day.

## [2026-06-11] | Priority: HIGH | Status: RESOLVED
**Area:** Rework/mutation workflow
**Summary:** The user moves entries in the Clockify UI between conversation turns; a mutation batch built from stale state will half-apply and create overlaps.
**Details:** Two rework batches in one session each found ~1/3 of target entries missing from their expected timestamps because the user had dragged them in the UI after the last fetch. One op landed inside a user-rearranged day and produced an overlapping entry.
**Suggested action:** Re-fetch live entries immediately before EVERY mutation batch (not at planning time), match by (start, description-prefix), and treat zero-match as "user moved it - re-inspect the day" rather than an error to force. After applying, always run a full audit (total=480min/day, SSE Other >= 60min, gaps <= 25min in working hours, no overlaps) and fix what it flags.
