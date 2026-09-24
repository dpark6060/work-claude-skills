---
type: Reference
title: MR Descriptions
description: Channel rules for a GitLab MR description — ~150 words derived from the actual diff and log, what changed and why, linked not pasted.
tags: [gitlab, mr, description, writing]
timestamp: 2026-09-24T00:00:00Z
---

# MR Descriptions

Default mode: **Docs**. These rules win over the mode on shape and length. The MR creation
workflow lives in the `gitlab` skill (`references/create-mr.md`).

## Ceiling

~150 words. The diff carries the detail.

## Shape

- Open with what the MR does, one or two sentences. Lead with a fix or a behavior change
  over a refactor.
- Why, only if it's in the commit messages, the ticket, or the conversation. Never invent
  motivation.
- Notable files or areas touched, as `path/file.py`, only where a reviewer needs pointing.
- Link the ticket by key and anything the reviewer should check. Don't recap the commits.
- GitLab renders mermaid. A diagram earns its place only for a changed flow.
