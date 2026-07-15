---
type: Example Set
title: Worked Import Rule Examples
description: End-to-end examples pairing a source directory tree and a verbal hierarchy description with the finished, commented rules YAML.
tags: [flywheel, import, rules, examples]
timestamp: 2026-07-14T00:00:00Z
---

# Worked Import Rule Examples

Each example: source tree → the user's verbal mapping description → the finished rules
file, commented the way deliverables should be commented. Filter/mapping syntax
details: rule-schema.md and template-pattern-syntax.md.

## Contents

1. Nested DICOM study with subject attachments and project docs
2. Flat directory, filename-encoded hierarchy
3. Regex extraction and label transformation
4. Mixed-depth source (deep DICOM + shallow single-session data)

## Example 1 — Nested DICOM study with attachments

```
study_data/
├── README.md
├── consent_template.pdf
├── SUBJ001/
│   ├── report.csv
│   ├── baseline/
│   │   ├── T1_MPRAGE/           # ~200 .dcm files
│   │   └── fMRI_REST/
│   └── followup/
│       └── T1_MPRAGE/
├── SUBJ002/
│   └── ...
└── scratch/                     # QA leftovers, don't import
```

> "Top-level folders are the subjects, inside those are the sessions, and each scan
> folder is an acquisition full of DICOMs. Each subject has a report.csv that should
> go on the subject. The README and PDF go on the project. Skip the scratch folder."

```yaml
# Import rules for study_data/ → fw://<group>/<project>
# Layout: <subject>/<session>/<acquisition>/*.dcm
# Rules are first-match-wins, so specific rules come first and every rule
# excludes the scratch/ tree and OS junk explicitly where it could match.

# --- Rule 1: per-subject report.csv → subject-level attachment ---------------
- level: subject
  include:
    - "depth=2"                  # directly inside a subject folder
    - "name=report.csv"          # (redundant with depth=2 alone; both kept for clarity)
  exclude:
    - "path=~scratch/**"
  mappings:
    # Path is <subject>/report.csv — capture the folder as the subject label.
    - "path={subject.label}/*"

# --- Rule 2: project docs at the source root → project attachments -----------
- level: project
  include:
    - "depth=1"                  # only files sitting at the root
  exclude:
    - "name=.DS_Store"           # depth=1 alone would import root junk too —
                                 # caught by simulating against the real tree
  mappings:
    - "path={file.name}"

# --- Rule 3: DICOM series → acquisitions --------------------------------------
# type: dicom parses headers, groups each series, and uploads one zip per series.
# subject/session labels are taken from the FOLDER names (not PatientID) per the
# study convention; acquisition.label falls back to DICOM defaults
# (SeriesNumber - SeriesDescription) because we don't map it.
- level: acquisition
  type: dicom
  include:
    - "depth=4"
    - "name=~*.dcm"
  exclude:
    - "path=~scratch/**"
  mappings:
    - "path={subject.label}/{session.label}/*/*"

# --- No catch-all rule ---------------------------------------------------------
# Anything else (scratch/, unexpected files, .DS_Store) is intentionally skipped.
# Files matching no rule are skipped SILENTLY — the coverage table in the summary
# lists exactly what falls through.
```

Notes on choices worth copying:

- `report.csv` had to be matched BEFORE the DICOM rule only if the rules could both
  match; here they can't (depth differs), but the attachment-rules-first ordering is a
  good habit — attachments are the exceptions, DICOM is the bulk.
- The subject rule maps only `{subject.label}` — `level: subject` requires nothing
  else. The file lands on subject `SUBJ001` with its original name.
- In rule 3 the acquisition segment is matched with `*` instead of
  `{acquisition.label}` deliberately, to let DICOM header defaults name the
  acquisition. Mapping the folder name instead is the other valid choice — this is
  exactly the kind of decision to surface to the user in the summary.

## Example 2 — Flat directory, filename-encoded hierarchy

```
nifti_drop/
├── S001_baseline_T1w.nii.gz
├── S001_baseline_bold-rest.nii.gz
├── S001_followup_T1w.nii.gz
├── S002_baseline_T1w.nii.gz
└── manifest.xlsx
```

> "It's all in one folder. Filename is subject_session_scan. The manifest is for me,
> don't import it."

```yaml
# Import rules for nifti_drop/ → one acquisition per file, hierarchy parsed
# from the filename: <subject>_<session>_<scan>.nii.gz

- level: acquisition
  include:
    - "name=~*.nii.gz"
  exclude:
    - "name=manifest.xlsx"       # explicit even though the include already skips it —
                                 # documents intent if xlsx→csv or includes loosen later
  mappings:
    # Underscore-delimited filename. Patterns are lazy: {subject.label} stops at the
    # FIRST underscore and the literal ".nii.gz" tail keeps the extension out of the
    # acquisition label, so S001_baseline_bold-rest.nii.gz →
    # subject=S001, session=baseline, acquisition=bold-rest.  (verified)
    - "name={subject.label}_{session.label}_{acquisition.label}.nii.gz"
```

Watch out: if subject IDs can themselves contain underscores (`S_001`), the lazy
first-underscore split breaks. Constraining captures with regex character classes
requires raw-regex mode — the whole mapping in real regex:

```yaml
    - "name={subject.label:S_[0-9]+}_{session.label:[^_]+}_{acquisition.label:[^.]+}\\.nii\\.gz!r"
```

(In simplified mode a `[^.]+` constraint fails to compile — `[...]` means optional
there. See template-pattern-syntax.md.)

## Example 3 — Regex extraction and label transformation

```
uploads/
└── batch1/
    ├── 004-001_V1/
    │   └── DICOM/               # .dcm files
    ├── 004-001_V2/
    │   └── DICOM/
    └── 011-042_V1/
        └── DICOM/
```

> "Folder names are site-subject_visit: 004 is the site, 001 the subject, V1 the
> visit. Subject label should be just the subject number, session should read
> 'Visit 1', and I want the site stored on the session info."

```yaml
# Import rules for uploads/ → hierarchy from <site>-<subject>_V<visit>/DICOM/*
# Uses regex mode (!r suffix) to capture pieces of one path segment into
# separate fields, then assignment mappings to build the final labels.

- level: acquisition
  type: dicom
  include:
    - "path=~**/*-*_V*/DICOM/**"
  mappings:
    # Regex mode (!r): everything is real regex — note ".*/" not "*/" (a bare * is
    # invalid regex; the docs' own examples get this wrong and fail to compile).
    # {@site} and {@visit_num} are TEMP variables (@) — captured for reuse below,
    # not written to Flywheel directly.
    - "path=.*/{@site:[0-9]+}-{subject.label:[0-9]+}_V{@visit_num:[0-9]+}/DICOM/.*!r"
    # Assignment mappings referencing temp variables need the ! prefix.
    - "session.label=Visit {!@visit_num}"
    - "session.info.site_id={!@site}"
```

Verified extraction for `batch1/004-001_V1/DICOM/img0001.dcm`:
`subject.label=001`, `session.label=Visit 1`, `session.info.site_id=004`.
This is the docs' transformation pattern ("V1" → "Visit 1") written with fw-meta's
temp-variable syntax. Order matters: temp variables must be captured by an earlier
mapping before a later template references them.

## Example 4 — Mixed-depth source

```
archive/
├── modern/                       # sub/ses/acq/file.dcm   (depth 4)
│   └── P01/2024-01-15/MR_T1/…
└── legacy/                       # sub/acq/file.nii       (depth 3, single-session)
    └── P90/T1/…
```

> "The modern folder is subject/session/acquisition DICOM. Legacy only has
> subject/scan — call every legacy session 'legacy'."

```yaml
# Import rules for archive/ — two layouts dispatched by path prefix.
# First-match-wins: each rule pins its subtree with a path include, so ordering
# between them doesn't matter, but keeping deep-before-shallow is the convention.

# --- modern/: full hierarchy, DICOM ------------------------------------------
- level: acquisition
  type: dicom
  include:
    - "path=~modern/**"
  mappings:
    # Literal prefix "modern/" consumes that segment; it never becomes a label.
    - "path=modern/{subject.label}/{session.label}/{acquisition.label}/*"

# --- legacy/: no session folder → constant session label ----------------------
- level: acquisition
  include:
    - "path=~legacy/**"
  mappings:
    - "path=legacy/{subject.label}/{acquisition.label}/*"
  overrides:
    # session.label is required at acquisition level and the path doesn't have it.
    # This MUST be an override, not a default: an unmapped session.label gets filled
    # by a PATH DEFAULT (the parent directory name → 'P90') before user defaults are
    # consulted. overrides apply last and win.  (verified)
    - "session.label=legacy"
  defaults:
    # Provenance stamp: which rule imported this file (handy when auditing later).
    # A default is fine here — info fields have no path-default to lose against.
    - "acquisition.info.import_rule=legacy_depth3"
```

**The defaults-vs-path-defaults trap (docs get this wrong):** the docs' own
multi-depth example uses `defaults: ['session.label=baseline']` to supply a missing
session on a `{sub}/{acq}/*` layout. Verified against fw-meta 4.13.0, that default
never applies — the path default fills `session.label` with the subject folder name
first (`legacy/P90/T1/file.nii` → `session.label=P90`). Hierarchy labels the path
could plausibly fill must be forced with `overrides`; `defaults` only fire when the
whole cascade left the field empty.
