---
type: Library Reference
title: Gear README
description: Where the gear README template lives and how to write one — hand off to the doc-writer skill, or follow the skeleton template's own placeholders if that skill isn't installed.
tags: [fw-gear, gears, readme, documentation]
timestamp: 2026-09-24T00:00:00Z
resource: https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/skeleton/-/blob/main/README.md
---

# Gear README

The gear README layout is owned by the SSE skeleton template's README:

- Template: <https://gitlab.com/flywheel-io/scientific-solutions/gears/templates/skeleton/-/blob/main/README.md>
- Fetch raw:
  `glab api 'projects/flywheel-io%2Fscientific-solutions%2Fgears%2Ftemplates%2Fskeleton/repository/files/README.md/raw?ref=main'`
- The `flywheel-io/flywheel-apps/templates/skeleton` path is a dead namespace. Don't use it.

## How to write it

**If the `doc-writer` skill is installed** (it's listed in the available skills), invoke it with
the Skill tool: `skill: "doc-writer"`, args naming the gear repo and "gear README". It loads its
`references/gear-readme.md`, which covers how to fill each section from `manifest.json` and the
gear code.

**If it isn't installed**, fetch the template above and follow its own instructions. Each
`*{...}*` placeholder says where its value comes from (e.g. `*{From "inputs.Input-File.base"}*`).
Replace every placeholder, keep the section structure and links, and read the gear code for the
sections the manifest can't fill (Outputs, Workflow, Use Cases, Logging).
