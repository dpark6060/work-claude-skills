---
type: Syntax Reference
title: Xfer Rule Sets — Common Syntax & Machinery
description: What import and export rules share — evaluation order, filter expression syntax, template syntax, field aliases, the rule-set spec envelope, and the repo map — source-verified.
tags: [flywheel, xfer, import, export, rules, filters, templates]
timestamp: 2026-10-14T00:00:00Z
resource: https://gitlab.com/flywheel-io/tools/lib/fw-utils
---

# Xfer Rule Sets — Common Syntax & Machinery

> **Load when:** authoring or debugging an import OR export rules file. Used by the
> `fw-import-rules` and `fw-export-rules` skills; each owns its direction-specific field
> catalog and workflow, this file owns the shared engines.

Verified against fw-meta 4.13.0, fw-utils 5.2.0, xfer 23.0.0, connector (2026-10),
cli 23.0.0. Re-verify with the probe pattern at the bottom when versions move.

## Contents

- Rule evaluation model
- Filter expressions (syntax, operators, string semantics)
- Templates (format syntax)
- Field aliases
- The rule-set spec envelope and managed rule sets
- Repos, clones, version skew

## Rule evaluation model

- Rules are evaluated **in list order**; the **first rule whose filters match** a file
  handles it. Later rules never see that file.
- Files matching NO rule are **skipped silently**: no error. They appear in the
  operation report only when the job was created with `report_skip` (`--report-skip`).
- Within one rule: a file matches when (ANY include matches OR include list is empty)
  AND (NO exclude matches). Exclude beats include. An excluded file falls through to the
  next rule — it is not globally skipped.
- Max 50 rules per job / rule set. `rules` and a rule-set reference are mutually
  exclusive in one request.

## Filter expressions

Format: `<field><operator><value>`, e.g. `name=~*.dcm`, `file.size>1GB`,
`session.label=~baseline`. The allowed **fields** differ by direction (import: file-stat
fields; export: Flywheel metadata fields) — see each skill's rule schema. Syntax and
operators are shared (`fw_utils/filters.py`).

| Op | Meaning | Applies to |
|---|---|---|
| `=~` | pattern match | strings (and sets: "any element matches") |
| `!~` | pattern non-match | strings/sets |
| `=` (or `==`) | equal | all |
| `!=` | not equal | all |
| `<` `>` `<=` `>=` | comparisons | number, size (`500KB`, `1.5GiB`), time (`2024-01-01`, prefix precision) |

**String matching semantics (source-verified, differs from most docs):**

- Always **case-insensitive**.
- `=~` values use **simplified glob syntax**, not regex: `*` = any chars except `/`,
  `**/` = any depth, **`.` is a literal dot**, `[opt]` = optional part. Append `!r` for
  raw regex.
- `=~` uses `re.search` — **substring** semantics. `name=~README` matches
  `old_README.txt`. Anchor with `!r` and `^...$`, or match the full structure.
- **Regex habits silently misfire.** `field=~.+` means "contains a literal dot", not
  "non-empty": verified False for `sub-01/anat`, True for `a.b`. For "has any value" use
  `field=~*` (verified False only when the field is missing). xfer's built-in BIDS export
  rule set ships `file.info.BIDS.Path=~.+` and is wrong for this reason.
- Plain `=` on strings is exact (case-insensitive) equality.
- Set-valued fields (`*.tags`) match when any element matches.

**Validation timing:** pydantic model validation of a rule does not always compile its
filters. xfer validates them when the job or rule set is created; a 422 names the bad
field and lists the allowed ones.

## Templates

f-string-like formatting used for: import mapping left sides, export `path`,
`dicom_instance_name`, and rule-set `label` templates (`fw_utils.formatters.Template`).

| Syntax | Meaning |
|---|---|
| `{field}` | Insert the value. Empty/None renders as **`UNKNOWN`** unless a default is given. |
| `{field\|default}` | Use `default` when empty/None. |
| `{field/pat/sub}` | `re.sub(pat, sub, value)` before inserting. **No trailing slash**: `{file.name/\.dicom\.zip$/}` strips the suffix (verified `T1`). `{file.name/\.dicom\.zip$//}` sets `sub` to `/` and yields `T1/`. Escape a literal `/` as `\/`. |
| `{field:spec}` | Python format spec: `{session.timestamp:.10}` → `2024-03-05` (string slice). A strftime spec (`:%Y%m%d`) only works on real datetime values — on an ISO string it raises `Invalid format specifier`. |
| `{a}_{b}` | Multiple fields joined with literal text. |
| `\{` `\}` | Literal braces. |

Modifier order when combined: `/pat/sub` → `:format` → `|default`.

## Field aliases

`fw_meta/aliases.py` + unique-prefix matching, shared by both directions: `sub`/`subj` →
`subject`, `ses`/`sess` → `session`, `acq` → `acquisition`, `proj` → `project`, `grp` →
`group`; bare `subject` → `subject.label` (same for project/session/acquisition); bare
`group` → `group._id`; bare `file` → `file.name`; `timestamp` →
`acquisition.timestamp`; `session.time`/`ts` → `session.timestamp`; `info.*` →
`file.info.*`; `classification.*` → `file.classification.*`; `.id` → `._id`. Unique
prefixes of any allowed field also resolve (`weight` → `session.weight`). The built-in export rule sets lean on this (`{project}/{subject}/{file}`).
Write canonical names in authored files.

## The rule-set spec envelope

A rules YAML is either a **bare list of rules** or a **full spec**:

```yaml
type: import | export        # must match the job type; mismatched = validation error
label: "{...} job label"     # optional job-label template
storage_kind: blob           # blob (default) | dicom (DICOMweb/AHI); import also dicom_connector
rules: [...]                 # 1–50 rules
fail_fast: ...               # optional
# import-only keys: scan_params, conflict_strategy, uid_scope — see fw-import-rules
```

- The CLI wraps a bare list as `{"type": "<import|export>", "rules": [...]}` and
  validates spec files against `GET /xfer/rule-sets/schema`. The check is **skipped
  silently if the schema fetch fails**.
- `--rule-set` accepts a **local file path** (rules get inlined into the job) or a
  **24-hex managed rule-set ID**. It cannot be combined with `--rules` or the
  per-rule flags.
- **Managed rule sets** are scoped to site, group or project, versioned, and stored as a
  YAML string capped at **8192 chars**, comments included. Keep the commented master in a
  repo; strip comments only if the push complains.
- **Default rule set:** a job with neither rules nor a rule-set ID gets the default for
  its type and storage kind, resolved **project > group > site**
  (`xfer/rule_sets/mappers.py` `get_default_rule_set`). xfer seeds built-ins from
  `xfer/rule_sets/built_ins/*.yaml`, which double as real-world examples.
- The published docs disagree with source in several places, e.g. a `job:` wrapper and
  `ext` filters that do not exist. The instance's `GET /xfer/rule-sets/schema` beats
  every doc and every local library version.

## Repos, clones, version skew

| Repo | Owns | Clone |
|---|---|---|
| fw-meta | `ImportRule`, `ExportRule`, filter field catalogs, extraction — rule semantics | `https://gitlab.com/flywheel-io/tools/lib/fw-meta.git` (public) |
| fw-utils | `Pattern`, `Template`, filter engines | `https://gitlab.com/flywheel-io/tools/lib/fw-utils.git` (public) |
| cli | `flyw import/export`, rule-set CRUD, client-side validation | `https://gitlab.com/flywheel-io/tools/app/cli.git` (public) |
| xfer | `/xfer` API: validation, rule-set storage, defaults, reports | `git@gitlab.com:flywheel-io/tools/app/xfer.git` (**private**, SSH) |
| connector | Execution: storage walk / snapshot scan, rule evaluation, transfer | `git@gitlab.com:flywheel-io/tools/app/connector.git` (**private**, SSH) |

Clone shallow (`--depth 1`) into the session scratchpad. For private repos set
`GIT_TERMINAL_PROMPT=0`: anonymous HTTPS 404s and `git` can hang on a credential prompt.
For library semantics, PyPI is faster than cloning:
`uv run --with fw-meta==<ver> python -I probe.py`.

**Version skew:** cli, xfer and connector each pin their own fw-meta. Observed 2026-10:
connector locks fw-meta 4.13.0 / fw-utils 5.2.0; xfer allows `>=4.0.0,<5`; the CLI
allows `>=4.0.0` with no upper bound. When a rule validates in one place and misbehaves
in another, compare versions first:

```bash
rg -n -A1 'name = "fw-meta"' <repo>/uv.lock
```

**Probe pattern** — verify any syntax claim in this file before relying on it:

```python
# uv run -q --with fw-meta==4.13.0 python -I probe.py
from fw_meta.exports import ExportRule
ctx = {"file": {"name": "x", "info": {"BIDS": {"Path": "sub-01/anat"}}}}
print(ExportRule.model_validate({"include": ["file.info.BIDS.Path=~*"]}).match(ctx))
```
