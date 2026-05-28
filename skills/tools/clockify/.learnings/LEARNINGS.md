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
