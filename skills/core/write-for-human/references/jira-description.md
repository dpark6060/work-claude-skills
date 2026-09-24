---
type: Reference
title: Jira Ticket Descriptions
description: Channel rules for a Jira ticket description — written for whoever picks the work up; the reproduction or decision, linked sources, no narrative, no mermaid.
tags: [jira, ticket, description, writing]
timestamp: 2026-09-24T00:00:00Z
---

# Jira Ticket Descriptions

Default mode: **Docs**. These rules win over the mode on shape and length. Field and
formatting mechanics live in the `jira` skill (`references/create-ticket.md`).

## Shape

The reader is whoever picks the work up. Give them the task and what they need to start.

- Open with the task in one or two sentences: what needs doing and why.
- Then the reproduction, the decision, or the acceptance criteria. Not the story of how
  the ticket came to exist.
- Link the source (Slack permalink, commit, Confluence page, MR). Don't paste it.
- Headings (`##`) are fine for a multi-section description. A two-line ticket needs none,
  and needs no executive summary on top of itself.
- Jira does not render mermaid. Use a plain ASCII diagram or link out.

## Written as the user

When a skill writes the description on the user's behalf (`meeting-tickets`), it must read
as if the user typed it: no sign-off, no tool-generated language, no automation fingerprint.
