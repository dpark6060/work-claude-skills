# Jira Skill — Error Log

MCP errors, unexpected responses, and their resolutions. Add entries as they occur.

---

## Format

```
### YYYY-MM-DD — <brief title>
**Tool:** `mcp__claude_ai_Atlassian__<tool_name>`
**Error:** <exact error message or behavior>
**Resolution:** <what fixed it>
```

---

<!-- Add entries below -->

### 2026-08-13 — Sprint field rejects object shape on create
**Tool:** `mcp__claude_ai_Atlassian__createJiraIssue`
**Error:** `Bad Request. {"errors":{"customfield_10021":"Specify a valid value for Sprint"}}` when passing `"customfield_10021": {"id": 3555}` in `additional_fields` (the shape shown in `references/create-ticket.md`).
**Resolution:** Pass the bare integer: `"customfield_10021": 3555`. Created GEAR-22872 successfully. `create-ticket.md` corrected.
