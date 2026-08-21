# Jira Skill — Learnings

Field IDs, sprint conventions, label forms, and MCP behavior accumulated from real usage.
Update this file after each session where something new is discovered.

---

## Confirmed Field IDs

| Field | Jira key | Notes |
|---|---|---|
| Customer | `customfield_10108` | Confirmed — format: `[{"value": "<name>"}]` |
| Sprint | `customfield_10021` | Confirmed — format: `{"id": <int>}` |
| Story Points | `customfield_10016` | Confirmed — format: number |
| Billable | _not confirmed_ | Run `getJiraIssueTypeMetaWithFields` to locate before use |

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

- `addCommentToJiraIssue` does not accept a `contentFormat` parameter — keep comments as plain prose.
- `createJiraIssue` and `editJiraIssue` require `contentFormat: "markdown"` to prevent literal `\n` in descriptions.

## [2026-08-18] | Area: tool namespace | Status: RESOLVED
**Summary:** Every code example in this skill called `mcp__atlassian__*` — a namespace that does NOT exist in a normal claude.ai session. Replaced all 12 with an `ATL__` placeholder and added a resolve-the-prefix section to SKILL.md.
**Details:** Verified live 2026-08-18: `ToolSearch` on all three spellings returns a schema for `mcp__claude_ai_Atlassian_Rovo__getJiraIssue` ONLY. `mcp__atlassian__*` and `mcp__claude_ai_Atlassian__*` both resolve to nothing. So the skill was instructing calls against a dead prefix. Three spellings are known: `mcp__claude_ai_Atlassian_Rovo__` (live, post 2026-08-17 server rename), `mcp__claude_ai_Atlassian__` (pre-rename), `mcp__atlassian__` (local MCP server if registered).
**Suggested action:** Resolve the prefix with one ToolSearch before the first call; treat `ATL__` in this skill as a placeholder. A permission error naming a tool is an allowlist mismatch in the CALLING WRAPPER's `--allowedTools`, not a connector outage — and no skill can fix that, since the harness enforces the allowlist before skill code runs. Wrappers need an `ATLASSIAN_PREFIXES` array listing every spelling (`run_quest_sweep.sh` and `run_draft_fill.sh` both have one as of 2026-08-18).
