---
type: Template Set
title: project-init scaffold templates
description: The five file templates project-init writes into a new project — CLAUDE.md boilerplate, INDEX.md knowledge map, seed HANDOFF.md, seed WORKLOG.md, and .gitignore.
tags: [scaffolding, templates]
---

# project-init Templates

Fill `{{PROJECT_NAME}}`, `{{PURPOSE}}`, and `{{DATE}}` (today, `YYYY-MM-DD`) before
writing. Each fenced block below is the complete content of one file.

## CLAUDE.md

````markdown
# {{PROJECT_NAME}}

{{PURPOSE}}

This is a cowork-style project workspace, not a code repo. Work products are files;
every file gets filed by the rules below. The goal is that any agent launched here
can read this file plus `INDEX.md` and be an expert on the project, loading sources
lazily as questions demand.

## Session startup protocol

1. This file loads automatically.
2. Read `INDEX.md` — the project's knowledge map: every source, skill, and external
   reference, each with a "Load when" trigger. Do **not** read the listed files up
   front; load each one lazily when a question or task matches its trigger.
3. Read `HANDOFF.md` — the previous session's state dump and the source of truth for
   where things stand.
4. Read `WORKLOG.md` **only** if HANDOFF.md points to it or you're missing context
   HANDOFF.md doesn't cover. Don't read it by default.

After steps 1–3 you are ready to answer questions about the project.

## Session end protocol

When wrapping up a work session (or whenever the user says to wrap up / hand off):

1. **Update** `INDEX.md` — every source ingested, skill used, or external reference
   relied on this session must have an entry. An unindexed source is invisible to
   future sessions.
2. **Overwrite** `HANDOFF.md` with a fresh state dump. It is written by LLM, for LLM —
   dense, telegraphic, no prose niceties; human readability is irrelevant. It must
   cover: current goal, state of the work, open threads, exact paths of files the next
   session should read, and next actions.
3. **Append** a dated entry to `WORKLOG.md` — human readable, a few lines: what was
   done, what was decided.

## Filing rules

| Directory | What goes there |
|---|---|
| `sources/` | Anything ingested from outside — PDFs, exports, transcripts, pasted docs. READ-ONLY: never edit these, treat them as evidence. Every file added here gets an `INDEX.md` entry at the same time. |
| `notes/` | Intermediate thinking — summaries, analyses, meeting notes. Editable, kept. Index the load-bearing ones. |
| `outputs/` | Finished work products only. If it isn't shareable as-is, it isn't done — it belongs in `notes/` or `scratch/`. Never save files directly at the top level of `outputs/`: every deliverable goes in a descriptively-named subdirectory (e.g. `outputs/2026-q2-gear-audit/report.md`). |
| `snippets/` | Reusable fragments that outlive one task — code blocks, boilerplate text, queries. |
| `scratch/` | Disposable workspace — temp files, experiments, half-baked drafts. May be wiped at any time; never reference scratch files from other documents. Never indexed. |

## Conventions

- Dated filenames use ISO dates: `YYYY-MM-DD-<topic>.md`.
- Don't invent new top-level directories — everything files under the table above.
- `sources/` is read-only; `scratch/` is wipeable.
- No loose files at the top of `outputs/` — one descriptively-named subdirectory per
  deliverable.
- INDEX.md is the single knowledge map — keep entries in its defined format, and keep
  it a pointer list, never a content dump.
````

## INDEX.md

````markdown
---
type: Project Index
title: {{PROJECT_NAME}} knowledge map
description: Catalog of every source, skill, and external reference this project uses — what each is and when to load it.
tags: [index, knowledge-map]
timestamp: {{DATE}}T00:00:00Z
---

# INDEX — {{PROJECT_NAME}}

The project's knowledge map, read at every session start. Entries are pointers, not
content: never paste source material in here. Load a listed file only when a question
or task matches its "Load when" trigger.

**Entry format** — one bullet per item, exactly this shape:

`- \`path-or-name\` — what it is (one line). Load when: <trigger>. <access/size note if non-obvious>.`

Example:
`- \`sources/2026-03-fda-guidance.pdf\` — FDA guidance on SaMD submissions. Load when: regulatory or submission questions. 80pp — read the TOC pages first.`

## Sources

Files in `sources/`. Every file there must have an entry here.

- (none yet)

## Skills

Personal Claude skills relevant to this project — invoke with the Skill tool.

- (none yet)

## Key documents

Load-bearing docs in `notes/` and `outputs/` worth loading for context.

- (none yet)

## External

URLs, dashboards, tickets, drives — things that live outside this directory.

- (none yet)
````

## HANDOFF.md (seed)

````markdown
# HANDOFF

FRESH PROJECT — no prior sessions, nothing to hand off yet.

GOAL: {{PURPOSE}}
STATE: scaffold only; all directories empty; INDEX.md has no entries.
NEXT: begin work. Populate sources/ with input material, register each in INDEX.md,
then work per CLAUDE.md filing rules. Overwrite this file at session end per the
session end protocol.
````

## WORKLOG.md (seed)

````markdown
# WORKLOG — {{PROJECT_NAME}}

Append-only, newest entry last. A few human-readable lines per session: what was
done, what was decided.

## {{DATE}}

- Project scaffolded by project-init.
````

## .gitignore

````
# scratch/ is disposable — keep the dir, ignore its contents
scratch/*
!scratch/.gitkeep

.DS_Store
Thumbs.db
*.tmp
````
