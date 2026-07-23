# okf-lint — design & rationale

**Date:** 2026-07-21
**Status:** implemented
**Owner:** David Parker

Design record for the `okf-lint` skill, its enforcement hook, and how both relate to
the OKF spec and the project-init template. This is the *why* — the research and the
decisions. Operational how-to (running the linter, the rule-fix table, the spec-bump
sync procedure) lives in the skill itself at `skills/meta/okf-lint/SKILL.md`; this doc
does not repeat it.

## Problem

The config repo adopted OKF (Open Knowledge Format) for curated markdown — skill
`references/`, project-init workspaces, wikis. `project-init` reads the spec at scaffold
time, but nothing enforced conformance afterward. Adherence was 100% behavioral: it
relied on an agent following the session-end protocol every time. That has no closing
loop, and drift creeps in three ways:

1. **Instance drift** — a growing bundle accumulates violations (unindexed files,
   missing `type`, malformed `index.md`) because nothing checks §9 conformance. The spec
   *defines* a conformance contract; there was no checker for it.
2. **Paraphrase drift** — the rules were stated in two places that could diverge: the
   spec, and the project-init CLAUDE.md template's inline restatement.
3. **Version drift** — the spec is vendored and pinned to v0.1; if upstream bumps, the
   vendored copy, the enforcement, and the paraphrase all silently fall behind.

Notably, the `llm-wiki` plugin in this same config already ships a `wiki:lint`. OKF
bundles had the spec but no linter.

## Prior art surveyed

Before building, we checked whether an existing OKF linter was worth adopting or
vendoring. Four candidates:

| Tool | Lang / dist | Adopt? | Why |
|---|---|---|---|
| `GoogleCloudPlatform/knowledge-catalog` (`okf/`) | Python, Apache-2.0 | No | Ships **no** validator — only a bundle *generator* + Cytoscape visualizer. `SPEC.md` is the only normative artifact. |
| `serradura/okf-gem` | Ruby, Apache-2.0 | No | Richest rule taxonomy of the lot, but the linter (~450 lines) is tightly coupled to its own graph/frontmatter/link/report objects. "Pull out just the linter" means porting the graph builder too, in Ruby. It's a full harness (Rack server, renderer, registry). |
| `PoorvaJ-WW/okft` | Python, Apache-2.0 | No | Closest match and the only Python option, but drags in `pyyaml` and is a serve-oriented CLI package (MCP server). Installing a server package to run one lint command in a hook is backwards. |
| `thisismydesign/okf-lint` | TypeScript, MIT | No | Wrong language for a stdlib-Python git/session hook. |

### What we took (ideas, not code)

- **The error/warning split — the key takeaway.** All three real linters converge on it,
  straight from spec §9: the only *hard errors* are (a) unparseable frontmatter,
  (b) missing/empty `type`, (c) malformed reserved files (`index.md` / `log.md`).
  Everything else — **including broken links** — must be a warning, because §9 requires
  consumers to tolerate it. A session hook that errors on anything else is too noisy to
  live with. This directly shaped the hook's exit-code behavior.
- **okft's error/warning code taxonomy** as a checklist for which warnings are worth
  having (broken links, bad timestamps, malformed tags, orphans, missing root index).
- **serradura's six-category rule IDs** (reachability, backlog, completeness, freshness,
  provenance, hygiene) as a menu for future richer checks if we ever want them.

### What we rejected and why

- **Broken-link checking** — omitted deliberately. Spec §5.3/§9 say a link to a
  not-yet-written concept is legitimate, and consumers must tolerate broken links. Our
  OKF006 index-coverage check catches the practical "this file is invisible" case better.
- **Orphan/reachability detection** — redundant with OKF006 for our use case.
- **Project directory-structure checks** — the linter checks OKF only (frontmatter,
  reserved files, index coverage). project-init's `sources/`/`notes/`/`outputs/` layout
  is a project convention, not OKF, so it stays out of the linter. This keeps the linter
  reusable against any OKF bundle.

**Decision: build our own, ~400-line stdlib Python script.** No install step (matters for
a hook that fires constantly), no license/attribution obligation, and already ahead of all
four on one axis — none of them has an autofix, ours has a safe `--fix`.

## Components and how they relate

```
skills/shared/okf-spec.md ............. SINGLE SOURCE OF TRUTH for the rules
      │                                 (vendored from GCP, pinned via okf_version)
      │ referenced by
      ├── skills/meta/okf-lint/
      │     ├── scripts/okf_lint.py .... executable enforcement of the spec
      │     │                            (version-pinned; self-checks vs the spec)
      │     └── SKILL.md ............... /okf-lint; operational how-to + sync procedure
      │
      ├── hooks/okf-lint-hook.sh ....... Stop hook; runs the linter in OKF bundles only
      │     └── (registered in ~/.claude/settings.json, symlinked from repo)
      │
      └── skills/meta/project-init/references/templates.md
            └── generated CLAUDE.md ..... points to the spec; keeps only a short
                                          non-authoritative cheat-sheet + project rules
```

The single-source-of-truth structure is the point. Prose (spec), code (linter), and
embedded agent-instructions (template) can't be one file — three media, three consumers —
but only **one** of them *states* the rules. The template used to restate four spec
sections inline; it now defers to the spec and delegates enforcement to okf-lint.

## The linter

`skills/meta/okf-lint/scripts/okf_lint.py`. Stdlib-only; uses PyYAML for stricter parse
checks *if* it's importable, degrades gracefully to a minimal key parser otherwise (so it
runs in a bare hook environment). Walks a bundle root, dispatches each `.md` by filename
(index / log / concept), then runs directory-level coverage checks.

### Rules

| Code | Severity | Checks |
|---|---|---|
| OKF000 | warning | linter's `OKF_SPEC_VERSION` disagrees with the vendored spec's `okf_version` |
| OKF001 | error | concept file has no frontmatter block |
| OKF002 | error | frontmatter missing a non-empty `type` |
| OKF003 | error | reserved file frontmatter violation (`log.md` any; non-root `index.md` any; root `index.md` beyond `okf_version`) |
| OKF009 | error | frontmatter present but unparseable (PyYAML path only) |
| OKF004 | warning | `log.md` date heading not ISO `YYYY-MM-DD` |
| OKF005 | warning | `index.md` contains a code fence or table (content dump; indexes are pointer lists) |
| OKF006 | warning | concept file / indexed subdir not referenced by its directory's `index.md` |
| OKF007 | warning | directory lacks `index.md` but holds 4+ uncovered concept files (recursive rule) |
| OKF008 | warning | `timestamp` present but not ISO-8601 |
| OKF010 | warning | `tags` present but not a YAML list (PyYAML path only) |

Only OKF001/002/003/009 are hard errors (spec §9). Exit codes: 0 clean, 1 failures
present, 2 bad usage. `--strict` promotes warnings to failures; `--errors-only` is what
the hook uses.

### Exemptions

`SKILL.md`, `CLAUDE.md`, `README.md`, `AGENTS.md`, `GEMINI.md` are skipped entirely —
harness-owned files whose frontmatter the tooling owns, per the OKF scope note. This also
fixes a false positive: a fresh project-init bundle's root `CLAUDE.md` is intentionally
never indexed (it auto-loads), so without the exemption OKF006 would wrongly flag it.

`sources/` and `scratch/` subtrees (`SKIP_DIRS`) are excluded from every check. This came
out of linting a real project-init bundle: `sources/` is read-only ingested evidence that
the project's own filing rules forbid adding frontmatter to, so demanding it was a false
positive; `scratch/` is disposable and never indexed. Skipping by directory name is a
small concession of project-init knowledge into an otherwise project-agnostic linter,
justified because project-init bundles are a primary consumer.

### `--fix` scope (deliberately narrow)

`--fix` only *creates* a missing `index.md` (pulling title/description from concept
frontmatter). It never edits an existing index and never touches frontmatter. Judgment
calls — writing a `type`, a good description, an index entry's "Load when" trigger,
removing frontmatter from a reserved file — are left to the `/okf-lint` skill with the
agent in the loop. The script stays deterministic and safe; the skill does the thinking.

## Spec interaction & drift control

The version pin is the bridge between the two authorities (spec and linter). It looks like
duplication but isn't:

- `okf_version: "0.1"` in the spec means *"the spec IS 0.1."*
- `OKF_SPEC_VERSION = "0.1"` in the linter means *"my hand-written rules implement 0.1."*

These are different facts and can legitimately differ (spec updated, rules not yet). The
linter compares them every run and emits **OKF000** on divergence. It deliberately does
**not** read the version from the spec — if it did, the two would be tautologically equal
and drift would never surface. The sync procedure for a spec bump is in SKILL.md's
"Keeping current" section (not repeated here, by the same SoT principle this whole design
serves).

Upstream drift (GCP revising the spec) is not auto-detected — nothing polls the URL. It's
a manual WebFetch-and-diff against the `resource:` URL when touching the skill.

## The hook

`hooks/okf-lint-hook.sh`, a `Stop` hook (fires when a turn ends), symlinked into
`~/.claude/hooks/` so `git pull` keeps it current. Behavior:

- **Bundle gate:** exits 0 silently unless `cwd/index.md` declares `okf_version`. That
  signal marks a real OKF bundle, so the hook never fires in code repos or this config
  repo — only where OKF applies.
- **Errors-only by default:** runs the linter `--errors-only` and blocks the stop (exit 2,
  findings on stderr fed back to the agent) only on hard errors. Warnings never block —
  per the §9 tolerance rule, and because blocking on every unindexed file mid-work would
  be unlivable. `OKF_LINT_LEVEL=strict` at the top of the hook flips it to block on
  warnings too.
- **Loop guard:** honors `stop_hook_active` so a blocked stop can't recurse.

## Non-goals

- Not a general markdown linter — OKF structure only.
- Not a project-layout checker — `sources/`/`notes/`/`outputs/` are project-init's, not
  OKF's.
- No broken-link or orphan checking (see rejections above).
- No upstream spec polling.
