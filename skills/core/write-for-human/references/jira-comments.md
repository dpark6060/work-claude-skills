---
type: Reference
title: Jira Comments
description: Channel rules for a Jira comment a human will read — what it is for, its shape, the one-screen ceiling, the sign-off, and how to correct an earlier comment.
tags: [jira, comment, writing, style]
timestamp: 2026-09-24T00:00:00Z
---

# Jira Comments

Default mode: **Email** (a comment lands as an inbox notification). These rules win over the
mode on shape, length, and sign-off. Tool mechanics (`contentFormat: "markdown"`, `commentId`,
the `\n` trap) live in the `jira` skill and `~/.claude/skills/shared/tools/atlassian/mcp-access.md`.

## What a comment is for

**A comment is an activity note in a permanent record, not the deliverable.** Someone
opens this ticket in six months and needs to know: what happened, what it means, what's
still open, where the detail lives.

The full findings go in the local output file. The comment points at it.

**Exception:** paste the deliverable inline only when the user explicitly asked for that
("post the full findings to the ticket"), or the calling skill's output *is* the comment
(`pm-update`).

## Ceiling

~200 words, one screen. Over that, the findings file gets it. Under the ceiling is not a
target: a three-line comment that says the thing beats a 200-word one that says it twice.

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
- **Don't restate the ticket.** The reader has it open.
- **Keep the sign-off.** It marks the comment as bot-posted so nobody reads it as a
  human sign-off. Say which mode: auto-posted vs posted with approval.

**Sign-off exception:** text written *as the user* (e.g. `meeting-tickets` descriptions)
carries no sign-off. The rule applies to comments a skill posts in its own voice.

## Corrections

When you're correcting your own earlier comment, say so in the first line and link the
comment you're correcting. Don't silently contradict a comment above you in the thread —
someone reading top to bottom needs to know which one won.

Do not edit a posted comment to change a conclusion. Post a new one. Editing is for
typos and broken formatting only.

## Comment alongside a transition

One or two lines saying what moved and why is usually the whole comment. Do not narrate
the transition you just made.
