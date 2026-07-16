---
type: flywheel-howto
title: "Authoring a custom curation template"
description: "How to build or fix a custom curation template — the relabel-vs-template decision, extends:reproin plus rules, a worked example, disambiguation, and the test loop."
tags: [flywheel, bids, curation, template, authoring, reproin]
source: bids-client 1.2.34 templates (reproin.json, default.json) + supporting_files/templates.py, rule_check.py
timestamp: 2026-07-15T00:00:00Z
---
# Authoring a custom curation template

The **how-to** for building/fixing a curation template. For *what the pieces are* (top-level keys,
rule anatomy, `auto_update` interpolation) read [[curation-template]] first — this page assumes it
and focuses on the procedure. Full real templates to copy from are vendored in `templates/`.

## First: do you even need a custom template?

| Situation | Do this |
| --- | --- |
| Labels just need renaming to ReproIn form (e.g. `anat-T1w`) | **Relabel instead** ([[relabel-container-gear]]) — simpler, no template to maintain. Use `pull_relabel_skeleton.py`. |
| You can't/won't modify the data, or want a reusable mapping for raw scanner labels | **Custom template** (this page). |
| ReproIn matches but a few rules are wrong/missing | Custom template that `extends: reproin` and overrides just those rules. |

A custom template earns its keep when the same odd naming recurs across projects, or when
relabeling thousands of acquisitions by hand isn't acceptable. Otherwise relabel.

## The build procedure

1. **Start from a base — never from scratch.** Top of the file:
   ```json
   { "extends": "reproin", "rules": [ ...your rules... ] }
   ```
   Your rules run *after* the inherited ones (first match wins). Inherited rules that misfire can be
   dropped with `"exclude_rules": ["<id>"]`. ([[bids-client]] covers match order.)
2. **Pick the definition** your files should populate — `anat_file`, `func_file`, `dwi_file`, etc.
   (the `template` field of your rule). Browse the vendored `reproin.json`/`default.json` for the
   available definitions and the properties each expects.
3. **Write the `where`** so it matches your acquisitions and nothing else. Anchor on
   `container_type: file` + `file.type` (`nifti`), then narrow with a `$regex` on `acquisition.label`
   and/or `file.classification.*`.
4. **Write `initialize`** to fill the BIDS fields (Suffix, Acq, Run, …) from context.
5. **Test** (see below) before trusting it.

## Initialize patterns (the real shapes)

- **Extract from a label** — `$regex` with a named `(?P<value>…)` group:
  ```json
  "Acq": { "acquisition.label": {"$regex": "(?i)\\((?P<value>[A-Z]+)"} }
  ```
- **Literal** — `"Suffix": {"$value": "T1w"}`
- **Conditional** — `$switch` over a field, cases by `$eq` or `$regex`, with a `$default`
  (mirrors `default.json`'s `bids_anat_file` Suffix switch):
  ```json
  "Suffix": { "$switch": { "$on": "file.classification.Measurement", "$cases": [
    {"$eq": ["T1"], "$value": "T1w"},
    {"$eq": ["T2"], "$value": "T2w"},
    {"$default": true, "$value": "T1w"} ] } }
  ```
- **Auto-incrementing run** — `"$run_counter": {"key": "anat.{file.info.BIDS.Suffix}"}`

## Worked example — mapping raw scanner labels

PRISMA-AKU's labels are raw SeriesDescriptions like `8 - T1 (AXI) - Standard-NOT FOR DIAGNOSTIC USE`
that ReproIn can't match (its `reproin_anat_file` rule requires `Intent=Structural` **and** a
ReproIn-style label). A custom rule that matches the raw label directly:

```json
{
  "extends": "reproin",
  "rules": [
    {
      "id": "kcl_scanner_anat",
      "template": "anat_file",
      "where": {
        "container_type": "file",
        "parent_container_type": "acquisition",
        "file.type": {"$in": ["nifti", "NIfTI"]},
        "acquisition.label": {"$regex": "(?i)\\b(T1|T2|FLAIR)\\b"}
      },
      "initialize": {
        "Suffix": { "$switch": { "$on": "acquisition.label", "$cases": [
          {"$regex": "(?i)FLAIR",   "$value": "FLAIR"},
          {"$regex": "(?i)\\bT1\\b", "$value": "T1w"},
          {"$regex": "(?i)\\bT2\\b", "$value": "T2w"},
          {"$default": true,         "$value": "T1w"} ] } },
        "Acq": { "acquisition.label": {"$regex": "(?i)\\((?P<value>[A-Z]+)"} },
        "Run": { "$run_counter": {"key": "anat.{file.info.BIDS.Suffix}.{file.info.BIDS.Acq}"} }
      }
    }
  ]
}
```

What it does: matches any NIfTI whose label contains T1/T2/FLAIR → sets `Suffix` by `$switch`, pulls
the plane (`AXI`/`SAG`/`COR`) out of the parentheses into `Acq`, and assigns a `Run` counter per
suffix+acq so repeats don't collide.

**Caveat — order and false matches:** `$switch` cases are tried top-down, so `FLAIR` comes before
`T2`. But `9 - T2 Mapping (AXI)…` would still match `\bT2\b` and be mislabeled `T2w` — it's a
quantitative `T2map`. Add an earlier case for it (a `T2\s*Mapping` case *above* the `T2` case), or
a separate rule, or exclude it. Treat this example as a starting skeleton and verify every family
against the spec pages (`references/bids/`).

### Realistic `Acq` is a multi-case `$switch`, not one regex

The single-regex `Acq` above (grab the parenthetical) is rarely enough. Real labels distinguish
scans by *both* plane (AXI/SAG/COR) and descriptor (Standard vs Gray_White; Fast), and the simple
grab loses one. Use an ordered `$switch` — **descriptor cases before plane cases**:

```json
"Acq": { "$switch": { "$on": "acquisition.label", "$cases": [
  {"$regex": "(?i)gray|white|contrast", "$value": "graywhite"},
  {"$regex": "(?i)standard",            "$value": "standard"},
  {"$regex": "(?i)(axi.*fast|fast.*axi)","$value": "axfast"},
  {"$regex": "(?i)(sag.*fast|fast.*sag)","$value": "sagfast"},
  {"$regex": "(?i)(cor.*fast|fast.*cor)","$value": "corfast"},
  {"$regex": "(?i)(\\baxi\\b|axial)",    "$value": "ax"},
  {"$regex": "(?i)(\\bsag\\b|sagittal)", "$value": "sag"},
  {"$regex": "(?i)(\\bcor\\b|coronal)",  "$value": "cor"},
  {"$default": true, "$value": ""} ] } }
```

Order is load-bearing: a `T1 (AXI) - Standard` must hit `standard` before `ax`, or two T1
families collapse to `acq-ax` and collide. A fully worked, validated version of this template is in
`/Users/davidparker/Documents/Claude/TerminalProjects/Bids/prisma-aku-project-template.json`.

> **`$switch` + `$regex` → string is a confirmed-real construct** (the shipped templates use
> `$switch`+`$regex` to set the boolean `ignore`, and `$switch`+`$eq` to set string `Suffix`). The
> `$regex`-case → *string*-value combination above is the natural extension, but it isn't in the
> shipped examples verbatim — **always dry-run it** (next section).

## Disambiguation, ignore, exclude

- **Same suffix in a session collides** unless distinguished — that's what `Acq`/`Run` are for.
  Without them, axial+sagittal+coronal T2s all become `…_T2w` → duplicate paths (the exact
  PRISMA-AKU failure; see [[curate-bids-gear]]). `Run` via `$run_counter` is the backstop: it makes
  any residual same-`(suffix,acq)` scans unique as `run-1`, `run-2` — but that's only *correct* if
  they really are repeats; if they're distinct scans, give them distinct `Acq` instead.
- **Two ways to keep a scan out of BIDS:**
  - **Leave it unmatched** — if no rule matches it, it stays `unrecognized` and is simply excluded
    from the BIDS tree. This is the simplest exclusion (it's what the PRISMA template does for
    localizers/PSIF/CALIPR — just don't write rules for them). Downstream apps ignore unrecognized.
  - **Explicitly `ignore`** — `ignore` is set at the **acquisition** level. The base template's
    `bids_acquisition` rule already sets it via a `$switch` on the `_ignore-BIDS` / `__dup<N>` label
    convention — so relabeling a scan `…_ignore-BIDS` excludes it. Because that inherited rule
    matches *every* acquisition (first-match-wins), you can't just add another acquisition rule;
    `exclude_rules: ["bids_acquisition"]` and replace it if you need custom ignore logic.
- **Decide on non-standard sequences first.** Quantitative/specialty scans (T2 Mapping, PSIF, MT,
  CALIPR, etc.) have no standard anat suffix. For each: map to a quantitative suffix from the spec
  if you need it downstream, or leave it unmatched/ignored. In PRISMA-AKU that's ~20% of the NIfTIs
  — don't let them get silently mislabeled by a greedy `\bT2\b` case.

## Test before trusting it

1. **Offline dry-run first** — `simulate_template.py <template.json> <niftis.csv>` predicts, without
   a gear run, how many files match each rule, the suffix/acq distribution, what stays
   `unrecognized`, and the **predicted duplicate-path count**. Iterate here until it's clean. (It's
   a predictor — it can't evaluate `classification`-based conditions and simplifies `auto_update`.)
2. **Real dry-run / single subject** — then run curate-bids on one subject with the template input.
3. **Read the report** — `analyze_curation_report.py <niftis.csv>`: images under `sub-…/anat/`,
   **0 duplicates**, no unexpected `unrecognized`.
4. **Trace a stubborn file** — `rule_check.verbose_rule_matches` (search the code index:
   `search_code.py "verbose rule matches" --repo bids-client`) steps through why a rule did/didn't fire.

## Pitfalls

- **First match wins** — rule order matters; put specific rules before general ones.
- **`auto_update` fields are recomputed every pass** and overwrite manual edits ([[curation-template]]).
- **`"NA"` is sticky** — a file unmatched on a prior run is skipped until you `reset` ([[bids-client]]).
- **Confirm the deployed version** — rule ids/definitions differ across bids-client versions
  (`templates/README.md`); author against the version that will run (`fetch_deployed_template.py`).
