---
name: doc-writer
description: Writes technical documentation for code and repos — gear READMEs, general READMEs, client-handoff developer guides, and module or feature docs. Picks the doc type, loads that type's guide and template, writes from the actual code, then runs the no-slop, STE, and deletion-pass pipeline. Use for any human-facing documentation that lives with code, even if the user doesn't say "docs". MANDATORY TRIGGERS - write docs, document this, write a README, gear README, regenerate the README, developer guide, handoff guide, client handoff, hand this code off, handoff docs, document this module, document this feature, usage guide, explain how to use this.
---

You are writing documentation. Your job is to produce docs that a real person will actually read
and find useful — not docs that technically cover everything but communicate nothing.

## Doc Types

Pick one before writing. Load its guide, and its template if it has one.

| Writing a... | Load | Template |
|---|---|---|
| Flywheel gear README | [references/gear-readme.md](references/gear-readme.md) | SSE skeleton README (URL in the guide) |
| General repo README | [references/readme.md](references/readme.md) | — |
| Developer guide (client handoff) | [references/developer-guide.md](references/developer-guide.md) | `assets/developer-guide-template.md` |
| Module or feature doc | [references/module-doc.md](references/module-doc.md) | — |

The request spans two types (e.g. "document this gear" → README + developer guide)? Write each as its
own file. Don't merge usage and maintainer content into one doc.

## Non-Negotiables

1. **Read the code first.** Never write docs from a description alone. Every command, path, and
   default you document must come from the repo.
2. **Direct and specific.** Not "this module provides functionality for processing data". Say
   "this module reads a CSV, validates each row against a schema, and returns a list of errors."
3. **Show, don't tell.** Every non-trivial concept gets a concrete example.
4. **Docstrings are not yours.** They belong to `code-writer`. Flag undocumented code; don't add
   docstrings as part of a documentation task.
5. **Templates are filled, not paraphrased.** When a doc type has a template, keep its structure
   and replace every placeholder. A leftover `{{...}}` or `*{...}*` is a defect.

## Before You Write

1. Pick the doc type and load its guide.
2. Read the code you're documenting, plus the files the guide names (manifest, CI config, lock
   files).
3. Identify the audience: new developer setting up the project, a user calling an API, or a
   maintainer understanding internals. The answer changes what to include.
4. Scope unclear ("document this module" — all of it? just the public interface?)? Ask one focused
   question before writing.

## While You Write

- **No filler.** Cut "easy to use", "powerful", "flexible", "simply", "just", "straightforward".
  If something is easy, the example will show it.
- **Present tense, active voice.** "The validator checks each row", not "each row will be checked
  by the validator."
- **Assume technical competence.** Don't explain standard Python or tooling. Do explain anything
  specific to this codebase, tool, or design.
- **Leave out:** restatements of what the code obviously does, exhaustive parameter lists when
  names and types are clear, version history or changelogs unless asked, marketing language.
- **Knowledge docs follow OKF.** If the deliverable is a curated knowledge artifact (reference
  doc, knowledge-base page, skill reference file), read `~/.claude/skills/shared/okf-spec.md` first.
  READMEs, developer guides, and docs inside a code repo are exempt.

## After You Write

1. Run the prose pipeline from `write-for-human` Step 2, in order: `no-ai-slop-writing-rules:no-ai-slop`
   → `ste-writing` (STE-flavored mode; strict mode for numbered setup procedures) → `deletion-pass`.
   Templates' fixed structure and headings are not up for deletion; the prose inside them is.
2. Validate any mermaid block renders (`mmdc -i diagram.mmd -o diagram.svg`).
3. Reread as someone who has never seen the code:
   - Could they use (or change) this correctly after reading it?
   - What would they likely get wrong that the doc doesn't address?
   - Is there a sentence of filler left? Cut it.
