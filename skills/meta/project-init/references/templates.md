---
type: Template Set
title: project-init scaffold templates
description: The file templates project-init writes into a new project — CLAUDE.md boilerplate, OKF index.md files, seed HANDOFF.md, seed log.md, and .gitignore.
tags: [scaffolding, templates, okf]
timestamp: 2026-07-15T00:00:00Z
---

# project-init Templates

Fill `{{PROJECT_NAME}}`, `{{PURPOSE}}`, and `{{DATE}}` (today, `YYYY-MM-DD`) before
writing. Each fenced block below is the complete content of one file. The scaffold is
an OKF knowledge bundle (spec: `~/.claude/skills/shared/okf-spec.md`) — index/log
structure and frontmatter rules come from that spec.

## CLAUDE.md

````markdown
---
type: Agent Instructions
title: {{PROJECT_NAME}} project instructions
description: Session protocol and filing rules for the {{PROJECT_NAME}} workspace.
---

# {{PROJECT_NAME}}

**Purpose:** {{PURPOSE}}

This is a cowork-style project workspace, not a code repo. Work products are files;
every file gets filed by the rules below. The directory is an **Open Knowledge Format
(OKF) bundle** (spec: `~/.claude/skills/shared/okf-spec.md`): markdown concept
documents with YAML frontmatter, navigated through per-directory `index.md` files.
The goal is that any agent launched here can read this file plus the root `index.md`
and be an expert on the project, loading documents lazily as questions demand.

## OKF rules (how every file is written)

The authoritative rules are the OKF spec: `~/.claude/skills/shared/okf-spec.md`. Read it
for anything beyond the basics below, and don't reproduce its rules elsewhere — it is the
single source of truth. The `okf-lint` skill enforces them; run it before wrapping up.

Day-to-day essentials (a convenience summary, not the authority):

- Every document you author is an OKF **concept**: YAML frontmatter with a required
  `type` (`Note`, `Analysis`, `Report`, `Snippet`, `Handoff`, …), plus `title` and a
  one-sentence `description` (copied verbatim into indexes — keep it tight).
- `index.md` and `log.md` are **reserved**: no frontmatter (root `index.md` carries only
  `okf_version`).
- Cross-link with relative markdown links; cite external sources under a `# Citations`
  heading. Links to not-yet-written documents are fine.

## Session startup protocol

1. This file loads automatically.
2. Read `index.md` (root) — the bundle's entry point: subdirectory indexes, project
   documents, skills, and external references. Do **not** read listed files up front;
   descend into a subdirectory's `index.md`, then into a document, only when a
   question or task matches its description / "Load when" trigger.
3. Read `HANDOFF.md` — the previous session's state dump and the source of truth for
   where things stand.
4. Read `log.md` **only** if HANDOFF.md points to it or you're missing context
   HANDOFF.md doesn't cover. Don't read it by default.

After steps 1–3 you are ready to answer questions about the project.

## Session end protocol

When wrapping up a work session (or whenever the user says to wrap up / hand off):

1. **Update the index files** — every directory you added or changed files in gets
   its `index.md` refreshed. Entry format (one per file, alphabetical):
   `* [Title](file.md) - one-sentence description. Load when: <trigger>.`
   The description comes from the file's frontmatter; the "Load when" trigger is
   this project's convention for lazy loading. An unindexed file is invisible to
   future sessions. New skills or external references go in the root `index.md`.
2. **Overwrite** `HANDOFF.md` with a fresh state dump (keep its frontmatter, bump its
   `timestamp`). It is written by LLM, for LLM — dense, telegraphic, no prose
   niceties. It must cover: current goal, state of the work, open threads, exact
   paths of files the next session should read, and next actions.
3. **Prepend** a dated entry to `log.md` — newest first, per OKF: a `## YYYY-MM-DD`
   heading (reuse today's if it exists) with `* **Update**: ...` /
   `* **Creation**: ...` bullets. Human readable, a few lines: what was done, what
   was decided.
4. **Verify OKF conformance** — run the `okf-lint` skill (or
   `python3 ~/.claude/skills/okf-lint/scripts/okf_lint.py .`) and clear any findings.
   It catches unindexed files, missing `type`, and malformed `index.md`/`log.md` before
   they become drift. `--fix` generates any missing indexes; the rest you fix by hand.

## Filing rules

| Directory | What goes there |
|---|---|
| `sources/` | Anything ingested from outside — PDFs, exports, transcripts, pasted docs. READ-ONLY: never edit these and never inject frontmatter into them — their `description` and load trigger live in `sources/index.md` instead. Every file added here gets a `sources/index.md` entry at the same time. Exception: a dataset, cloned repo, or other multi-file directory ingested whole gets **one** index entry for the directory, not per-file entries. Add large binary data to `.gitignore`. |
| `notes/` | Intermediate thinking — summaries, analyses, meeting notes. Editable, kept, written as OKF concepts. Index every file. Generated working artifacts (rendered previews, intermediate JSON) don't belong here — keep them in `scratch/` until they're part of a deliverable in `outputs/`. |
| `outputs/` | Finished work products only. If it isn't shareable as-is, it isn't done — it belongs in `notes/` or `scratch/`. Never save files directly at the top level of `outputs/`: every deliverable goes in a descriptively-named subdirectory (e.g. `outputs/2026-q2-gear-audit/report.md`). A subdirectory with more than one file gets its own `index.md`, listed under `# Subdirectories` in `outputs/index.md`. |
| `scripts/` | Runnable helper scripts and reusable fragments that outlive one task — build/deploy/scrape tools, code blocks, boilerplate text, queries. Non-markdown files never get frontmatter — their description and load trigger live in `scripts/index.md`, like sources. Index every file. |
| `scratch/` | Disposable workspace — temp files, experiments, half-baked drafts. May be wiped at any time; never reference scratch files from other documents. Never indexed, no frontmatter needed. |

## Conventions

- Dated filenames use ISO dates: `YYYY-MM-DD-<topic>.md`.
- Don't invent new top-level directories — everything files under the table above.
- `sources/` is read-only; `scratch/` is wipeable.
- No loose files at the top of `outputs/` — one descriptively-named subdirectory per
  deliverable.
- Index files are pointer lists, never content dumps — headings plus
  `* [Title](path) - description` bullets, nothing else.
````

## index.md (bundle root)

````markdown
---
okf_version: "0.1"
---

# Subdirectories

* [sources](sources/index.md) - Ingested external material — read-only evidence.
* [notes](notes/index.md) - Intermediate thinking: summaries, analyses, meeting notes.
* [outputs](outputs/index.md) - Finished deliverables, one subdirectory each.
* [scripts](scripts/index.md) - Runnable helper scripts and reusable fragments that outlive one task.

# Project Documents

* [HANDOFF](HANDOFF.md) - State dump from the most recent session — the source of truth for where the project stands.

# Skills

Personal Claude skills relevant to this project — invoke with the Skill tool.

* (none yet)

# External

URLs, dashboards, tickets, drives — things that live outside this directory.

* (none yet)
````

## sources/index.md

````markdown
# Sources

* (none yet)
````

## notes/index.md

````markdown
# Notes

* (none yet)
````

## outputs/index.md

````markdown
# Outputs

* (none yet)
````

## scripts/index.md

````markdown
# Scripts

* (none yet)
````

## HANDOFF.md (seed)

````markdown
---
type: Handoff
title: Session handoff
description: State dump from the most recent session — the source of truth for where the project stands.
timestamp: {{DATE}}T00:00:00Z
---

# HANDOFF

FRESH PROJECT — no prior sessions, nothing to hand off yet.

GOAL: {{PURPOSE}}
STATE: scaffold only; all directories empty; index files have no entries.
NEXT: begin work. Populate sources/ with input material, register each in
sources/index.md, then work per CLAUDE.md filing rules. Overwrite this file at
session end per the session end protocol.
````

## log.md (seed)

````markdown
# Project Update Log

## {{DATE}}

* **Initialization**: Project scaffolded by project-init.
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
