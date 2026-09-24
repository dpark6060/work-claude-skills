---
type: Reference
title: Slack Posts
description: Channel rules for a skill's Slack run report or nudge — one post, ~150 words plus the list, the "needs you" line, and the markdown gotcha that silently italicizes headings.
tags: [slack, writing, style, report]
timestamp: 2026-09-24T00:00:00Z
---

# Slack Posts

Default mode: **Chat**. These rules win over the mode on shape and length. Delivery
mechanics (target channel, lazy tool loading, Slack limits) live in the `report-to-slack` skill.

## How Slack differs from Jira

| | Jira comment | Slack post |
|---|---|---|
| Lifespan | permanent record | read once, scrolled past |
| Reader | someone auditing in 6 months | David on a phone, now |
| Needs citations | yes | only for the thing he'll act on |
| Needs the ask | no | **yes — what does he do about it?** |

A Slack post that reports without saying what needs a human is half a post.

## Shape

A run report is **one post**, not Chat mode's split thread.

```
**<Skill> — <what ran> — <date>**

<Outcome in one line, with the numbers.>

<The one thing worth knowing, 2-4 lines. Lead with broken/surprising.>

<Needs you: the decisions or actions only he can take. Skip if genuinely none.>

<Ranked list, if the skill produces one.>

<Output paths, one line.>
```

Keep it to roughly 150 words plus the list. If a finding needs more, it goes in the
file and the post links it.

## The markdown gotcha

**`slack_send_message` takes standard markdown, not Slack's classic mrkdwn.** So:

- `**bold**` → **bold**
- `*single asterisk*` → *italic*, NOT bold

A post written with `*Headings Like This*` renders every heading in italic. Verified
2026-08-17 by reading a post back: every `*bold*` came through as `_italic_`.

Tables, fenced code blocks, `~~strikethrough~~`, blockquotes, links, and headers all render.

## Don't

- Don't tease. "Top 3 below, full list in the file" is useless in a headless run where
  Slack is the only copy. Post the whole ranked list.
- Don't paste the findings file. Link it.
- Don't reformat a table into prose because it's Slack. Tables render.
- Don't repeat the run's numbers three times in different phrasings.
- Don't add "Let me know if you need anything else!"

## Post no matter what

A successful run, a nothing-to-do run, and a partial failure all get a message. A quiet
day has to stay distinguishable from a silent failure. If something failed, say what and
where the log is — do not bury it under the successes.
