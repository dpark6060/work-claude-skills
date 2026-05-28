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
