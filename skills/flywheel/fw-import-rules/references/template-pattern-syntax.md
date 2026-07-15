---
type: Syntax Reference
title: Import Mapping Template & Pattern Syntax
description: Complete syntax for the template and pattern halves of an import rule mapping, from the fw-utils/fw-meta source.
tags: [flywheel, import, mappings, templates, patterns]
timestamp: 2026-07-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/lib/fw-utils/-/blob/main/fw_utils/parsers.py
---

# Import Mapping Template & Pattern Syntax

Verified against source: `fw_utils/parsers.py` (`Pattern`), `fw_utils/formatters.py`
(`Template`), `fw_meta/imports.py` (`MetaExtractor`, `ImportTemplate`, `ImportPattern`).

## Contents

- How a mapping works (template → string → pattern)
- Template syntax (the left side)
- Pattern syntax (the right side)
- Temp variables and metadata references
- Multiple mappings: fallback semantics
- The full metadata cascade (mappings → type defaults → path defaults → defaults → overrides)
- Gotchas

## How a mapping works

A mapping is `"<template>=<pattern>"`:

```
{path}={subject.label}/{session.label}/{acquisition.label}/{file.name}
```

1. The **template** (left of `=`) joins one or more *source* fields into a single string.
   For plain files the source fields are the file-stat fields: `path`, `name`, `dir`,
   `depth`, `size`, `ctime`, `mtime`. For `type: dicom` rules, any DICOM keyword
   (`PatientID`, `SeriesDescription`, ...) is also a valid source field.
2. The **pattern** (right of `=`) parses that string and captures parts of it into
   *destination* Flywheel metadata fields (`subject.label`, `session.info.foo`, ...).

The parser tries left-to-right first, then **reversed** (`validate_metadata_mapping`),
which enables the two idiomatic forms seen throughout the docs:

- **Extraction form** (source on the left): `'path={sub}/{ses}/{acq}/*'`
- **Assignment form** (destination on the left): `'subject.label={PatientID}'` —
  parsed reversed into template `{PatientID}`, pattern `{subject.label}`.
  (Verified: fw-meta normalizes it to `('{PatientID}', '{subject.label}')`.)

Follow that docs convention when authoring: extraction mappings source-left,
simple assignments destination-left.

In YAML, `mappings` accepts a list of `"template=pattern"` strings, a list of
`[template, pattern]` pairs, or a dict `{template: pattern}`. Use the string list —
it matches the docs and survives templates containing `=` poorly in dict form.

## Template syntax (left side)

f-string-like formatting of source fields into a string (`fw_utils.formatters.Template`):

| Syntax | Meaning |
|---|---|
| `{field}` | Insert the field value. Bare `field` with no curlies anywhere is an implicit `{field}`. |
| `{field/pat/sub}` | `re.sub(pat, sub, value)` before inserting. Escape literal `/` in pat/sub as `\/`. |
| `{field:format}` | Python format spec (e.g. `:.5` truncates to 5 chars); `strftime` pattern for timestamp fields. |
| `{field\|default}` | Use default when the value is None/empty. Without it, empty values render as `UNKNOWN`. |
| `{a}_{b}` | Multiple fields joined with literal text between. |
| `\{` `\}` | Literal curly braces. |

Modifier order when combined: `/pat/sub` → `:format` → `|default`, e.g.
`{file.name/\.dicom\.zip$//}` or `{PatientName/\^/_:.20|anon}`.

**Empty-value skip:** if ANY field referenced by the template is empty/None for a file,
the whole mapping is skipped for that file (no partial `UNKNOWN` extraction happens in
mappings — the `UNKNOWN` fill only applies where Template is used for formatting, e.g.
`dicom_instance_name`).

## Pattern syntax (right side)

Simplified-regex capture (`fw_utils.parsers.Pattern`). The regex is **anchored at both
ends** (`^...$`) — the pattern must match the ENTIRE formatted string, not a substring.

| Syntax | Meaning |
|---|---|
| `{field}` | Capture into destination field (dot notation). Default value regex: `.+`, but label fields (`*.label`, `group._id`, `file.name`) capture `[^/]+` — they never span a `/`. |
| `{field:constraint}` | Constrain the capture. **The constraint uses the SAME simplified syntax as the rest of the pattern** unless the pattern ends in `!r` — so `{acquisition.label:[^.]+}` in simplified mode is a broken "optional section" and fails to compile (`multiple repeat`). Regex character classes like `[0-9]+` require `!r` on the whole pattern (verified). |
| `{field:strptime}` | For timestamp fields (`*.timestamp`), a strftime pattern, e.g. `{session.timestamp:%Y%m%d}`. |
| `[part]` | Optional part, e.g. `[ses-]{session.label}`. Nestable. |
| `*` | Any chars EXCEPT `/` (like shell glob). |
| `**/` | Any chars INCLUDING `/` — "any number of leading directories". |
| `.` | Literal dot (glob-style, NOT regex any-char). |
| `\uid` | Matches a DICOM UID (dotted-numeric, optionally modality-prefixed). |
| `{2,3}` | Repetition of the preceding element (faux group). |
| `!r` suffix | Raw-regex mode: everything outside `{...}` is real regex and capture constraints are real regex. Write `.*` not `*` (a bare `*` is "nothing to repeat" — the docs' own regex examples get this wrong), and escape literal dots (`\.nii\.gz`). |
| `!i` suffix | Case-insensitive matching. Combine as `!ri`. |

Quantifiers are made lazy automatically (`*` → `*?`), so `{subject.label}_{session.label}`
on `S01_ses_01` captures `S01` / `ses_01` (shortest first match), not `S01_ses` / `01`.

**No match → no metadata, no error.** `Pattern.match` returns an empty dict when the
string doesn't match. The file then falls through to the cascade below and may end up
`failed` on required-field checks — the mapping itself never raises at import time.

## Temp variables and metadata references

- `{@var}` in a pattern captures into a temporary variable instead of real metadata.
- `{!@var}` in a LATER mapping's template references it.
- `{!subject.label}` in a template references an already-extracted destination field.
- Both `!` references must be assigned by an earlier mapping in the same rule, or
  validation fails with "cannot reference ... before assignment".

Example — build session label from two path pieces:

```yaml
mappings:
  - "{path}={@site}/{@visit}/**"
  - "{!@site}_{!@visit}={session.label}"
```

## Multiple mappings: fallback semantics

Extraction uses `setdefault`: the FIRST mapping that produces a value for a field wins;
later mappings only fill fields still missing. This makes ordered mapping lists act as
fallback chains:

```yaml
mappings:
  - "{StudyDescription}={session.label}"   # preferred
  - "{StudyInstanceUID}={session.label}"   # fallback if StudyDescription empty
```

## The full metadata cascade

Order of application per file (`MetaExtractor.extract`), each stage only filling fields
the previous stages left empty — EXCEPT overrides, which replace unconditionally:

1. **mappings** — in list order, setdefault semantics.
2. **type defaults** — for `type: dicom`, header-derived fields (see rule-schema.md
   for the DICOM default table).
3. **path defaults** — unmapped hierarchy labels are filled from parent directory
   names, nearest-first. For `level: acquisition` with path `a/b/c/file.txt` and
   nothing mapped: `acquisition.label=c`, `session.label=b`, `subject.label=a`.
   This is why a bare rule with no mappings "just works" on
   `subject/session/acquisition/file` trees — and why a forgotten mapping produces
   directory names as labels instead of an error.
4. **defaults** — rule-level literal fallbacks. **Trap:** because path defaults run
   FIRST, a `defaults:` entry for a hierarchy label (subject/session/acquisition)
   almost never fires — the directory name has already filled it. Verified: on
   `legacy/P90/T1/f.nii` with session unmapped, `defaults: [session.label=x]` still
   yields `session.label=P90`. The docs recommend defaults for exactly this case;
   they're wrong — use `overrides`. Defaults ARE right for fields with no path
   default (info.*, tags, cohort, etc.).
5. **overrides** — rule-level literal forced values, applied last, replacing
   anything; an empty override DELETES a field.

## Gotchas

- Pattern `*` does not cross `/`; use `**/` for arbitrary depth. A pattern without
  enough segments simply won't match deeper paths (anchored match).
- Pattern matching is case-SENSITIVE unless `!i`. (Filter expressions, by contrast,
  are always case-insensitive — don't confuse the two.)
- `.` is literal in patterns; write `*.dcm` naturally. In `!r` raw mode you're in real
  regex and must escape dots yourself.
- Label values are sanitized for path characters and truncated (64 chars; 128 for
  `acquisition.label`) at load time — see rule-schema.md field catalog.
- `session.timestamp` / `acquisition.timestamp` need timezone-aware parsing; setting
  them auto-populates `session.timezone` / `acquisition.timezone`.
- Field names may be abbreviated (`sub.label`, `acq`, `tstamp` aliases) — but always
  write them out in authored YAML files; abbreviations hurt the humans reading them.
