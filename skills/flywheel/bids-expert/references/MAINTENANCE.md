---
type: maintainer-notes
title: bids-expert — maintenance notes, design decisions, known gaps
tags: [maintenance, roadmap, internal]
---

# bids-expert — maintenance notes

Internal notes for whoever maintains this skill. Not part of the answer path — the skill
doesn't load this at runtime.

## v1 design decisions

- **Spec layer is generated, not hand-written.** `references/bids/` is a deterministic join off
  the vendored schema (`sources/bids-schema/`) via `bidsschematools`. Don't hand-edit those files —
  edit the generator and regenerate, or they drift from the schema and lose provenance.
- **Code depth is ground truth, no LLM distill.** `code-index/cards.jsonl` holds real source +
  real template rules (no paraphrase). Regenerated deterministically.
- **Flywheel overviews are hand-distilled** (`references/flywheel/*.md`). These are the one layer
  that can drift as the gears change — refresh them manually on gear updates.

## Known gaps / future work

- **Artifact generation is playbook-driven, not scripted.** The skill *describes how* to produce
  relabel CSVs and curation-template JSON (the model follows the reference formats); there is no
  `scripts/` helper that emits them. This is deliberate for v1 — templates and label mappings are
  judgment-heavy, not mechanical. If a deterministic helper becomes worth it (e.g. "dump a
  project's acquisition labels into the relabel CSV skeleton"), add it under `scripts/`. Note that
  such a helper needs **live SDK access**, which v1 deliberately keeps out of scope (the skill
  advises + generates artifacts; the user runs the gears/SDK). Wiring live ops in is a scope change,
  not just a script — gate every mutation behind confirmation and compose with `fw-client` /
  `flywheel-sdk` / `fw-instance-inspector`.

## Regenerating

- Spec pages (BIDS version bump):
  `uv run --with bidsschematools python3 ${CLAUDE_SKILL_DIR}/scripts/build_bids_reference.py`
- Code index (latest repo versions):
  `python3 ${CLAUDE_SKILL_DIR}/scripts/build_code_index.py --pull`

Provenance/versions: each spec page's frontmatter, `sources/bids-schema/VENDOR.md`, and
`code-index/code-manifest.md`.
