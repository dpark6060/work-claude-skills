---
type: Reference
title: Jira Comments
description: How to write a Jira comment a human will actually read — the shape, the length ceiling, the sign-off, and the ADF/markdown mechanics of addCommentToJiraIssue.
tags: [jira, comment, writing, style]
timestamp: 2026-08-17T00:00:00Z
---

# Jira Comments

Read [outbound-core.md](outbound-core.md) first — length, voice, and the summarize-and-link
rule live there. This file is Jira-specific.

## What a comment is for

**A comment is an activity note in a permanent record, not the deliverable.** Someone
opens this ticket in six months and needs to know: what happened, what it means, what's
still open, where the detail lives.

The full findings go in the local output file. The comment points at it.

**Exception:** paste the deliverable inline only when the user explicitly asked for that
("post the full findings to the ticket").

## Shape

Not a rigid template — vary it to fit. But it covers these, in roughly this order:

```
<The finding, one or two lines. Lead with what's broken or surprising.>

<2-5 tight bullets or a small table: the evidence, each with its number and source.>

<What's still open / what someone else has to do. Only if there is something.>

Full findings: <path to the output file>

— <skill> (<auto-posted | posted with David's approval>, <date>). Reopen/ping if this misses something.
```

Rules on top of that:

- **Bold the verdict**, not the labels. `**Production still can't run headless.**` —
  not `**Status:** production cannot run headless`.
- **A small table beats six bullets** when you're comparing two things (before/after,
  dev/prod, expected/actual). Three columns max, or it wraps badly.
- **Sources inline, not in a trailing block.** `f28ada67 (today 13:09)` in the sentence
  reads better than a Sources section nobody scrolls to. Keep a Sources list only when
  there are 4+ distinct sources or the ticket is a formal record.
- **One output-file path, at the end, once.**
- **Keep the sign-off.** It marks the comment as bot-posted so nobody reads it as a
  human sign-off. Say which mode: auto-posted vs posted with approval.

**Sign-off exception:** `meeting-tickets` writes ticket *descriptions* deliberately as
David, with no automation fingerprint — a sign-off there would defeat the point. The
sign-off rule applies to comments a skill posts in its own voice, not to content authored
on the user's behalf. If you're writing as the user, drop it.

## Corrections

When you're correcting your own earlier comment, say so in the first line and link the
comment you're correcting. Don't silently contradict a comment above you in the thread —
someone reading top to bottom needs to know which one won.

Do not edit a posted comment to change a conclusion. Post a new one. Editing is for
typos and broken formatting only (see `commentId` below).

## Mechanics of `addCommentToJiraIssue`

**`contentFormat: "markdown"` works.** Older notes in this knowledge base claim the tool
has no `contentFormat` param and that you must write plain prose — that is **wrong**,
verified 2026-08-17. Pass `contentFormat: "markdown"` and you get real markdown: tables,
bullets, code spans, bold.

- **Tables render.** Pipe syntax, standard markdown.
- **Code spans and fenced blocks render.** Use them for paths, field ids, SHAs, URLs.
- **Do not nest `**bold**` inside a code span** — `` `a.**b**.c` `` prints the literal
  asterisks. Pick one.
- **Bodies come back as ADF on read**, not markdown, unless you pass
  `responseContentFormat: "markdown"` on the read call.
- **`commentId` updates an existing comment** instead of adding one. Use it to fix
  formatting you got wrong; do not use it to rewrite history.
- Don't hand-write `\n` escapes. Write real newlines.

Access setup, cloudId, and the unstable tool namespace:
[../tools/atlassian/mcp-access.md](../tools/atlassian/mcp-access.md).

## Before you post

- Would the reader learn something they don't already have on screen? If no, don't post.
- Is every number attached to where it came from?
- Is the longest sentence doing one job?
- Did you delete the preamble and the wrap-up?
- Is it under a screen?
