---
type: Example Set
title: Worked Export Rule Examples
description: Simulator-verified export rule sets pairing a target layout description with the finished, commented YAML and the coverage it produces.
tags: [flywheel, export, rules, examples]
timestamp: 2026-10-14T00:00:00Z
---

# Worked Export Rule Examples

All examples were run through `scripts/simulate_export.py` (fw-meta 4.13.0) against this
fixture:

```yaml
project: {label: Study A}
files: [{name: protocol.pdf}]
subjects:
  - label: S01
    info: {cohort: control}
    files: [{name: consent.pdf}]
    sessions:
      - label: baseline
        files: [{name: notes.txt}]
        acquisitions:
          - label: 1 - T1w
            files: [{name: 1 - T1w.dicom.zip, type: dicom}, {name: T1w.nii.gz, type: nifti}]
          - label: 2 - rest
            files: [{name: 2 - rest.dicom.zip, type: dicom}, {name: rest.nii.gz, type: nifti}]
      - label: test-phantom
        acquisitions:
          - label: 1 - T1w
            files: [{name: T1w.nii.gz, type: nifti}]
  - label: S02
    sessions:
      - label: baseline
        acquisitions:
          - label: 1 - T1w
            files: [{name: T1w.nii.gz, type: nifti}, {name: qa.png, type: image}]
```

## Contents

- 1 — Full mirror including attachments at every level
- 2 — NIfTI only, flattened, grouped by cohort, test sessions dropped
- 3 — DICOM unzipped into clean series folders
- Anti-example — a path that drops a level (silent collision)

## 1 — Full mirror including attachments at every level

"Give me everything, laid out like Flywheel, with metadata." The site default
(`acq_asis`) exports acquisition files only, so this needs one rule per level.

```yaml
# Export: full project mirror, all levels, metadata sidecars.
# One rule per level because `level` gates which files a rule can see:
# a level: acquisition rule never touches subject/session/project attachments.
# Default paths mirror the hierarchy, so no collisions are possible.
# Sidecars (*.metadata.json) carry full container metadata: treat them as PHI.
type: export
rules:
  - level: project        # project attachments -> <project>/<file>
    metadata: true
  - level: subject        # subject attachments -> <project>/<subject>/<file>
    metadata: true
  - level: session        # session attachments -> <project>/<subject>/<session>/<file>
    metadata: true
  - level: acquisition    # acquisition files -> <project>/<subject>/<session>/<acq>/<file>
    metadata: true
```

Coverage: rule 0: 1, rule 1: 1, rule 2: 1, rule 3: 7, skipped 0.

## 2 — NIfTI only, flattened, grouped by cohort, test sessions dropped

"Just the NIfTIs, one folder per cohort, filename = subject_session_acquisition, skip
test sessions."

```yaml
# Export: NIfTI only, flat per cohort.
# Destination: <cohort>/<subject>_<session>_<acquisition>.nii.gz
# Unmatched by design: DICOM zips, PNGs, every attachment, sessions with "test" in the label.
type: export
rules:
  - level: acquisition
    include:
      - file.name=~*.nii.gz          # name filter, so the hardcoded .nii.gz in path is true
    exclude:
      - session.label=~test          # substring + case-insensitive: also drops "Latest", "TEST_2"
    # cohort may be unset: |unassigned avoids an UNKNOWN folder.
    # subject+session+acquisition in the name keeps every file unique (no _N renames).
    path: "{subject.info.cohort|unassigned}/{subject.label}_{session.label}_{acquisition.label}.nii.gz"
```

Coverage: rule 0: 3 (`control/S01_baseline_1 - T1w.nii.gz`,
`control/S01_baseline_2 - rest.nii.gz`, `unassigned/S02_baseline_1 - T1w.nii.gz`),
skipped 7, including `test-phantom`, as intended.

## 3 — DICOM unzipped into clean series folders

"Unzipped DICOMs, one folder per series, under subject/session."

```yaml
# Export: DICOM series unzipped, <subject>/<session>/<series>/<instances>
# unzip turns dst_path into a directory. Without the regex strip the folder
# would be literally "1 - T1w.dicom.zip/".
# unzip_path defaults to basename: member subfolders are flattened.
type: export
rules:
  - level: acquisition
    include:
      - file.type=dicom
    path: "{subject.label}/{session.label}/{file.name/\\.dicom\\.zip$/}"
    unzip: true
```

Coverage: rule 0: 2 → `S01/baseline/1 - T1w/<members>`, `S01/baseline/2 - rest/<members>`.
Note the single `/` closing the regex sub: `$//}` would append a `/` instead (see
xfer-rules-common.md, Templates).

## Anti-example — a path that drops a level

```yaml
- level: acquisition
  include: [file.type=nifti]
  path: "{subject.label}/{file.name}"   # BAD: session and acquisition dropped
```

Simulator output:
`COLLISION: Study A/S01/test-phantom/1 - T1w/T1w.nii.gz wanted S01/T1w.nii.gz, renamed to S01/T1w_1.nii.gz`.
On the server this rename is silent: no error, no warning, and which file gets `_1`
depends on snapshot order. Any path that omits a level must include something else that
keeps files unique.
