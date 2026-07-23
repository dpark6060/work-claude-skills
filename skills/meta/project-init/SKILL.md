---
name: project-init
description: Scaffolds a new local "cowork-style" project directory in the current
  working directory, structured as an Open Knowledge Format (OKF) bundle — sanctioned
  subdirectories (sources, notes, outputs, scripts, scratch) each with an index.md
  for progressive disclosure, a boilerplate CLAUDE.md with OKF filing rules, a root
  index.md knowledge map, and HANDOFF.md/log.md for cross-session continuity. Use
  whenever the user wants to start, set up, or initialize a new project workspace for
  non-code work (research, docs, reports), even if they don't say "project-init".
  MANDATORY TRIGGERS: new project, init a project, set up a project, start a project,
  project directory, cowork project, workspace for.
---

# Project Init

You are scaffolding a standardized "cowork-style" project directory: a terminal
workspace for non-code work (source docs, summaries, scripts, reports) with a fixed
structure and cross-session continuity files. The directory is an **OKF knowledge
bundle** (spec: `~/.claude/skills/shared/okf-spec.md`): authored markdown files are
concept documents with YAML frontmatter, every directory carries an `index.md`, and
`log.md` records history. All file content comes from
`${CLAUDE_SKILL_DIR}/references/templates.md` — read it before writing anything.

## Non-Negotiables

- Create the project in the **current working directory** as `./<name>/`. Use another
  location only if the user explicitly names one.
- Never overwrite: if `./<name>/` already exists, stop and tell the user.
- Every scaffolded file is filled from the templates file. Don't improvise structure,
  add directories, or drop sections.
- OKF reserved filenames are exact: `index.md` and `log.md`, lowercase. Index files
  carry no frontmatter (the root `index.md` carries only `okf_version`).
- No leftover `{{...}}` placeholders in any written file.
- The Step 1 purpose must be specific and must land as the labeled first line of
  CLAUDE.md under the title (per the template). A vague one-line label is a failure —
  see Step 1.
- Always ask about git init (Step 5). Never assume either way.

## Step 1 — Gather inputs

You need two things. Ask only for what the invocation didn't already provide:

1. **Project name** — normalize to kebab-case (`Gear Audit Q2` → `gear-audit-q2`).
2. **Purpose** — one line stating *specifically* what the project is for. It goes
   verbatim into the first line of CLAUDE.md (under the title) and the seed
   HANDOFF.md `GOAL:`, so it must stand alone as *the* description of the project.
   **Reject vague labels.** If the purpose wouldn't distinguish this project from a
   differently-scoped project that happens to share a name, push back and get a real
   one before scaffolding.
   - Bad: `Cloud art reference project` — a category label, not a purpose. A later
     session read it as an *edible*-clouds project because nothing in CLAUDE.md,
     HANDOFF, or the log said otherwise.
   - Good: `Recreate the visual look of billowing cumulus clouds inside a jar via a
     polymer cloud-point effect — an art project, not edible.`
   This is the cowork-project form of the `write-claudemd` skill's "first-line rule"
   (primary purpose stated specifically in the first line of CLAUDE.md); read that
   rule if you need the rationale.

Optionally: if the user named source material, relevant personal skills, or external
references in the invocation, capture them — they become the first index entries in
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
├── CLAUDE.md            # agent instructions (OKF concept, type: Agent Instructions)
├── index.md             # bundle root index — the knowledge map
├── HANDOFF.md           # OKF concept, type: Handoff
├── log.md               # OKF update log, newest first
├── .gitignore
├── sources/index.md
├── notes/index.md
├── outputs/index.md
├── scripts/index.md
└── scratch/.gitkeep     # scratch is never indexed
```

Each content subdirectory gets its own `index.md` (which also keeps the empty
directory tracked by git). Only `scratch/` uses a `.gitkeep` — it is disposable and
never indexed.

## Step 4 — Write the files

Read `${CLAUDE_SKILL_DIR}/references/templates.md` and write each template to the new
project, filling the placeholders:

| Placeholder | Value |
|---|---|
| `{{PROJECT_NAME}}` | kebab-case project name |
| `{{PURPOSE}}` | the one-line purpose |
| `{{DATE}}` | today, `YYYY-MM-DD` |

If Step 1 captured initial sources, skills, or external references, write them as
index entries in the OKF entry format the templates define
(`* [Title](path) - description. Load when: <trigger>.`), replacing the relevant
`(none yet)` placeholders — sources into `sources/index.md`, skills and external
references into the root `index.md`.

## Step 5 — Git

Ask the user whether to `git init` the project. If yes:

```bash
git init && git add -A && git commit -m "Initialize <name> project scaffold"
```

Write `.gitignore` in Step 4 regardless of the answer — it costs nothing and is ready
if they init later.

## Step 6 — Report

Print the created tree and remind the user: start the next Claude session **inside**
the new directory so its CLAUDE.md loads and the session protocol (read index.md and
HANDOFF.md, maintain the indexes and log.md) kicks in.
