# {{project_name}} Developer Guide

## Start here

{{Three sentences: what the code does, who it's for, which file to open first. Link to the README for usage.}}

## Architecture and workflow

{{One-line summary of how the system is put together.}}

```mermaid
{{workflow diagram, components as nodes}}
```

1. {{Step 1, naming the component that does it}}
2. {{Step 2}}

<!-- OPTIONAL: component entries. Include when 3+ components, or any component spans 2+ files. -->
### Components

#### {{Component name}}

{{One-line job.}}

- Pieces: `{{Class}}` (`{{path}}`), `{{function()}}` (`{{path}}`)
- In: {{what it receives}}. Out: {{what it produces}}.
- Workflow step: {{n}}

## Where do I change X

{{One-line summary.}}

| To change... | Edit |
|---|---|
| {{task}} | `{{path}}:{{function()}}` or `{{CONSTANT}}` in `{{path}}` |

## Running it

{{One-line summary.}}

Prerequisites:

- {{runtime + version from lock file / Dockerfile}}
- {{package manager + version}}
- {{system deps, Docker, credentials and where to get them}}

1. `{{install command}}`
2. Run the code: `{{command}}` → `{{expected output}}`
3. Run the tests: `{{command}}` → `{{expected output}}`

## Scope and limitations

{{One-line summary.}}

- {{Input it rejects or doesn't handle}}
- {{Assumption about input data}}
- {{Deliberately out of scope}}

<!-- ============================================================ -->
<!-- OPTIONAL SECTIONS. Keep a section only when its trigger fires. -->
<!-- Delete every section below whose trigger doesn't.            -->
<!-- ============================================================ -->

<!-- OPTIONAL: include when there are 3+ hops between components. -->
## Worked trace

{{One-line summary.}} Input: `{{test fixture path}}`.

1. `{{function()}}`: {{what the data looks like at this hop}}
2. `{{function()}}`: {{...}}

<!-- OPTIONAL: include when there are 5+ source files, not counting tests. -->
## Responsibilities map

{{One-line summary.}}

| File | Holds | Component |
|---|---|---|
| `{{path}}` | {{what it holds}} | {{component}} |

<!-- OPTIONAL: include when there are 3+ behavior-changing constants. Fewer go in Where do I change X. -->
## Constants and levers

{{One-line summary.}}

| Name | Location | What it controls | Lever? |
|---|---|---|---|
| `{{NAME}}` | `{{path}}` | {{effect}} | {{Yes. What changes / No. What it's coupled to}} |

Other levers:

- {{What to change, where, what it does}}

<!-- OPTIONAL: include when the code reads config, env vars, or CLI flags the README doesn't document. -->
## Runtime config

{{One-line summary.}}

| Name | Source | Default | Effect | Read in |
|---|---|---|---|---|
| `{{name}}` | {{manifest / env / CLI}} | `{{default}}` | {{effect}} | `{{path}}:{{function()}}` |

<!-- OPTIONAL: include when the code talks to an outside service. -->
## External dependencies

{{One-line summary.}}

| Service | Used for | Library + version | Your environment must provide |
|---|---|---|---|
| {{service}} | {{purpose}} | `{{lib}} {{version}}` | {{API key, permissions, network access, ...}} |

<!-- OPTIONAL: include when the same group of files changes together in 3+ commits. -->
## Common changes

### {{Adding a ...}}

1. {{Step, naming the file}}
2. {{Step}}

<!-- OPTIONAL: include when there's evidence (warning comments, reverts, name/version checks). -->
## Sharp edges

- {{The edge}}: {{what breaks}}

<!-- OPTIONAL: include when reproducing a failure takes more than running the tests. -->
## Debugging a run

{{How to reproduce a failed run locally, where logs go, how to run one component in isolation.}}

<!-- OPTIONAL: include when there's evidence (clean-checkout errors, fix commits). -->
## Troubleshooting

### `{{exact error string}}`

{{Cause and fix.}}

<!-- OPTIONAL: include when the code uses 3+ domain terms a new developer wouldn't know. -->
## Glossary

- **{{term}}**: {{one line}}

---

Last verified: {{YYYY-MM-DD}} against `{{short SHA or version}}`.
