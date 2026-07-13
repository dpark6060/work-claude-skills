---
name: project-init
description: Scaffolds a new local "cowork-style" project directory in the current
  working directory — sanctioned subdirectories (sources, notes, outputs, snippets,
  scratch), a boilerplate CLAUDE.md with filing rules, an INDEX.md knowledge map for
  lazy-loading sources and skills, and HANDOFF.md/WORKLOG.md for cross-session
  continuity. Use whenever the user wants to start, set up, or
  initialize a new project workspace for non-code work (research, docs, reports),
  even if they don't say "project-init". MANDATORY TRIGGERS: new project, init a
  project, set up a project, start a project, project directory, cowork project,
  workspace for.
---

# Project Init

You are scaffolding a standardized "cowork-style" project directory: a terminal
workspace for non-code work (source docs, summaries, snippets, reports) with a fixed
structure and cross-session continuity files. All file content comes from
`${CLAUDE_SKILL_DIR}/references/templates.md` — read it before writing anything.

## Non-Negotiables

- Create the project in the **current working directory** as `./<name>/`. Use another
  location only if the user explicitly names one.
- Never overwrite: if `./<name>/` already exists, stop and tell the user.
- Every scaffolded file is filled from the templates file. Don't improvise structure,
  add directories, or drop sections.
- No leftover `{{...}}` placeholders in any written file.
- Always ask about git init (Step 5). Never assume either way.

## Step 1 — Gather inputs

You need two things. Ask only for what the invocation didn't already provide:

1. **Project name** — normalize to kebab-case (`Gear Audit Q2` → `gear-audit-q2`).
2. **Purpose** — one line describing what the project is for. Goes into CLAUDE.md and
   the seed HANDOFF.md verbatim.

Optionally: if the user named source material, relevant personal skills, or external
references in the invocation, capture them — they become the first INDEX.md entries in
Step 4 instead of the `(none yet)` placeholders. Don't interrogate for them; only use
what was volunteered.

## Step 2 — Preflight

- Confirm `./<name>/` does not exist. If it does, stop.
- Warn (but proceed if the user confirms) when the cwd is inside an existing git repo
  or is itself a project-init project (has both `CLAUDE.md` and `HANDOFF.md`) —
  nesting projects is usually a mistake.

## Step 3 — Scaffold the tree

```
<name>/
├── CLAUDE.md
├── INDEX.md
├── HANDOFF.md
├── WORKLOG.md
├── .gitignore
├── sources/.gitkeep
├── notes/.gitkeep
├── outputs/.gitkeep
├── snippets/.gitkeep
└── scratch/.gitkeep
```

Create the five subdirectories, each with a `.gitkeep` so git tracks the empty
structure.

## Step 4 — Write the files

Read `${CLAUDE_SKILL_DIR}/references/templates.md` and write each template to the new
project, filling the placeholders:

| Placeholder | Value |
|---|---|
| `{{PROJECT_NAME}}` | kebab-case project name |
| `{{PURPOSE}}` | the one-line purpose |
| `{{DATE}}` | today, `YYYY-MM-DD` |

If Step 1 captured initial sources, skills, or external references, write them as
INDEX.md entries in the entry format the template defines, replacing the relevant
`(none yet)` placeholders.

## Step 5 — Git

Ask the user whether to `git init` the project. If yes:

```bash
git init && git add -A && git commit -m "Initialize <name> project scaffold"
```

Write `.gitignore` in Step 4 regardless of the answer — it costs nothing and is ready
if they init later.

## Step 6 — Report

Print the created tree and remind the user: start the next Claude session **inside**
the new directory so its CLAUDE.md loads and the session protocol (read INDEX.md and
HANDOFF.md, maintain WORKLOG.md) kicks in.
