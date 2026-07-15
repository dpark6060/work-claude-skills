---
name: fw-import-rules
description: Authors Flywheel data-import rule YAML files (rule sets) — takes a data directory plus a description of how folders/files map to subjects, sessions, acquisitions, and attachments, and produces a correct, fully commented rules file for `flyw import run`. Also debugs rule behavior down to the fw-meta/xfer/connector source. Use for any bulk import / ingest rule work even if the user just says "import this folder into Flywheel". MANDATORY TRIGGERS: import rules, rule set, rule-set, rules file, rules.yaml, --rules-file, --rule-set, bulk import, data ingest, ingest rules, xfer import, flyw import, map folders to subjects, "these folders are the subjects", import this directory, file didn't import, import skipped files, wrong subject label on import.
---

You are authoring (or debugging) a Flywheel **import rules file**: the YAML consumed by
`flyw import run --rule-set <file-or-id>` that tells the import engine which files to
import, where they land in the project hierarchy (project / subject / session /
acquisition), and what metadata to extract. Your deliverable is a correct, exhaustively
commented rules YAML plus a coverage summary the user can trust.

## Reference index

| File | Load when |
|---|---|
| `references/rule-schema.md` | Always, before drafting — document shapes, every rule field, filter semantics, destination field catalog, DICOM behavior |
| `references/template-pattern-syntax.md` | Always, before drafting — mapping syntax, the metadata cascade, pattern gotchas |
| `references/examples.md` | Drafting — worked tree→YAML examples to pattern-match against |
| `references/source-map.md` | Verifying or debugging — local simulation harness, repo/entrypoint map, per-symptom recipes |

## Mindset

- **Unmatched files are skipped silently.** No error, no report line (and on local
  imports, not even a report entry). Every file in the source tree must be accounted
  for: matched by the intended rule, or listed as intentionally skipped in your summary.
- **The source is the spec.** The published docs are wrong in places (they use an
  `ext` filter field the server rejects, and a `job:` wrapper that doesn't exist).
  The references here are source-verified; when something is still ambiguous, test it
  empirically against fw-meta rather than trusting any doc — including this skill's.
- **Comments are the deliverable.** The YAML will be read by people who don't know the
  rule engine. Every rule gets a comment block: what it matches, where files land, why
  it's ordered where it is, and what falls through.
- **Verify before you hand over.** A rules file you haven't simulated against the real
  tree is a draft, not a deliverable.

## Step 1 — Profile the data directory

Before reading any mapping description, learn what's actually there:

```bash
# shape: depth histogram and per-depth file counts
find <root> -type f | awk -F/ '{print NF}' | sort | uniq -c
# extensions by count
find <root> -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
# sample paths at each depth; eyeball naming conventions
find <root> -type f | awk -F/ 'NF==4' | head -5
# junk that will need excluding
find <root> -name '.DS_Store' -o -name 'Thumbs.db' -o -name '*.tmp' | head
```

Record: total file count, depths present, extensions per depth, naming patterns
(delimiters, prefixes, dates), junk files, empty dirs, zip archives, and anything that
doesn't fit the described convention (those become questions or explicit skips).

## Step 2 — Turn the description into a mapping table

Translate the user's verbal description ("top folders are subjects, ...") into an
explicit table before writing YAML:

| Source (path shape / filename) | Level | Label source | Notes |
|---|---|---|---|
| `<subj>/<sess>/<acq>/*.dcm` (depth 4) | acquisition | folders (or DICOM headers?) | type: dicom |
| `<subj>/report.csv` (depth 2) | subject | folder name | attachment |
| `*.pdf`, `README*` (depth 1) | project | — | attachment |
| `scratch/**`, `.DS_Store` | — | — | intentionally skipped |

Ambiguities to resolve — ask the user only when the answer changes the YAML and can't
be inferred from the data; otherwise pick the sensible default and flag it in the
summary:

- DICOM labels from **folder names or headers**? (Header defaults are richer; folder
  names are what the user literally described. Default: headers for acquisition
  label, folders for subject/session if the folders look curated.)
- Files that match no described category — skip or catch-all? (Default: skip, listed.)
- Delimiters that could be ambiguous (`S_001_baseline` — where does the subject end?)
- Should junk exclusions be global (every rule) or is a no-catch-all enough?

## Step 3 — Draft the rules file

Read `references/rule-schema.md` and `references/template-pattern-syntax.md` first;
crib structure from `references/examples.md`. Rules that always apply:

- **Order rules specific → general** (first match wins). Attachments and special files
  first, bulk data rules after, no accidental catch-all.
- **Pin each rule to its territory** with includes (`depth=`, `path=~prefix/**`,
  `name=~*.dcm`) so rule order is belt-and-suspenders, not load-bearing.
- Use `name=~*.dcm` style filters — **never `ext=`** (docs show it; server rejects it).
- Map every hierarchy label explicitly OR document which cascade fallback (DICOM
  header / path default / `defaults:`) is intentionally providing it. Watch the
  path-default trap: an unmapped label silently takes a parent directory name —
  which is wrong whenever the tree is missing that level.
- Prefer boring, readable patterns over clever ones. Constrain captures
  (`{subject.label:[^_]+}`) when delimiters could be ambiguous.
- Comment every rule: what it matches, where files land, why this position in the
  file. Top of file: source tree shape, target project, date, and a pointer to what
  is intentionally skipped.

## Step 4 — Verify against the real tree

1. **Simulate locally** with the fw-meta harness in `references/source-map.md`
   (`uv run --with fw-meta==4.13.0 ...`): every file → which rule matched → extracted
   metadata, or SKIPPED. This is the same match/extract code the server runs.
2. Build the **coverage table**: per rule, file count matched; plus the full skipped
   list. Confirm skips are exactly the intended ones and extracted labels spot-check
   correctly (weird subjects, deepest paths, edge-case filenames).
3. For DICOM header mappings the harness can't simulate, run
   `flyw import test <file> --rule-set rules.yaml` on 1-2 real files (reads actual
   headers, client-side).
4. Offer the real dry run: `flyw import run -p <proj> -s <storage> --rule-set
   rules.yaml --dry-run` (previews a SUBSET only — the local simulation is the
   exhaustive check; the dry run validates server acceptance). Use the `flyw-cli`
   skill for CLI invocation details.

## Step 5 — Deliver

Hand over: the commented `rules.yaml`, the coverage summary (rule → count → example
paths, skipped files list), assumptions/defaults you chose, and the exact commands to
test and run the import. If the file will be stored as a managed rule set, note the
8192-char YAML limit (comments count).

## Debugging rule problems

For "file didn't import", "wrong label", "DICOM grouped wrong", "import stuck", or a
suspected genuine bug: load `references/source-map.md` — it maps every symptom to the
owning repo/file (fw-meta and fw-utils for rule semantics, cli for `import test` and
local uploads, xfer for validation/conflicts/reports, connector for server-side
execution), includes clone commands (xfer and connector are private — SSH), and the
local reproduction harness. Reproduce with the harness or `flyw import test` before
reading service code; most "bugs" are the metadata cascade or silent-skip semantics
behaving as designed.
