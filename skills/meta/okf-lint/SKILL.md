---
name: okf-lint
description: Checks and repairs Open Knowledge Format (OKF) conformance in a directory of
  markdown-plus-frontmatter knowledge docs — skill references/, project-init workspaces,
  wikis, any OKF bundle. Runs a deterministic linter (scripts/okf_lint.py) for the
  structural checks, then handles judgment-call fixes (writing a `type`, good
  descriptions, index entries with Load-when triggers) with agent review. Use for a spot
  check, to enforce the spec, or to bring a drifted directory back to spec. MANDATORY
  TRIGGERS — "okf", "OKF", "okf-lint", "lint the wiki", "check OKF", "is this OKF valid", "bring this
  directory to spec", "OKF conformance", "check frontmatter", "audit this knowledge base",
  "why isn't this file showing up in the index".
---

# OKF Lint

Enforces the Open Knowledge Format spec (`~/.claude/skills/shared/okf-spec.md`) against a
directory tree. Scope is **OKF structure only** — frontmatter, the reserved `index.md` /
`log.md` files, and index coverage. It does **not** check project-specific directory
layouts (project-init's `sources/`, `notes/`, `outputs/`, …) — that is a project
convention, not OKF.

`sources/` and `scratch/` subtrees are skipped entirely: `sources/` holds read-only
ingested evidence that project-init says must never get frontmatter, and `scratch/` is
disposable and never indexed. Neither is authored OKF content, so linting them is wrong.

Two halves: a deterministic Python linter does the detecting and the trivially-safe
fixes; you (the agent) do the fixes that need judgment.

## Step 1 — Run the linter

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/okf_lint.py <path>
```

- `<path>` defaults to the current directory. Point it at the bundle root.
- `--json` — machine-readable findings (rule, severity, path, message).
- `--strict` — treat warnings as failures (exit 1). Default: only errors fail.
- `--errors-only` — show/count hard errors only (what the Stop hook uses).
- `--fix` — apply **safe** fixes only: create the `index.md` files the house rule (OKF007)
  requires — only in directories at or over the uncovered-file threshold, deepest-first so
  an indexed subdir covers its subtree before the parent is counted, filling
  titles/descriptions from frontmatter and listing uncovered nested files by relative
  path. It never creates an index below the threshold, never edits an existing
  `index.md`, and never touches frontmatter.
- Exit codes: `0` clean, `1` failures present, `2` bad usage.

Stdlib-only; uses PyYAML for stricter parse checks if it happens to be installed.

## Step 2 — Fix what the script won't

The script reports these but leaves them to you, because they need judgment. Fix them by
editing the files, then re-run to confirm zero findings:

| Rule | Finding | Your fix |
|---|---|---|
| OKF001 | concept file has no frontmatter | add a frontmatter block; pick a `type`, write a one-sentence `description` |
| OKF002 | frontmatter missing `type` | add a descriptive `type` (`Note`, `Reference`, `Analysis`, …) |
| OKF009 | frontmatter won't parse | fix the YAML (usually an unquoted value or bad indent) |
| OKF003 | `index.md` / `log.md` carries frontmatter | remove it (root `index.md` may keep **only** `okf_version`) |
| OKF006 | concept/subdir not in its dir's `index.md` | add a bullet: `* [Title](file.md) - <description>. Load when: <trigger>.` — description from the file's frontmatter |
| OKF004 | `log.md` date heading not ISO | rewrite the heading as `## YYYY-MM-DD` |
| OKF005 | `index.md` has a code fence / table | move that content into a concept doc; the index is a pointer list |
| OKF008 | `timestamp` not ISO-8601 | rewrite as `YYYY-MM-DDThh:mm:ssZ` |
| OKF010 | `tags` not a list | rewrite as `tags: [a, b]` |

For "bring this directory to spec": run `--fix` first to generate any missing indexes,
then walk the remaining findings and fix them by hand. Use `--fix` output plus a re-run to
confirm you reached zero.

## House rule: when an index.md is required (OKF007)

The spec (§6) only says an index MAY appear. This repo tightens that: an `index.md` is
**required** once a directory holds **4+ uncovered concept files** — its own files plus,
recursively, those of any subdirectory *without* its own `index.md` (an indexed
subdirectory covers its subtree and contributes zero; an unindexed one passes its files up
to the parent's count). Four 2-file subdirs don't each need an index, but their parent
sees 8 uncovered files and does — it lists the nested files directly by relative path.
Below the threshold an index is still legal anywhere.

The linter flags this as OKF007 (warning), and `--fix` repairs it by creating the missing
index. The threshold is `INDEX_THRESHOLD` in `scripts/okf_lint.py`. Other skills
(skill-maker, project-init) should not restate this rule — they point here and run the
linter.

## What counts as an error vs a warning

Only three things are hard **errors** (spec §9): unparseable frontmatter, missing/empty
`type`, and malformed reserved files. Everything else — including index coverage and
broken links — is a **warning**, because the spec requires consumers to tolerate it. The
Stop hook blocks a session only on errors; use `--strict` when you want coverage enforced
too.

## Keeping current with the OKF spec

`skills/shared/okf-spec.md` is the single source of truth for the OKF rules. Everything
else refers to it rather than restating it: the project-init CLAUDE.md template points to
it, and this linter is its executable enforcement. Prose and code can't be the same file,
so there are exactly two authorities — the spec and the linter — and one mechanism to keep
them aligned.

That mechanism is the version pin. `OKF_SPEC_VERSION` in `scripts/okf_lint.py` asserts
"my rules implement version X"; the spec's `okf_version` frontmatter asserts "the spec IS
version Y." These are **not** the same fact stored twice — the linter's rules are
hand-written and can legitimately lag the spec, so the two can differ. The linter compares
them on every run and emits **OKF000** when they diverge. (This is why the linter hardcodes
the version instead of reading it from the spec: if it read it, the two would be
tautologically equal and drift would never be detected.)

When OKF000 fires (or you deliberately update the spec):

1. `skills/shared/okf-spec.md` — refresh from upstream (`resource:` URL in its frontmatter
   — `WebFetch` and diff), update its `okf_version`. This is the only place the rules
   themselves live.
2. `scripts/okf_lint.py` — reconcile each rule against the new spec, then bump
   `OKF_SPEC_VERSION` to match. Do this last; bumping the constant is what clears OKF000,
   so only do it once the rules actually match.

The project-init template holds a short *convenience* cheat-sheet (not authoritative) that
points here — re-check it only if the day-to-day essentials changed, which is rare across
minor versions.

Upstream drift (GCP revising the spec) is not auto-detected — nothing polls the URL. Check
it manually when you touch this skill, or when OKF releases a new version.

---

Design rationale, prior-art survey, and the reasoning behind the rules/hook live in
`docs/okf-lint/2026-07-21-okf-lint-design.md` (repo-only, not loaded — read it only if
you're reworking this skill).
