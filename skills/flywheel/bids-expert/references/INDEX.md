---
type: index
title: bids-expert reference index
tags: [index, bids, flywheel, curation]
source: BIDS 1.11.2-dev / schema 1.3.0-dev + Flywheel curation tooling
---

# bids-expert reference index

Read this first. It maps every reference file so you load only what you need. Two halves:
the **BIDS spec** (what valid BIDS looks like) and **Flywheel tooling** (how we curate data into
BIDS). The BIDS half is generated from the vendored schema (`scripts/build_bids_reference.py`);
the Flywheel half is hand-distilled from the repos.

## BIDS spec reference (`bids/`)

Foundations — read for any naming/validation question:

| File | What it covers |
| --- | --- |
| [`bids/_filename-grammar.md`](bids/_filename-grammar.md) | Filename syntax, label vs index, directory structure, inheritance principle, sidecars. |
| [`bids/_entities.md`](bids/_entities.md) | Every BIDS entity, its key, format, and canonical filename order. |

Per-datatype rules — each lists suffix groups, allowed entities (with required/optional), legal
extensions, and datatype-specific sidecar metadata. Each modality dir also has a
`_common-metadata.md` with the metadata shared across that modality's datatypes.

| Modality | Datatypes (files under `bids/<modality>/`) |
| --- | --- |
| MRI | [`anat`](bids/mri/anat.md) · [`func`](bids/mri/func.md) · [`dwi`](bids/mri/dwi.md) · [`fmap`](bids/mri/fmap.md) · [`perf`](bids/mri/perf.md) · [common](bids/mri/_common-metadata.md) |
| MRS | [`mrs`](bids/mrs/mrs.md) · [common](bids/mrs/_common-metadata.md) |
| PET | [`pet`](bids/pet/pet.md) · [common](bids/pet/_common-metadata.md) |
| EEG | [`eeg`](bids/eeg/eeg.md) · [common](bids/eeg/_common-metadata.md) |
| MEG | [`meg`](bids/meg/meg.md) · [common](bids/meg/_common-metadata.md) |
| iEEG | [`ieeg`](bids/ieeg/ieeg.md) · [common](bids/ieeg/_common-metadata.md) |
| EMG | [`emg`](bids/emg/emg.md) · [common](bids/emg/_common-metadata.md) |
| Microscopy | [`micr`](bids/micr/micr.md) · [common](bids/micr/_common-metadata.md) |
| Motion | [`motion`](bids/motion/motion.md) · [common](bids/motion/_common-metadata.md) |
| NIRS | [`nirs`](bids/nirs/nirs.md) · [common](bids/nirs/_common-metadata.md) |
| Behavioral | [`beh`](bids/beh/beh.md) · [common](bids/beh/_common-metadata.md) |

> For exhaustive/edge-case rules not captured here, the full machine-readable schema is vendored at
> `vendor/bids-schema/` and is the ground truth. Regenerate these pages with
> `uv run --with bidsschematools python3 ${CLAUDE_SKILL_DIR}/scripts/build_bids_reference.py`.

## Flywheel curation tooling (`flywheel/`)

How data actually gets curated into BIDS on a Flywheel instance:

| File | What it covers |
| --- | --- |
| [`flywheel/curation-workflow.md`](flywheel/curation-workflow.md) | The end-to-end pipeline: prep → precurate → curate → validate. Start here. |
| [`flywheel/container-to-bids-mapping.md`](flywheel/container-to-bids-mapping.md) | How Flywheel project/subject/session/acquisition/file map to BIDS, and where `info.BIDS` lives. |
| [`flywheel/curation-template.md`](flywheel/curation-template.md) | The curation template JSON *structure*: rules, definitions, `where`/`initialize`, `auto_update` interpolation. |
| [`flywheel/authoring-templates.md`](flywheel/authoring-templates.md) | *How to build/fix* a template: relabel-vs-template, `extends: reproin` + rules, a worked scanner-label example, disambiguation, testing. |
| [`flywheel/bids-client.md`](flywheel/bids-client.md) | The matching engine — algorithm, key source files, gotchas. |
| [`flywheel/curate-bids-gear.md`](flywheel/curate-bids-gear.md) | The gear that runs curation: inputs, config, outputs, reports. |
| [`flywheel/relabel-container-gear.md`](flywheel/relabel-container-gear.md) | Precuration gear: rename containers via CSV so the template matches. |
| [`flywheel/bids-app-gears.md`](flywheel/bids-app-gears.md) | Downstream BIDS-app gears (bids-mriqc, bids-fmriprep…): the empty-`/work/bids` failure and the curate-bids dependency. |

## Full curation templates (`flywheel/templates/`)

The complete shipped templates — `reproin.json`, `bids-v1.json`, `default.json` — vendored whole
for authoring/debugging custom templates (the code index only has them chunked per rule). Vendored
from bids-client 1.2.34; **rule ids differ across versions** — see `flywheel/templates/README.md`
before grounding against a specific instance.

## Code-grounded depth layer (`flywheel/code-index/`)

The 6 pages above are a curated overview. When a technical question needs the **actual
implementation** or a **real template rule** and the overviews don't cover it, search the code
index — 487 ground-truth cards (Python symbols + template rules/definitions) extracted straight
from the repos, each with `path:line`. No LLM paraphrase; you read the real source.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/search_code.py "intendedfor fieldmap resolver" -k 5
python3 ${CLAUDE_SKILL_DIR}/scripts/search_code.py "anat T1w rule" --kind template-rule
python3 ${CLAUDE_SKILL_DIR}/scripts/search_code.py "rename acquisition" --repo relabel-container
```

Filters: `--repo` (bids-client / curate-bids / relabel-container), `--kind`
(code / template-rule / template-def), `--full` (whole source, not a snippet).
Provenance + commit SHAs: [`flywheel/code-index/code-manifest.md`](flywheel/code-index/code-manifest.md).

**Regenerate for the latest repo versions:** `python3 ${CLAUDE_SKILL_DIR}/scripts/build_code_index.py --pull`.

Use this only as a fallback — answer from the lean `.md` files first; drop into the code index when
they run out.

## Scripts (`scripts/`)

| Script | Use |
| --- | --- |
| `search_code.py "<query>"` | Search the code index (depth layer) — ranked cards with `path:line`. |
| `analyze_curation_report.py <niftis.csv>` | Diagnose a curate-bids run from its report: real-vs-`unrecognized`, duplicate clusters, verdict. Stdlib, no SDK. |
| `simulate_template.py <template.json> <niftis.csv>` | **Offline dry-run** of a curation template: predicted coverage, suffix/acq distribution, `unrecognized`, and duplicate-path count — before a gear run. Stdlib, no SDK. |
| `pull_relabel_skeleton.py (--report <niftis.csv> \| --project <id> --api-key-env <ENV>)` | Build a relabel CSV with suggested ReproIn targets — from an existing report (offline) or a live project (SDK). Prefer `--report`. |
| `fetch_deployed_template.py (--job <id>\|--project <id>) --api-key-env <ENV>` | Read-only: report the curate-bids/bids-client version + template that actually ran. Needs SDK. |
| `build_bids_reference.py` / `build_code_index.py --pull` | Regenerate the spec pages / code index. |

All paths are `${CLAUDE_SKILL_DIR}/scripts/...`. The SDK scripts run via
`uv run --with flywheel-sdk [--with fw-client] [--with pandas] python ...` and compose with the
`fw-client` / `flywheel-sdk` / `fw-instance-inspector` skills for auth.

## Routing hints

- "Is this a valid filename / what entities can X have?" → `bids/_filename-grammar.md` +
  `bids/_entities.md` + the datatype page.
- "What metadata does a T1w need?" → `bids/mri/anat.md` + `bids/mri/_common-metadata.md`.
- "How do I rename acquisitions to curate?" → `flywheel/relabel-container-gear.md` +
  `flywheel/curation-workflow.md` + `pull_relabel_skeleton.py`.
- "Why didn't my file get curated?" → `flywheel/bids-client.md` (matching) +
  `flywheel/curation-template.md`.
- "How do I write/fix a curation template?" → `flywheel/authoring-templates.md` (+ `templates/` to
  copy from, `search_code.py --kind template-rule` for real rules). **Always dry-run with
  `simulate_template.py` before handing it over.**
- "A whole project's curation failed / duplicate paths" → SKILL.md diagnose-a-project playbook +
  `analyze_curation_report.py` + `fetch_deployed_template.py`.
- "bids-mriqc / bids-fmriprep got an empty dataset" → `flywheel/bids-app-gears.md` (it's a
  curation problem upstream — diagnose the project).
- Deep "what does this function/rule actually do?" (overview not enough) →
  `python3 ${CLAUDE_SKILL_DIR}/scripts/search_code.py "<terms>"` against the code index.
