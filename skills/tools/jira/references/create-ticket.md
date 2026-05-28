# Jira: Create a New Ticket

Create a new ticket on the GEAR board. Follow each phase in order.

---

## Phase 1 — Gather Required Information

Collect the following before drafting anything. If the user has not provided a value, ask. Do not guess or omit required fields.

| Field | Required | Source |
|---|---|---|
| Summary (title) | Yes | User |
| Issue type | Yes | User (Task / Bug / Story) |
| Description | Yes | User |
| Assignee | Yes | Default to yourself (`5d88bebcc7d4e30dc282e6e0`) unless told otherwise |
| Customer | Yes | User — must match a valid option (e.g. `"UWash - NACC"`) |
| Labels | Yes | Always include `"Hourly"` + the client name as a label (see label normalization note below) |
| Epic / parent | If given | User — accept as a ticket key (e.g. `GEAR-7595`) |
| Sprint | Auto | Query the active sprint (see Phase 2) |
| Billable | If known | See note below |

**Label normalization:** For multi-word customer names, use the short form as the label (e.g. `"NACC"` not `"UWash - NACC"`). Check existing GEAR tickets for that customer to confirm the established label convention before creating. Check `.learnings/LEARNINGS.md` — confirmed label forms may already be recorded there.

**Billable field:** The custom field ID for "billable" has not been confirmed. Before setting it, run:
```
mcp__atlassian__getJiraIssueTypeMetaWithFields(
    cloudId="flywheelio.atlassian.net",
    projectKey="GEAR",
    issueTypeName="Task"
)
```
Search the response for a field named "billable" or similar to get its `key` (e.g. `customfield_XXXXX`) and the accepted values.

---

## Phase 2 — Find the Active Sprint

Query the active sprint for the GEAR board before creating the ticket. Do not hardcode a sprint ID — sprints rotate quarterly.

Use `mcp__atlassian__searchJiraIssuesUsingJql` with:
```
jql: "project = GEAR AND sprint in openSprints()"
fields: ["customfield_10021"]
maxResults: 1
```

Extract the sprint `id` (integer) from `customfield_10021[0].id` on any returned issue. Use that ID when creating the ticket.

If no active sprint is found, omit the sprint field and note it to the user.

---

## Phase 3 — Draft and Confirm

Present the proposed ticket to the user before creating it:

> **Summary:** `<summary>`
> **Type:** `<type>`
> **Assignee:** Parker
> **Customer:** `<customer>`
> **Labels:** `<labels>`
> **Sprint:** `<sprint name>`
> **Epic:** `<epic key>` (if provided)
> **Description:**
> ```
> <description>
> ```
>
> *Create this ticket, or would you like to change anything?*

Wait for explicit approval before proceeding.

---

## Phase 4 — Create the Ticket

```
mcp__atlassian__createJiraIssue(
    cloudId="flywheelio.atlassian.net",
    projectKey="GEAR",
    issueTypeName="<type>",
    summary="<summary>",
    description="<description>",
    contentFormat="markdown",
    assignee_account_id="<accountId>",
    parent="<epic key>",           # omit if no epic given
    additional_fields={
        "customfield_10108": [{"value": "<customer name>"}],
        "customfield_10021": {"id": <sprint id>},
        "labels": ["Hourly", "<client label>"]
    }
)
```

**Formatting the description:**
- Always pass `contentFormat: "markdown"`
- Use blank lines between paragraphs — do not use `\n` escape sequences
- Use `**bold**`, `` `code` ``, and `- bullet` markdown as needed
- Headings (`##`) are fine for multi-section descriptions

---

## Phase 5 — Confirm and Link

After creation, report back:
- The new ticket key (e.g. `GEAR-11710`)
- The direct URL: `https://flywheelio.atlassian.net/browse/<key>`

If the user is on a branch that maps to the new ticket, note they can update their branch or link
the ticket manually.

---

## Flywheel Conventions

1. Assign the ticket to the current user unless specified.
2. Ticket Types:
    - "Story": Tickets that require coding or an MR
    - "Task": Non-coding, non-MR work (e.g. create tech spec)
    - "Spike": An investigation to be carried out for information gathering. 
3. Ticket name (summary) take the convention: <EpicNickname>-<OptionalNumber> <Summary>
    Create a short nickname for the epic and if multiple related tickets are created
    where order is important add a number.  The number is not necessary.
Good:
```
# Two related tickets with a clear order:
SesSplit-1 Create Manifest
SesSplit-2 Update Parser

# Ticket with no required order:
SesSplit remove default content from readme.md
```

Bad:
```
# Tickets with no required order with unnecessary numbers:
SesSplit-1 Update Readme
SesSplit-2 Update Contributing
SesSplit-3 Update flywheel-sdk
```
4. always attach the tickets to the current active sprint.

  
