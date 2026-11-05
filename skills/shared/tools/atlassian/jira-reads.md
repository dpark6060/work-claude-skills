---
type: Reference
title: Jira Reads
description: How to read Jira tickets, comments, and attachments and run complete JQL scans through the Atlassian MCP, plus the response gotchas that silently mislead.
tags: [atlassian, jira, jql, reads]
timestamp: 2026-11-04T00:00:00Z
---

# Jira Reads

Reading tickets and running JQL that you can trust. Access setup, the unstable tool
namespace, cloudId: `mcp-access.md`. GEAR field ids: `gear-board-fields.md`.

## Contents

- There is no REST route
- Reading one ticket
- JQL scans and pagination
- Response gotchas
- Attachments

---

## There is no REST route

There are no Jira API credentials on this machine: no `~/.atlassian-env`, `~/.netrc`,
`acli`/`jira` binaries, keychain entries, or `JIRA_*`/`ATLASSIAN_*` env vars (checked
2026-08-17). The Atlassian MCP is the single path. Since 2026-11-04 it covers pagination
and attachments, so nothing needs REST.

---

## Reading one ticket

`getJiraIssue` with `cloudId` + `issueIdOrKey`. The default `compact` view returns a
useful subset (summary, description, status, issuetype, priority, labels, assignee, dates).

- `view: "evidence"` adds custom fields, mapped to human labels under
  `fields.customFields`, plus issue links. `view: "full"` returns everything.
- `fields: ["customfield_10021", ...]` fetches specific custom fields.
- **Comments are not in `getJiraIssue`.** It reports a count only. Read them with
  `listJiraIssueComments`, which pages with `startAt` until `isLast`.
- Bodies default to markdown. See `mcp-access.md` for when they come back as HTML.

**Read the comments before classifying any ticket.** The title lies, and prior
automated runs have completed work without transitioning the ticket.

**These responses land straight in context — there is no file to redirect to.** So
pass the tightest `fields` list that answers your question and keep `maxResults` low.
Reach for `view: "full"` only when you need it.

---

## JQL scans and pagination

`searchJiraIssuesUsingJql` **paginates** (confirmed 2026-11-04). `maxResults` is honored up
to 100. Each page returns `nextPageToken` and `isLast`. Pass the token back to get the next
page, and stop when `isLast` is true.

For the total, pass `searchResultMode: "count"`. It returns `totalCount` and no issues.
Use it when a downstream step needs the number, not on every scan.

The old connector truncated every search to 5 issues and its pagination was dead
(2026-08-12 to 2026-08-17). The fix then was the "two-ends trick": run the query ASC and
DESC and union the results. Don't use it now. If a search ever stops paging again, check
`mcp-name-history.md` for a server change before working around it.

---

## Response gotchas

- **Standard fields named in `fields` can come back missing.** `fields: ["created",
  "reporter"]` returned neither on 2026-11-04. Adding `fieldsByKeys: true` fixed it.
- **`renderedFields` only populates for fields you explicitly list** in `fields`.
  `description` must be in the list or `renderedFields.description` comes back empty —
  which reads as "this ticket has no description."
- **`updated` is not a close time.** It moves on any edit, including a bot touching a
  field. Don't infer "finished on" from it.
- **Group `id` vs `_id`** — unrelated to Jira, but the same class of silent-empty
  mistake shows up in Flywheel finders; see the SDK finder rules.
- A zero-result JQL is a **red flag, not "no work."** Status names are
  workflow-specific. Drop the `status in (...)` clause, look at what statuses
  actually come back, and adjust. Confirm the count resembles the real board before
  trusting it.
- A zero-result run in a *headless* job is more likely a connector-name/allowlist
  problem than an empty board. Check that first (`mcp-access.md`).

---

## Attachments

Reachable again through the MCP (2026-11-04):

1. `getJiraIssue` with `fields: ["attachment"]` lists each attachment's numeric `id`,
   `filename`, `size`, and `mimeType`.
2. `executeRead(name="downloadJiraIssueAttachment", inputs={cloudId, attachmentId,
   outputPath})` returns a short-lived URL and a `downloadCommand`.
3. Run that command from the shell to save the file.

The download itself has not been run yet. Zips have held whole repos. A docx needs
`textutil -convert txt` to read.
