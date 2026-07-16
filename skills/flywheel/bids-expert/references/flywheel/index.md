# Curation tooling

* [Authoring a custom curation template](authoring-templates.md) - How to build or fix a custom curation template — the relabel-vs-template decision, extends:reproin plus rules, a worked example, disambiguation, and the test loop.
* [BIDS-app gears (bids-mriqc, bids-fmriprep, …)](bids-app-gears.md) - Downstream BIDS-app gears (bids-mriqc, bids-fmriprep, …): how they consume a curated dataset and the empty-/work/bids failure mode.
* [bids-client (the matching engine)](bids-client.md) - The bids-client matching engine — the curation algorithm, key source files, the upload/curate/export workflows, and gotchas.
* [curate-bids gear](curate-bids-gear.md) - The curate-bids gear that runs bids-client curation across a project — inputs, config, outputs, and CSV reports.
* [End-to-end BIDS curation workflow](curation-workflow.md) - The end-to-end BIDS curation pipeline on Flywheel: prep, precurate, curate, and validate.
* [Flywheel container ↔ BIDS mapping](container-to-bids-mapping.md) - How Flywheel project/subject/session/acquisition/file containers map to BIDS and where info.BIDS metadata is stored.
* [relabel-container gear (precuration)](relabel-container-gear.md) - The relabel-container precuration gear — renaming subject/session/acquisition labels via CSV so the template matches.
* [The BIDS curation template](curation-template.md) - The curation template JSON structure — rules, definitions, where/initialize, and auto_update interpolation.

# Vendored Assets

* [Flywheel code index — provenance](code-index/code-manifest.md) - Provenance for the code index — source repos, commit SHAs, card counts, and how to regenerate.
* [Vendored base curation templates](templates/README.md) - The full shipped reproin/bids-v1/default curation templates, with version caveats for grounding against a live instance.
