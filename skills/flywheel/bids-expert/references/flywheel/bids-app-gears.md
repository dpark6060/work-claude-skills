---
type: flywheel-gear
title: BIDS-app gears (bids-mriqc, bids-fmriprep, …)
tags: [flywheel, bids, bids-app, mriqc, fmriprep, downstream]
source: bids-client flywheel_bids_app_toolkit 1.2.34 (context.py, prep.py, utils/query_flywheel.py)
repo: https://gitlab.com/flywheel-io/scientific-solutions/gears/bids-apps
---

# BIDS-app gears (bids-mriqc, bids-fmriprep, …)

The gears that *consume* a curated BIDS dataset and run a containerized BIDS App (MRIQC,
fMRIPrep, QSIPrep, etc.). They are **downstream of curation** — they do not curate. They share the
`flywheel_bids_app_toolkit` library in [[bids-client]].

## How they get their data

At runtime the toolkit builds a local BIDS tree and hands it to the app:

- `bids_dir = work_dir / "bids"` → `/flywheel/v0/work/bids` (the path in the classic error message)
  — `flywheel_bids_app_toolkit/context.py:186` (`BIDSAppContext.parse_directory_settings`).
- It downloads the project's **curated** files into that tree using the BIDS metadata that
  curate-bids wrote (`info.BIDS.Path`/`Filename`); files with no curation (`info.BIDS` empty/`NA`)
  are not downloaded. See `flywheel_bids_app_toolkit/utils/query_flywheel.py` and `prep.py`.
- The app then runs with `bids_dir` as a positional argument.

So the local BIDS tree is only as good as the curation. No curation → empty (or partial) tree.

## The signature failure: "empty result"

```
mriqc: error: Querying BIDS dataset at </flywheel/v0/work/bids> got an empty result.
```

This almost always means **curation upstream produced nothing valid**, not a bug in the app gear.
The app downloaded the project, found no files with valid BIDS metadata, and got an empty dataset.
Running curate-bids as a "pre-req" is necessary but **not sufficient** — curate-bids can *complete*
(or fail) while still having curated zero images (e.g. labels didn't match the template; see
[[curate-bids-gear]] gotchas and the duplicate-path mechanism). A green-ish curate-bids run with
everything `unrecognized` still yields an empty `/work/bids`.

## Diagnosing an empty/partial BIDS-app run

Work backward to curation — don't debug the app gear:

1. Identify the project from the failed job (`destination` → project).
2. Run the **diagnose-a-project-curation** playbook in `SKILL.md`: find the most-recent curate-bids
   run, pull its `*_niftis.csv`, and run `analyze_curation_report.py` on it.
3. If images are `unrecognized` / nothing reached a real `sub-XX/...` path, the fix is curation
   (precurate labels with [[relabel-container-gear]], then re-curate), **then** re-run the app.

## Notes

- bids-mriqc/bids-fmriprep need a FreeSurfer license (config `gear-FREESURFER_LICENSE`) for some
  workflows — unrelated to the empty-dataset error but a common second question.
- These gears run at the **project or subject/session** level; an empty result at subject level can
  mean that one subject has no curated data even if others do — check the report per subject.
- The version-drift caveat applies: app-toolkit behavior and the curation it depends on both track
  the bids-client version baked into the gear (see `templates/README.md`).
