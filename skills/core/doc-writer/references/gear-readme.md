---
type: Doc Type Guide
title: Gear README
description: How to write a Flywheel gear README — start from the SSE skeleton template's README, fill each section from manifest.json and the gear code, and leave the user-owned sections alone.
tags: [doc-writer, fw-gear, gears, readme, manifest]
timestamp: 2026-09-24T00:00:00Z
resource: https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/skeleton/-/blob/main/README.md
---

# Gear README

The section layout is owned by the SSE skeleton template. Do not reproduce it from memory and do
not invent sections. Fetch it and fill it in:

- Template: <https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/skeleton/-/blob/main/README.md>
- Fetch raw:
  `glab api 'projects/flywheel-io%2Fscientific-solutions%2Fgears%2Ftemplates%2Fskeleton/repository/files/README.md/raw?ref=main'`
- The `flywheel-io/flywheel-apps/templates/skeleton` path is a dead namespace. Don't use it.

If the gear repo already has a README built from the skeleton, edit that file in place. Keep the
`[[_TOC_]]`, the Usage/FAQ anchor links, the `FAQ.md` and `CONTRIBUTING.md` links, and the trailing
`<!-- markdownlint-disable-file -->` line. Replace every `*{...}*` placeholder; a leftover
placeholder is a defect.

## Before writing

- `manifest.json` must exist at the repo root. If it's missing, stop and say so.
- Read `run.py`, the `fw_gear_<name>/` package (`parser.py`, `main.py`), and any output/metadata
  writing code. Inputs and config come from the manifest; outputs, workflow, and use cases come
  from the code.

## Manifest key mapping

| README field | Manifest key |
|---|---|
| Title `{{gear_name}} ({{gear_label}})` | `name`, `label` |
| Summary | `description` |
| Cite | `cite` |
| License | `license` |
| Classification → Category | `custom.gear-builder.category` |
| Docker image (if referenced) | `custom.gear-builder.image` |
| Inputs | `inputs` |
| Config | `config` |

## Writing each section

### Overview

- **Summary**: copy `description` verbatim. If it's vague or wrong against the code, keep it and
  flag it for the user rather than rewriting the manifest's text.
- **Cite / License**: copy verbatim. For `license: Other`, add the specific license if the repo's
  `LICENSE` file names it.
- **Classification**: fill Category from the manifest. For Gear Level, tick the box(es) the code
  supports (what container types it reads from `context.destination` / its parent). If the code
  doesn't make it clear, leave all unticked and flag it.

### Inputs

One bullet block per key in `inputs`, in manifest order, using the skeleton's field list:

- Name: the input key
- Type: `inputs.<key>.base` (`file`, `api-key`, `context`)
- Optional: `inputs.<key>.optional`, default `False` when absent
- Classification: based on `base`
- Description: `inputs.<key>.description` verbatim
- Notes: leave blank unless the code enforces something the description doesn't say (required
  file type, required classification). That's the one place to add it.

### Config

One bullet block per key in `config`: Name, Type (`config.<key>.type`), Description (verbatim),
Default (`config.<key>.default`, or `None` when absent). Don't add prose between entries.

### Outputs

The manifest has no outputs section, despite the skeleton's placeholder text. Get outputs from the
code.

- **Files**: scan for files written to `context.output_dir` / `/flywheel/v0/output` and SDK
  uploads. One block per file using the skeleton's field list. Type is the extension. Optional is
  whether it's written on every run (say "unknown" if you can't tell). Leave Classification and
  Notes blank.
- **Metadata**: list what the gear writes via `.metadata.json`, `context.metadata`, or SDK
  `update_info` / `update` calls, with the container level and the `info.` key path. No metadata
  written? Say so in one line.

### Pre-requisites

User-owned. Leave the skeleton's subsections as they are unless the user gives you the content.

### Usage

- **Description**: how the gear works inside Flywheel, not just what it computes. Where it reads
  from, what it does, where results land. Mark anything you inferred but couldn't confirm from code
  so the user can check it.
- **File Specifications**: user-owned. Don't modify.
- **Workflow**: a short numbered list plus a mermaid diagram adapted from the skeleton's (keep its
  `classDef` colors). Validate the diagram renders before delivering.
- **Use Cases**: only if the code makes them inferable (e.g. branches on config or input presence).
  Use the skeleton's Conditions checklist format. Otherwise leave the skeleton text.
- **Logging**: how to read the gear's log. Key messages, where failures show up. Skip if the code
  doesn't make it clear.

### FAQ / Contributing

Links only. Don't modify.
