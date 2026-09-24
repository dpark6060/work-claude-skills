---
type: Doc Type Guide
title: Developer Guide
description: How to write a client-handoff developer guide that lets the client's developers understand and safely change the code: six required sections, optional sections gated on code complexity, and no internal process or links.
tags: [doc-writer, developer-guide, handoff, client, architecture]
timestamp: 2026-09-24T00:00:00Z
---

# Developer Guide

This guide goes to a **client** receiving the code. Their developers will understand it, run it,
and change it with their own tools and workflow. Assume the reader is slow and short on
attention. They arrive with a task ("make it do X"), read the top, and jump. Usage belongs in the
README. Link to it instead of repeating it.

Template: `assets/developer-guide-template.md`. Copy it, fill the required sections, keep only the
optional sections whose trigger fires, and delete the rest. Remove every `<!-- ... -->` comment
from the output.

## Client-safe content

The guide must stand alone outside our organization. It must not contain:

- Links to internal systems: Confluence, internal GitLab repos or templates, Jira, Slack.
- Jira keys, ticket numbers, employee names, internal hostnames or site URLs.
- Our internal dev workflow: pre-commit hooks, qa-ci, branch naming, MR title rules, release
  pipelines. The client has their own.
- Real data of any kind. Examples and the worked trace use synthetic or test-fixture data only.

`git log` and CI config are good **sources**. Nothing from them is copied into the guide verbatim.

## Definition of done

The guide is done when **both** hold:

1. **Running it works.** In a clean checkout (`git worktree add` into the scratchpad, or a fresh
   venv), run every command in Running it exactly as written. Fix the guide wherever a command
   fails or needs an unwritten step. A step you couldn't run (no credentials, no Flywheel site,
   no Docker) is marked `(unverified)` in the guide and listed in your report.
2. **Where do I change X is true.** For each row, open the named file and confirm the named
   function or constant exists and does what the row says.

## Output location

Write the guide to `docs/developer-guide.md`. Create `docs/` if it doesn't exist.

## Before writing

1. Read the entry point (`run.py`, `main`, CLI module) and trace the main flow to its outputs. Do
   this before looking at the directory tree.
2. Read the lock file (`uv.lock`, `poetry.lock`, `requirements.txt`) to find how dependencies
   install, and the test config or CI config to find the test command.
3. Run `git log --name-only --no-merges -n 200` to find the changes people actually make (for
   Where do I change X and Common changes) and fix commits (for Sharp edges and Troubleshooting).
4. Count what the optional triggers need: source files (excluding tests), components, hops between
   components, behavior-changing constants, domain terms.

## Required sections

Every guide has these six, in this order. Every section opens with a one-line summary. Tables beat
prose. Diagrams go wherever there's a flow.

| Section | Source of truth | If the source is missing |
|---|---|---|
| Start here | Entry point, README | — |
| Architecture and workflow | Traced main flow | — |
| Where do I change X | Code, `git log` | — |
| Running it | Lock file, test config, your clean-checkout run | Mark `(unverified)` |
| Scope and limitations | Code (explicit rejections, `NotImplementedError`, unhandled branches, TODOs), README | Ask the user what scope was agreed with the client |
| Last verified | Today's date, `git rev-parse --short HEAD` | — |

## Optional sections

Include an optional section **only** when its trigger fires. Otherwise delete it. Don't write
"N/A". Small code gets the six required sections and nothing else. That's correct, not thin.

| Section | Include when | Source of truth |
|---|---|---|
| Component entries (inside Architecture) | 3+ components, or any component spread across 2+ files | Traced main flow |
| Worked trace | 3+ hops between components | Traced main flow, a test fixture |
| Responsibilities map | 5+ source files, not counting tests | Source files |
| Constants and levers | 3+ behavior-changing constants. With fewer, they become rows in Where do I change X | Source files |
| Runtime config | The code reads config, env vars, or CLI flags that the README doesn't already document | Manifest, argparse, `os.environ` reads |
| External dependencies | The code talks to an outside service (Flywheel API, cloud storage, another API) | Client init code, lock file, manifest inputs |
| Common changes | The same group of files changes together in 3+ commits | `git log` |
| Sharp edges | Evidence: comments warning against change, reverted commits, checks on specific names or versions | Code comments, `git log` |
| Debugging a run | Reproducing a failure takes more than running the tests | Code, logging setup |
| Troubleshooting | Errors from your clean-checkout run, or fix commits for user-visible errors | Your run, `git log --grep fix` |
| Glossary | 3+ domain terms a new developer wouldn't know | Code, README |

## Writing the required sections

### Start here

Three sentences: what the code does, who it's for, and which file to open first. Link to the
README for usage. Most readers stop here. It has to work alone.

### Architecture and workflow

Describe the system as **conceptual components**, not files. A component is a job the system
does, and the classes and methods that do it often live in different files. Validation might be
`Validator` in `validate.py`, `ErrorLog` in `logging_utils.py`, and `check_header()` in
`parser.py`.

To find components:

1. Trace from the entry point through the workflow. Each workflow step is a candidate component
   (Parsing, Validation, Output writing, Metadata upload).
2. Group the classes and methods that serve each step, whatever file they're in.
3. Keep to 3–7 components. More than 7 means you're listing files. One means you stopped at the
   entry point.
4. Name components the way the code names them (docstrings, comments, log messages). Don't invent
   names.

Always write:

- A mermaid diagram of the workflow with **components as nodes**. Validate it renders.
- A numbered workflow description, one line per step, naming the component that does it.

When the component-entries trigger fires, add one entry per component in this shape:

```markdown
#### Validation
Rejects input files whose headers don't match the schema, and logs every failure before exiting.
- Pieces: `Validator` (`fw_gear_x/validate.py`), `ErrorLog` (`fw_gear_x/logging_utils.py`),
  `check_header()` (`fw_gear_x/parser.py`)
- In: parsed file records. Out: valid records, plus an error log file on failure.
- Workflow step: 2
```

Stay at class and module level. Function-level detail goes stale fast. It belongs only in Where do
I change X.

### Where do I change X

The section readers use most. A table of task → exact location:

| To change... | Edit |
|---|---|
| The output filename | `fw_gear_x/main.py:build_output_name()` |
| Which headers are required | `REQUIRED_HEADERS` in `fw_gear_x/validate.py` |

Take the rows from the changes `git log` shows people making, and from the behavior a client would
plausibly want different. 5–12 rows (fewer for small code). Every row passes the definition-of-done
check.

### Running it

The minimum to prove the code works before changing it: install dependencies, run the code, run
the tests. Use the repo's package manager, since the client gets the lock file. No hooks, linters,
or CI steps.

- Prerequisites with versions, from the lock file or Dockerfile, not from memory.
- Numbered, copy-pasteable commands. One command per step.
- Each of "run the code" and "run the tests" ends with its expected output.
- For a gear, say how it runs on a Flywheel site (which inputs, which container level) and how to
  run it locally if the repo supports that.

### Scope and limitations

What the code does **not** do, and what it assumes. One line each:

- Input it rejects or doesn't handle (file types, container levels, missing metadata).
- Assumptions about input data (naming, required fields, sizes).
- Things deliberately left out of scope.

The client will otherwise find these in production. If the code doesn't make the agreed scope
clear, ask the user. Don't infer a client agreement.

### Last verified

`Last verified: <YYYY-MM-DD> against <short SHA or version>.`

## Writing the optional sections

- **Worked trace.** One test-fixture input followed through the workflow, one line per hop, with
  the real function name and what the data looks like at that hop.
- **Responsibilities map.** The file-first view. One line per source file: what it holds, and
  which component it serves. Skip `__init__.py` and config files unless they hold logic. Don't
  list the classes again.
- **Constants and levers.** One table covers both, so a constant is never listed twice:

  | Name | Location | What it controls | Lever? |
  |---|---|---|---|
  | `MAX_RETRIES` | `fw_gear_x/client.py` | Retries on transient API errors | Yes. Raise for flaky networks |
  | `SCHEMA_VERSION` | `fw_gear_x/validate.py` | Schema the validator loads | No. Must match the manifest |

  "Yes" says what changes. "No" says what it's coupled to. After the table, list levers that
  aren't constants (a strategy class to swap, a flag in `run.py`, a registry to add to), one line
  each.
- **Runtime config.** Values set per run without a code change. A table of name, source
  (manifest / env / CLI), default, effect, and where it's read in code.
- **External dependencies.** Each outside service: what the code uses it for, the library and
  version, and what the client's environment must provide (API key input, permissions, installed
  gears, network access).
- **Common changes.** 2–3 short recipes for the recurring changes. "Adding a config option:
  1. add it to `manifest.json` `config` 2. read it in `parser.py:parse_config()` 3. add a test in
  `tests/test_parser.py`." Each step names a file.
- **Sharp edges.** Things a reasonable developer would "fix" that would break something: a pinned
  dependency, a name another system looks for, an ordering that matters. The edge, and what breaks.
- **Debugging a run.** How to reproduce a failed run locally, where logs go, how to run one
  component in isolation.
- **Troubleshooting.** Exact error string → cause → fix. Only errors with evidence.
- **Glossary.** Domain terms only, one line each.

## Common failures

These are the ways this doc goes wrong. Check for every one before delivering.

- **Internal leakage.** Jira keys, internal URLs, employee names, our dev workflow. Search the
  draft for `GEAR-`, `FLYW-`, `atlassian`, `gitlab.com/flywheel-io`, `pre-commit`, `qa-ci`.
- **Invented commands.** Every command ran in the clean checkout or is marked `(unverified)`.
- **Versions from memory.** Versions come from the lock file or Dockerfile.
- **Filling optional sections.** A section whose trigger doesn't fire gets deleted.
- **Directory-tree tours.** A tree listing every folder is not architecture. Components are.
- **Components that are just files.** If each component has exactly one piece and it's one file,
  regroup by workflow step.
- **Invented component names.** Use the code's own words.
- **Inferred scope.** Scope and limitations comes from code evidence or the user, never a guess
  about what the client agreed to.
- **Generic advice.** "Write tests", "follow PEP 8", "keep functions small". Delete on sight.
- **Repeating the README.** Link to it.
- **Speculative troubleshooting.** No entry without evidence.

## Examples

**Running it — bad:**

```markdown
Install the dependencies using your preferred package manager, then run the tests to make sure
everything works.
```

**Running it — good:**

````markdown
1. `uv venv --python 3.12 && source .venv/bin/activate`
2. `uv sync`
3. Run the tests: `uv run pytest` → `42 passed`
````

**Component — bad:**

```markdown
#### validate.py
Contains validation logic and helper functions for checking data.
```

**Component — good:** the Validation entry under Architecture and workflow above: a job, the
pieces across three files, in/out, and the workflow step.

## Report back

After writing, report:

- The path of the file written.
- Every step marked `(unverified)` and why.
- Optional sections included, and the trigger that fired for each.
- Questions for the user (agreed scope, component names you couldn't find in the code).
