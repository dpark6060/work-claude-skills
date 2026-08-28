# Jira Skill — Learnings

Field IDs, sprint conventions, label forms, and MCP behavior accumulated from real usage.
Update this file after each session where something new is discovered.

---

## Confirmed Field IDs

**The field table moved.** Every GEAR field id, option id, issue-type id, priority id, and
write shape now lives in one place:
`~/.claude/skills/shared/tools/atlassian/gear-board-fields.md`. Do not re-add a table here —
record only new *findings* below.

### 2026-08-13 — live createmeta on GEAR (Story 10029 + Task 10020), two long-open questions closed

Call: `getJiraIssueTypeMetaWithFields`, `cloudId=flywheelio.atlassian.net`,
`projectIdOrKey=GEAR`, `requiredFieldsOnly=false`, paged. Story and Task each expose the
**same 24 create-screen fields**; only `project` and `summary` are required.

- **Acceptance Criteria EXISTS: `customfield_11394`, name "Acceptance Criteria", type
  `textarea`** — on both Story and Task. This settles the contradiction: `meeting-tickets`'
  tracker was right, and the old "GEAR has no AC field, AC lives inline in the description"
  line in `shared/tools/atlassian/jira-reads.md` was describing convention, not schema. That
  file has been corrected. Older tickets still carry AC inline, so read both places.
- **There is NO Billable field on GEAR.** All 24 fields enumerated; nothing named billable or
  similar. The "not confirmed, go find it" note is retired from `SKILL.md` and
  `references/create-ticket.md`. Billable-ness is carried by the `Hourly` / `Fixed` / `SOW`
  labels, consumed by the Jira→Clockify sync.
- **Story Points (`customfield_10016`) is NOT on the GEAR create screen** for Story or Task —
  the previous "Confirmed" entry in this file was wrong for create calls. Do not pass it on
  create.
- Also observed: Flagged `customfield_10027` (options Impediment=10019, "Option 1"=10118),
  Design `customfield_11286`, Zendesk Ticket IDs `customfield_11292`, Zendesk Ticket Count
  `customfield_11293`, Vulnerability `customfield_11296`, Start date `customfield_10015`,
  Development `customfield_10000`. Priorities: Blocker 10001, Urgent 1, High 2, Medium 3
  (default), Low 4, plus a sentiment set (Advocate 11008 … Escalated 11012). Issue types:
  Task 10020, Epic 10021, Subtask 10022, Story 10029, Bug 10030, Spike 10098,
  Vulnerability 11318. Project id 10020, team-managed (`simplified: true`) → epics attach
  via the system `parent` field, no epic-link custom field.

---

## Label Conventions

| Customer | Label to use |
|---|---|
| _Add entries here as confirmed from existing tickets_ | |

---

## Sprint Notes

- Sprint IDs rotate quarterly — always query `openSprints()` rather than hardcoding.
- Use `searchJiraIssuesUsingJql` with `fields: ["customfield_10021"]` and `maxResults: 1` to get the current sprint ID.

---

## MCP Behavior Notes

- Sprint on create (`customfield_10021` in `additional_fields`) must be a **bare integer** (`3555`), not `{"id": 3555}` — the object shape 400s with "Specify a valid value for Sprint" (2026-08-13, GEAR-22872).

- `addCommentToJiraIssue` does not accept a `contentFormat` parameter — keep comments as plain prose.
- `createJiraIssue` and `editJiraIssue` require `contentFormat: "markdown"` to prevent literal `\n` in descriptions.

## [2026-08-18] | Area: tool namespace | Status: RESOLVED
**Summary:** Every code example in this skill called `mcp__atlassian__*` — a namespace that does NOT exist in a normal claude.ai session. Replaced all 12 with an `ATL__` placeholder and added a resolve-the-prefix section to SKILL.md.
**Details:** Verified live 2026-08-18: `ToolSearch` on all three spellings returns a schema for `mcp__claude_ai_Atlassian_Rovo__getJiraIssue` ONLY. `mcp__atlassian__*` and `mcp__claude_ai_Atlassian__*` both resolve to nothing. So the skill was instructing calls against a dead prefix. Three spellings are known: `mcp__claude_ai_Atlassian_Rovo__` (live, post 2026-08-17 server rename), `mcp__claude_ai_Atlassian__` (pre-rename), `mcp__atlassian__` (local MCP server if registered).
**Suggested action:** Resolve the prefix with one ToolSearch before the first call; treat `ATL__` in this skill as a placeholder. A permission error naming a tool is an allowlist mismatch in the CALLING WRAPPER's `--allowedTools`, not a connector outage — and no skill can fix that, since the harness enforces the allowlist before skill code runs. Wrappers need an `ATLASSIAN_PREFIXES` array listing every spelling (`run_quest_sweep.sh` and `run_draft_fill.sh` both have one as of 2026-08-18).
