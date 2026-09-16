# Library References

* [fw-gear Basics: GearContext, Inputs, Outputs](gear-basics.md) - The canonical run.py pattern and how to use GearContext for config, input files, destination container, outputs, logging, and the SDK client.
* [fw-gear Manifest (manifest.json)](gear-manifest.md) - The manifest.json structure — name rules, config and input fields, runtime directory layout, and the output metadata spec.
* [fw-gear Metadata](gear-metadata.md) - Writing metadata back to Flywheel containers and files via .metadata.json (no SDK) and SDK methods, including QC results and file tags.
* [fw-gear Metadata Capability Matrix](metadata-capability-matrix.md) - What context.metadata can and cannot write in fw-gear 0.3.1 — the api-key requirement, the destination-and-up hierarchy rule, and a per-field file-vs-container matrix.
* [fw-gear Utils](gear-utils.md) - fw-gear utility helpers — exec_command, ZIP archives, SDK retry, launching child gears, FreeSurfer license, resource monitoring, and Nipype integration.
* [Gear Structure](gear-structure.md) - The skeleton gear's sanctioned file and module names (never rename run.py, main.py, parser.py), the reject table for common renames, and how to decouple main.py from Flywheel via run.py.
* [Gear Skeleton Setup](gear-skeleton-setup.md) - Which placeholder values to replace in manifest.json and pyproject.toml when starting a new gear from the skeleton template.
* [Gear README](gear-readme.md) - How to generate a gear README from manifest.json — which manifest keys map to which README fields, the Inputs/Config/Outputs templates, and the Usage sections to fill from code.
