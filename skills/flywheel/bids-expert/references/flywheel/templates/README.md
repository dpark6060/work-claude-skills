---
type: flywheel-reference
title: "Vendored base curation templates"
description: "The full shipped reproin/bids-v1/default curation templates, with version caveats for grounding against a live instance."
tags: [flywheel, bids, curation, templates]
timestamp: 2026-07-15T00:00:00Z
---
# Vendored base curation templates

The full, shipped BIDS curation templates from `bids-client`, copied here so the real files are
directly readable and copyable when authoring or debugging a custom template (the code index only
holds them chunked per-rule/definition).

| File | What it is |
| --- | --- |
| `reproin.json` | The **ReproIn** template — the default `base_template` for curate-bids. Matches ReproIn-style acquisition labels (`anat-T1w`, `func-task-rest`, …). |
| `bids-v1.json` | Legacy `bids-v1` base template. |
| `default.json` | The base both extend (`extends: default`); generic dicom/sourcedata + project-file rules. |

## Version — read this before grounding anything

Vendored from **bids-client 1.2.34**. Deployed instances often run an **older** bids-client, and
the templates differ between versions — **rule ids and structure are not stable across versions.**

Concrete example (ticket #33861): the BMGF instance ran curate-bids `2.1.3_1.0.7`, whose ReproIn
template has a rule `reproin_json_file` for JSON sidecars. That rule **does not exist in 1.2.34** —
it was restructured (the equivalent is `project_files` → `project_file`). So when diagnosing a
specific run, confirm the deployed gear/bids-client version and don't assume these files match it.

To check a real run's template, pull it from the instance (the project's curation template
attachment, or the gear's `base_template` at that version) rather than trusting these.

## Regenerating

These are a manual copy. To refresh:

```bash
cp /Users/davidparker/Documents/Flywheel/GitLab/public/bids-client/flywheel_bids/templates/{reproin,bids-v1,default}.json \
   ${CLAUDE_SKILL_DIR}/references/flywheel/templates/
```
