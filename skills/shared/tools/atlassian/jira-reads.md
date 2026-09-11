---
type: Reference
title: Jira Reads
description: How to read Jira tickets and run complete JQL scans through the MCP connector — the search truncation, the two-ends completeness trick, and the response gotchas that silently mislead.
tags: [atlassian, jira, jql, reads]
timestamp: 2026-08-17T00:00:00Z
---

# Jira Reads

Reading tickets and running JQL that you can trust. Access setup, the unstable tool
namespace, cloudId: `mcp-access.md`. GEAR field ids: `gear-board-fields.md`.

## Contents
- There is no REST route
- Reading one ticket
- JQL scans and the truncation trap
- The two-ends trick
- Response gotchas
- Attachments

---

## There is no REST route

Prior notes across the knowledge base say "if the MCP search truncates, re-run the
query over REST." **That route does not exist on this machine.** Checked and empty
(2026-08-17):

| Checked | Result |
|---|---|
| `~/.atlassian-env`, `~/.netrc`, `~/.config/atlassian*`, `~/.config/jira*` | none exist |
| `acli` / `jira` / `jira-cli` binaries | not installed |
| macOS keychain (`jira`, `flywheel-io.atlassian.net`) | no entries |
| `JIRA_*` / `ATLASSIAN_*` / `CONFLUENCE_*` env vars | unset |

The claude.ai connector is the single path. Everything below works within it.
Provisioning an API token is a credentials decision, not a build — treat "get REST
access" as a request to a human, not a task to attempt.

---

## Reading one ticket

`getJiraIssue` with `cloudId` + `issueIdOrKey`. Defaults return a useful subset
(summary, description, status, issuetype, priority, labels, assignee, dates).

- `fields: ["*all"]` for every field including custom ones.
- Include `"comment"` in `fields` to get comments in `fields.comment.comments` —
  they are **not** returned by default, and the ticket's real decision record is
  usually in them.
- `expand: "renderedFields"` for HTML-rendered descriptions when the raw body is
  hard to read.
- `expand: "names"` maps `customfield_XXXXX` → human label, which beats memorizing ids.
- `responseContentFormat: "markdown"` for readable bodies; `"adf"` for fidelity.

**Read the comments before classifying any ticket.** The title lies, and prior
automated runs have completed work without transitioning the ticket.

**These responses land straight in context — there is no file to redirect to.** So
pass the tightest `fields` list that answers your question and keep `maxResults` low.
Reach for `*all` when you actually need the custom fields, not by default; a handful
of `*all` reads will eat a scan's entire budget.

---

## JQL scans and the truncation trap

`searchJiraIssuesUsingJql` **truncates and cannot paginate.** It has returned 5
issues regardless of `maxResults` (2026-08-12) and 7 (2026-08-17), so treat the exact
cap as unknown and moving. `hasNextPage` comes back `false` and `endCursor` `null`
even when `remainingCount` is nonzero.

**Always read `remainingCount`.** A result set that looks complete is not proof of
completeness. A scan that stops at the cap silently drops the rest of the sprint, or
the rest of an epic's children — and reports the same shape as a correct result.

**Get the true total in one call: pass `searchResultMode: "all"`.** The response then
carries `totalCount` alongside the (still truncated) `nodes`, so you know immediately
how many you're missing instead of inferring it. Cheapest completeness check available —
use it on every scan that has to be complete.

Re-confirmed 2026-08-17: cap is **5**, and pagination is dead **even at
`maxResults: 50`** (`hasNextPage: false`, `endCursor: null`, `remainingCount: 2`,
`totalCount: 7`). Raising `maxResults` does nothing.

**Counter-observation 2026-09-08: the cap did not appear.** `parent = "GEAR-14843"` with
`searchResultMode: "all"` and `maxResults: 50` returned **14 nodes against `totalCount:
14`** — no truncation, `hasNextPage: false` with nothing missing. ASC and DESC runs held the
identical key set. The tool schema now also carries a `nextPageToken` parameter, which the
August runs did not have, so the connector looks to have gained real pagination.

Treat the cap as **unknown and possibly lifted**, not as a fixed 5. Nothing above is retired:
keep passing `searchResultMode: "all"` and keep reading `totalCount`, because that is what
told us the result was complete. The two-ends trick costs one cheap call and remains the
proof — just do not pre-emptively slice an epic-sized query on the assumption it will
truncate.

---

## The two-ends trick

The reliable completeness workaround, proven 2026-08-14:

1. Run the query `ORDER BY <field> DESC`.
2. Run the same query `ORDER BY <field> ASC`.
3. Union the two result sets.

If the two pages **overlap**, the union is provably complete and you can show the
arithmetic: 5 + 5 − 2 overlap = 8 = 5 + `remainingCount`. State that reconciliation
in your output instead of an unverified count.

It breaks when the true total exceeds roughly 2× the cap. Past that, slice the query
(by status, by `updated` window, by subrange) and union the slices — and say in the
report that you did, so nobody reads the number as a single clean scan.

---

## Response gotchas

- **Comment bodies are ADF dicts** under `body`, not markdown, unless you ask for
  markdown. `renderedBody` stays empty even with `expand: "renderedFields"`. To pull
  text out of ADF:
  ```bash
  jq '[.fields.comment.comments[] | {author: .author.displayName,
      text: [.body.content[]?.content[]?.text] | join(" ")}]' response.json
  ```
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

**The connector has no attachment tool, and the REST fetch it was documented against
is unavailable.** Ticket attachments are effectively unreachable — flag them as an
open item rather than guessing at their contents.

If credentials are ever provisioned, the shape was: ids via `fields=attachment`, then
`/rest/api/3/attachment/content/<id>`. Zips have held whole repos; docx needs
`textutil -convert txt` to read. This worked headless on 2026-07-14 (GEAR-14987) and
the route was lost on 2026-08-17.
