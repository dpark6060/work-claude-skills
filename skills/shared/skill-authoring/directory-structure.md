---
type: Convention Reference
title: Skill Directory Structure
description: This repo's sanctioned skill directory layout — the seven subdirectories, what belongs in each, and the OKF rules that govern references/.
tags: [skills, structure, okf, conventions]
timestamp: 2026-07-31T00:00:00Z
---

# Skill Directory Structure

> **Load when:** scaffolding a new skill, deciding where a file belongs, or reviewing whether an
> existing skill's layout is correct. Companion to
> [claude-skills-best-practices.md](../claude-skills-best-practices.md) (the core rulebook).

> This is **this repo's** convention layered on top of the official loading model in the core
> rulebook §3 — not Anthropic guidance. It exists so every skill has the same shape and tooling
> (`skill-maker`, `skill-audit`) can assume it.

**The base directory holds only `SKILL.md`.** Everything else goes in one of seven sanctioned
subdirectories. All are optional — add one only when the skill needs it. Don't invent siblings;
`server/` was added precisely so MCP servers stopped being a one-off.

| Subdir | Holds | Loading | Index? |
|---|---|---|---|
| `references/` | Detailed agent-ready markdown, split by topic/domain | Lazy — zero tokens until read | OKF `index.md` at 4+ uncovered files |
| `assets/` | Files that go **into the output** — output templates, boilerplate docs, images, fonts, CSS | Copied/filled, often never read into context | **Never** — describe at call site |
| `sources/` | Raw data (API dumps, large JSON/CSV) too costly to load casually | Lazy — high token cost, dig in only when needed | OKF `index.md` at 4+ uncovered files |
| `scripts/` | Executable code Claude **runs**, not reads | Token-free — executed, never loaded | **Never** — describe at call site |
| `server/` | Long-running / hosted processes (e.g. MCP servers) | Started, not loaded | **Never** — describe at call site |
| `cache/` | Runtime/generated state a script writes and later reads | Not loaded — runtime only | n/a — gitignored, never committed |
| `.learnings/` | Accumulated gotchas (`LEARNINGS.md`, `ERRORS.md`) | Read + summarized at task start | n/a — execution skills only |

**`references/` vs `assets/` — ask who consumes the file.** `references/` is consumed by the
*agent*, to change how it works; it lands in context and costs tokens. `assets/` is consumed by the
*deliverable* — copied, filled in, or embedded into what the skill produces. A schema guide the
agent reads to write a query is a reference. The report skeleton it fills in and hands back is an
asset. The `.pptx` boilerplate a script writes into is an asset that never enters context at all.

The practical tell: **`references/` files must carry OKF frontmatter, and an output template
can't.** If the agent copies the file into the artifact, `type:`/`title:` leaks into the
deliverable. So anything the agent reproduces rather than reads belongs in `assets/`, which is
exempt from OKF and never indexed.

```
skills/<category>/<skill-name>/
├── SKILL.md            # the only file in the base dir
├── references/         # OKF concept docs, lazy-loaded; index.md at 4+ uncovered files
│   └── <topic>.md
├── assets/             # goes into the output: templates, images, fonts; no OKF, never indexed
├── sources/            # raw data; high token cost; index.md at 4+ uncovered files
├── scripts/            # run via ${CLAUDE_SKILL_DIR}/scripts/...; never indexed
├── server/             # long-running processes (MCP servers); never indexed
├── cache/              # runtime state a script generates; gitignored, never committed
└── .learnings/         # execution skills only
    ├── LEARNINGS.md
    └── ERRORS.md
```

**This is an organization standard, not a token optimization.** Flat vs nested doesn't change
what loads — per the core rulebook §3, only the SKILL.md body loads on trigger, references/sources
cost nothing until read, and scripts/server never load. The subdirs buy authoring consistency, not
fewer tokens. The one real token lever is `index.md`, and it cuts both ways (below).

**Reference files follow OKF (Open Knowledge Format).** A skill's `references/` directory is an
OKF knowledge bundle. Full spec is vendored at `~/.claude/skills/shared/okf-spec.md`; the rules
that matter here:

- Every reference file starts with YAML frontmatter: `type` (required, e.g. `Config Reference`,
  `API Endpoint Schema`), plus `title` and a **one-sentence** `description` — the description is
  copied verbatim into `index.md`, so keep it tight. Optional: `tags`, `timestamp`, `resource`.
  This applies *only* under `references/` — `SKILL.md` and agent frontmatter keep the harness
  fields (`name`, `description`, control flags) exactly as
  [frontmatter-reference.md](frontmatter-reference.md) defines.
- A directory needs an `index.md` once it holds **4+ uncovered concept files** — its own files
  plus, recursively, those of any subdirectory *without* its own `index.md` (an indexed
  subdirectory covers its subtree and contributes zero; an unindexed one passes its files up to
  the parent's count). So four 2-file subdirs don't each need an index, but their parent sees 8
  uncovered files and does — listing the nested files directly by relative path. Below the
  threshold, SKILL.md routing suffices; an index is still legal anywhere. Index format: **no
  frontmatter**, body is nothing but headings with `* [Title](relative-path) - description`
  bullets, alphabetical. Concepts group under a heading naming the group; indexed subdirectories
  go under `# Subdirectories`, each linking to the subdirectory's own `index.md`.
- Optional `log.md` per directory for change history: `## YYYY-MM-DD` headings, newest first.
- Cross-link related reference files with file-relative markdown links; conventional section
  headings are `# Schema`, `# Examples`, `# Citations` (numbered `[1] [text](url)`, at the end).

**`index.md` is an enumeration layer, not a routing layer.** SKILL.md still owns routing: it
says *when* to load which reference ("writing a new gear? load gear-basics.md") and can point
at `references/index.md` instead of enumerating a large folder inline. Keep every index a pure
pointer list — an index that holds content Claude actually needs creates the
`SKILL.md → index.md → file` two-hop that the core rulebook's progressive-disclosure and
anti-patterns sections warn against.

**`scripts/` and `server/` are described at their call site, never indexed.** The caller doesn't
browse to pick a script — it needs the invocation contract (args in, what it writes/returns, exit
codes) inline next to the `${CLAUDE_SKILL_DIR}/scripts/foo.py` call. Always use
`${CLAUDE_SKILL_DIR}` for paths so they survive being symlinked into `~/.claude` and cloned
elsewhere.

**`.learnings/` is for execution skills only.** A pure reference/lookup skill has no "runs" to
learn from. It's writable and append-only, so periodically promote hot learnings into the SKILL.md
body and prune — otherwise it drifts from reality.

**`cache/` is where runtime state goes — never the base dir.** If a skill's script needs to write
generated state (a workspace dump, a resolved-ID lookup, anything fetched-then-reused), it writes
to `cache/` under the skill root, e.g. `${CLAUDE_SKILL_DIR}/cache/`. It's gitignored repo-wide by
`skills/*/*/cache/`, so it's never committed and doesn't count as authored skill content — a
script can rebuild it from scratch. Don't scatter runtime files at the skill root or invent
per-skill names for them.

**Data policy for `sources/` and `scripts/` fixtures.** Raw data and fixtures bloat a repo that's
cloned and symlinked into `~/.claude`. Commit small representative samples; fetch large dumps via
a script or keep them out of the repo.
