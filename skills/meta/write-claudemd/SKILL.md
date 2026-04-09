---
name: write-claudemd
description: A guide for how to write a detailed CLAUDE.md file for a repository.
version: 1.0.0
---

# Create CLAUDE.md

Generate a `CLAUDE.md` file for this project. This file serves as the primary context document for
AI coding assistants working in this codebase. It must be accurate, specific, and actionable — not
a vague overview.

Read the entire codebase before writing. Do not guess or generalize. Every claim in the file must
be verifiable from the code, config files, or project metadata.

## Required sources to read

Before writing anything, explore and read ALL of the following:

1. **Project metadata** — `pyproject.toml`, `package.json`, `Cargo.toml`, or whatever defines
   dependencies, build system, and project name. Note version constraints on all dependencies.
2. **Manifest or config** — any project-specific manifest (`manifest.json`, `app.yaml`, etc.) that
   defines inputs, outputs, configuration options, or deployment metadata.
3. **Entry point** — find the main entry point (e.g., `run.py`, `main.py`, `app.py`, `index.ts`,
   `main.rs`) and trace how it invokes the core logic.
4. **Core orchestration** — find the top-level function or class that drives the main workflow.
   Trace the full call chain from entry point through to completion.
5. **All source files** in the main package/source directory — understand every module's role.
6. **Test files** — read enough tests to understand testing patterns, fixture conventions, mock
   strategies, and naming conventions.
7. **Dockerfile** (if present) — base image, non-language runtime dependencies (Java, system
   packages, etc.), venv or build artifact locations.
8. **CI config** (if present) — `.gitlab-ci.yml`, `.github/workflows/`, `Jenkinsfile`, etc.
9. **Pre-commit or linter config** (if present) — `.pre-commit-config.yaml`, linter settings in
   pyproject.toml, `.eslintrc`, etc.
10. **Constants, enums, or shared config** — look for files that centralize magic strings, tag
    names, format strings, error codes, or shared data structures. These reveal important domain
    concepts.

## Output structure

The file must have exactly three top-level sections: **Product**, **Structure**, and **Tech**.
Write them in that order.

---

### Section 1: Product

**Purpose**: Explain WHAT this project does and WHY, with enough specificity that someone could
understand the business logic without reading the code.

Must include:

- **One-line summary**: What this thing is (not marketing copy — a factual description).
- **What it does**: Numbered list of the full pipeline/workflow steps. Be specific:
  - Name the exact data sources (e.g., "reads from `session.info['series-metadata']`" not just
    "extracts metadata")
  - Name the exact outputs (e.g., "writes CSV to `{output_dir}/batch.csv`" not just "creates a
    file")
  - Name any external systems called (APIs, databases, subprocesses, third-party binaries) with
    the actual invocation pattern
  - Name the success/failure indicators (tags applied, exceptions raised, exit codes, status
    fields written)
- **Key constraints**: Bulleted list of hard rules the code enforces. Look for things like:
  - Run level or scope restrictions (must be a session, must be a project, requires specific
    input types)
  - Idempotency mechanisms (what prevents duplicate runs, what state is checked before proceeding)
  - Supported input types, formats, or modalities
  - Credential or secret sources — be specific about the provider and path/key names
  - Any third-party binaries, JARs, or CLIs with their exact filenames or commands
  - Rate limits, size limits, or other operational boundaries

Do NOT include:
- Package manager instructions (that goes in Tech)
- File listings (that goes in Structure)
- Dependency lists (that goes in Tech)

---

### Section 2: Structure

**Purpose**: Show HOW the code is organized and how data flows through it.

Must include:

- **Top-level layout**: Brief annotated tree of the root directory (only top-level items and
  immediate children of the source directory, not deeply nested). Each entry gets a short comment
  explaining its role.
- **Package layout**: Annotated tree of the main source package, grouped by subdirectory. Each
  file gets a one-line comment: `filename.py  # ClassName or function — what it does`
- **Data flow**: **This is the most important part of the entire document.** Show the actual call
  hierarchy from the entry point down through the main pipeline. Use an indented tree format:
  ```
  entry_point.py
    -> module.run()
         -> Orchestrator.execute()
              |-- step_one()        # does X
              |-- step_two()        # does Y
              |-- step_three()      # does Z
              `-- cleanup()         # does W
  ```
  Trace the real method names from the code. Include every significant method in the main
  execution path. Add a brief comment for each explaining what it does. Do not fabricate method
  names — every name must exist in the codebase.
- **Conventions**: Actionable rules derived from patterns you actually observe in the codebase.
  Only include conventions you can point to in multiple files. Look for patterns like:
  - Where constants/magic strings are centralized and the rule for not hardcoding them elsewhere
  - How shell/subprocess commands are constructed (quoting, shell=True avoidance, etc.)
  - Data model patterns (Pydantic, dataclasses, TypedDicts) and field aliasing conventions
  - Logging approach (logger setup pattern, no print statements, etc.)
  - Error handling patterns (custom exceptions, how failures are surfaced)
  - State/tagging mechanisms used for idempotency or status tracking

Do NOT include:
- Dependency lists (Tech section)
- Business logic explanations (Product section)
- Generic language conventions everyone knows (e.g., "use snake_case in Python")

---

### Section 3: Tech

**Purpose**: Everything needed to build, run, lint, and test the project.

Must include:

- **Language & Runtime**: Language and minimum version required (read from project config or
  Dockerfile, not guessed)
- **Package manager**: Which tool (`uv`, `poetry`, `pip`, `npm`, `cargo`, etc.) and the key
  commands for:
  - Install dependencies
  - Run tests
  - Run tests with coverage
  - Run linter
  - Run the entry point
- **Build system**: Build backend (hatchling, setuptools, webpack, etc.) and the built package name
- **Key dependencies**: Table with columns: package name, version constraint, and one-line
  purpose. Split into **runtime** and **dev** dependency groups. Read version constraints from
  the actual project config — do not omit them.
- **Docker** (if applicable): Base image, any non-language runtime dependencies installed in the
  image (Java, system packages, native libraries), working directory, venv location
- **CI/CD** (if applicable): CI system, inherited templates or shared configs, notable settings
  (language version, coverage thresholds, deployment targets)
- **Pre-commit hooks** (if applicable): List what's configured (formatter, linter, tests, build
  checks, etc.)
- **Linter config**: Which linter(s), any notable non-default settings from project config

Do NOT include:
- Code structure (Structure section)
- Business logic (Product section)

---

## Writing rules

1. **Be specific, not generic**. "Fetches credentials from AWS SSM under `/prod/service/api/`" is
   useful. "Manages credentials" is not. Always prefer the concrete detail from the code.
2. **Use exact names from the code**. Class names, method names, field names, tag values, config
   keys — all must match the actual codebase. If you're not sure of the name, re-read the file.
3. **No aspirational content**. Only document what the code actually does today, not what it
   should do or might do in the future.
4. **No redundancy between sections**. Each fact appears in exactly one section. If you find
   yourself repeating something, decide which section owns it and remove it from the other.
5. **Keep it under 200 lines total**. Density over length. If a section is getting long, you're
   being too verbose or including things that belong elsewhere.
6. **Version constraints matter**. Write `pydantic ~2.0` not just `pydantic`. Read them from the
   actual project config file.
7. **The data flow diagram is mandatory and non-negotiable**. This is the single highest-value
   piece of the document. Trace the real call chain from entry point to completion. Every method
   name must exist in the code.
