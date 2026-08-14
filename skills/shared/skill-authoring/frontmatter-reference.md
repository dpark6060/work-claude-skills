---
type: Config Reference
title: Skill Frontmatter & Harness Controls
description: Every SKILL.md frontmatter field, the invocation-control flags, argument substitution, and dynamic context injection syntax.
tags: [skills, frontmatter, configuration]
timestamp: 2026-07-31T00:00:00Z
---

# Skill Frontmatter & Harness Controls

> **Load when:** writing or changing a skill's frontmatter, deciding who can invoke a skill,
> pre-approving tools, or injecting live command output into skill content. Companion to
> [claude-skills-best-practices.md](../claude-skills-best-practices.md) (the core rulebook).

# Schema

Every `SKILL.md` has two parts — frontmatter and a markdown body:

```yaml
---
name: skill-name            # Becomes /skill-name slash command
description: What it does and when to use it. Front-load the key use case.
---

# Your instructions here (markdown body)
```

## Field quick reference

| Field | Required | Notes |
|---|---|---|
| `name` | No (uses dir name) | Lowercase, hyphens, max 64 chars |
| `description` | **Recommended** | Max 1024 chars; truncated at ~250 chars in skill listing |
| `disable-model-invocation` | No | `true` = only user can invoke |
| `user-invocable` | No | `false` = only Claude invokes, hidden from `/` menu |
| `allowed-tools` | No | Pre-approve tools without per-use prompts |
| `context` | No | `fork` = run in isolated subagent |
| `agent` | No | Which subagent type when `context: fork` |
| `paths` | No | Glob patterns; skill auto-loads only for matching files |
| `model` | No | Model override for this skill |
| `effort` | No | `low`/`medium`/`high`/`max` |

There is no sanctioned `version` field — this repo versions skills with git.

# Examples

## Controlling invocation

```yaml
# Only the user can invoke (good for /deploy, /commit — side-effect commands)
disable-model-invocation: true

# Only Claude invokes (good for background reference skills)
user-invocable: false
```

| Frontmatter | User can `/invoke` | Claude auto-loads | Context loading |
|---|---|---|---|
| (default) | Yes | Yes | Description always; full body on invoke |
| `disable-model-invocation: true` | Yes | No | Description not in context |
| `user-invocable: false` | No | Yes | Description always; full body on invoke |

## Pre-approving tools

Avoid per-use approval prompts for skills with known tool needs:

```yaml
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
```

## Path-scoped skills

Automatically load a skill only when working with specific files:

```yaml
paths: "packages/frontend/**/*.tsx, packages/frontend/**/*.ts"
```

## Subagent isolation

Run a skill in its own forked context (no conversation history):

```yaml
context: fork
agent: Explore   # Built-in: Explore, Plan, general-purpose; or custom subagent name
```

## Argument substitution

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

# Or with indexed args:
Migrate the $0 component from $1 to $2.
```

## Dynamic context injection

The `` !`command` `` syntax executes shell commands *before* the skill content reaches Claude. The
output replaces the placeholder inline:

```yaml
---
name: pr-summary
description: Summarize a pull request with live diff data
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request: what changed, why, and any concerns.
```

For multi-line injection, use a fenced code block with `` ```! ``:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

This runs entirely as preprocessing — Claude only sees the final rendered result.
