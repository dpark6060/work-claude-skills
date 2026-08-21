---
type: Reference
title: Slack Posts
description: How to write a run report or nudge for Slack — read on a phone, skimmed once, never revisited; plus the markdown gotcha that silently italicizes your headings.
tags: [slack, writing, style, report]
timestamp: 2026-08-17T00:00:00Z
---

# Slack Posts

Read [outbound-core.md](outbound-core.md) first. This file is Slack-specific.

## How Slack differs from Jira

| | Jira comment | Slack post |
|---|---|---|
| Lifespan | permanent record | read once, scrolled past |
| Reader | someone auditing in 6 months | David on a phone, now |
| Needs citations | yes | only for the thing he'll act on |
| Needs the ask | no | **yes — what does he do about it?** |

A Slack post that reports without saying what needs a human is half a post.

## Shape

```
*<Skill> — <what ran> — <date>*

<Outcome in one line, with the numbers.>

<The one thing worth knowing, 2-4 lines. Lead with broken/surprising.>

<Needs you: the decisions or actions only he can take. Skip if genuinely none.>

<Ranked list, if the skill produces one.>

<Output paths, one line.>
```

Keep it to roughly 150 words plus the list. If a finding needs more, it goes in the
file and the post links it.

## The markdown gotcha

**The `slack_send_message` tool takes standard markdown, not Slack's classic mrkdwn.**
So:

- `**bold**` → **bold**
- `*single asterisk*` → *italic*, NOT bold

This bites. A post written with `*Headings Like This*` renders every heading in italic
and looks limp. Verified 2026-08-17 by reading a post back: every `*bold*` came through
as `_italic_`.

Also supported: tables, fenced code blocks with a language, `~~strikethrough~~`,
blockquotes, links, headers. 5000 chars per text element.

- Use `unfurl_app_links: true` when the post contains GitLab/Jira links you want
  previewed.
- Never put anything sensitive in a link query param.
- Cannot post to Slack Connect (externally shared) channels.

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

Self-DMs do not push-notify. A self-DM is a silent log, fine for ad-hoc, wrong for
anything that needs to be seen.
