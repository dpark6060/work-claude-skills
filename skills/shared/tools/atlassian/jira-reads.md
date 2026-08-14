---
type: Runbook
title: "Jira: Read Issues Without Blowing Context"
description: Best practice for all Jira reads — download the raw response to a file and jq out the fields you need instead of pulling full issue payloads into context; includes the REST route, the MCP 5-issue search truncation, field-trimming rules for MCP reads, and known response gotchas.
tags: [jira, read, rest, jq, context, jql, mcp, shared]
timestamp: 2026-08-13T00:00:00Z
---

# Jira: Read Issues Without Blowing Context

Shared runbook for every skill that reads Jira. Point at this file; do not restate it.

Jira issue payloads are huge — a single issue with `fields=*all` runs thousands of
tokens of ADF noise, empty custom fields, and avatar URLs. A JQL search multiplies
that per result. **Best practice for every read: download the response to a file,
then jq out only the fields you need.** Never let a full raw payload land in context.

---

## Gotcha first: MCP JQL search truncates to 5 issues

**`searchJiraIssuesUsingJql` returns at most 5 issue nodes per response no matter what
`maxResults` you pass, and pagination is a dead end** — the response carries
`remainingCount: N` alongside `pageInfo.hasNextPage: false` and `endCursor: null`, so
there is no cursor to follow. (Verified 2026-08-12 against epic GEAR-14843, 13 children.)

**Consequence: any scan that needs the full result set must use the REST route below,
not MCP.** Never treat a 5-row MCP result as "these are all of them" — child scans,
duplicate detection, and epic enumeration all break silently on this.

Check `remainingCount` on every MCP search. If it is nonzero (or the answer depends on
completeness at all), re-run the query over REST.

If REST is genuinely unavailable, the MCP-only workaround is to run the same JQL
`ORDER BY created DESC` and again `ORDER BY created ASC` to grab both ends, then fill
the middle with explicit `created > "YYYY-MM-DD HH:MM" AND created < ...` windows until
`5 shown + remainingCount` reconciles with the total. Slow and error-prone — prefer REST.

---

## Preferred route: REST → file → jq

Host is `flywheelio.atlassian.net` (NOT `flywheel.atlassian.net` — that host returns
401 "Client must be authenticated"). Basic auth `davidparker@flywheel.io` : `$JIRA_TOKEN`
(env var, `ATATT…` API token).

```bash
OUT=$SCRATCHPAD/GEAR-1234.json   # scratchpad dir from your system prompt

curl -s -u "davidparker@flywheel.io:$JIRA_TOKEN" \
  "https://flywheelio.atlassian.net/rest/api/3/issue/GEAR-1234?expand=renderedFields&fields=summary,status,description,customfield_10108,labels,parent" \
  -o "$OUT"

jq '{key: .key, summary: .fields.summary, status: .fields.status.name,
    customer: .fields.customfield_10108, labels: .fields.labels,
    parent: .fields.parent.key}' "$OUT"
```

JQL search — same pattern, always with an explicit `fields` list and `maxResults`.
This route honors `maxResults`; MCP search does not:

```bash
curl -s -u "davidparker@flywheel.io:$JIRA_TOKEN" \
  --get "https://flywheelio.atlassian.net/rest/api/3/search/jql" \
  --data-urlencode 'jql=project = GEAR AND cf[10108] = "UWash - NACC" AND type = Epic' \
  --data-urlencode "fields=summary,status,labels" \
  --data-urlencode "maxResults=25" \
  -o "$OUT"

jq '.issues[] | {key, summary: .fields.summary, status: .fields.status.name}' "$OUT"
```

Inspect an unfamiliar payload's shape before extracting, without dumping it:

```bash
jq 'paths(scalars) | join(".")' "$OUT" | sort -u | head -50   # what's in here?
jq '.fields | keys' "$OUT"                                     # top-level field names
```

---

## MCP reads: trim or don't

`getJiraIssue` / `searchJiraIssuesUsingJql` responses go **straight into context** —
there is no file to redirect to. So:

- Only use MCP reads for small, targeted lookups where you can pass a tight
  `fields` list (e.g. `fields: ["summary", "status"]`) and low `maxResults`.
- Never call `getJiraIssue` without a `fields` list. Never use `*all` via MCP.
- Never use MCP search when the answer depends on seeing every match — see the
  5-issue truncation above.
- If you need the description, comments, changelog, or "everything about this
  ticket" — use the REST route above instead.

---

## Response gotchas (verified)

- **`renderedFields` only populates for fields you explicitly list** in the
  `fields` param. `description` must be listed or `renderedFields.description`
  comes back empty. Use `renderedFields.description` (HTML) for a readable body;
  raw `fields.description` is ADF.
- **Comment bodies are ADF dicts** under `body` — `renderedBody` stays empty even
  with `expand=renderedFields`. Extract text from ADF with jq:
  ```bash
  jq '[.fields.comment.comments[] | {author: .author.displayName,
      text: [.body.content[]?.content[]?.text] | join(" ")}]' "$OUT"
  ```
- **`updated` is NOT the close time.** Pull `expand=changelog` before making any
  timeline claims about when a ticket moved status.
- **Attachments** have no MCP tool. Get ids via `fields=attachment`, then:
  ```bash
  curl -s -u "davidparker@flywheel.io:$JIRA_TOKEN" \
    "https://flywheelio.atlassian.net/rest/api/3/attachment/content/<attachment_id>" -o <file>
  ```
  Works for zips and docx (`textutil -convert txt` to read docx).
- GEAR **does** have an Acceptance Criteria field — `customfield_11394`, textarea, on
  Story and Task (live createmeta, 2026-08-13). An earlier version of this file claimed
  there was none; that was convention, not schema. Plenty of older tickets still carry
  AC inline in the description, so when reading, check both.

Tool prefix, cloudId, accountId, and ADF write rules: `mcp-access.md` in this directory.
GEAR field / option / issue-type / priority ids: `gear-board-fields.md`, same directory.
