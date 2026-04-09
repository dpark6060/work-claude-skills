# Claude Code Configuration

This repository contains rules, skills, and agent definitions for
[Claude Code](https://docs.anthropic.com/en/docs/claude-code). It is designed to be
cloned once and symlinked into `~/.claude/`, so that pulling updates to this repo
automatically updates your Claude configuration.

## What's in This Repo

| Directory | Purpose |
|---|---|
| `rules/` | Coding standards and domain guides that Claude reads as instructions |
| `skills/` | Reusable skill modules that extend what Claude can do |
| `agents/` | Subagent definitions for the Claude Code agent team feature |

---

## Setup

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- `~/.claude/` directory exists (created automatically by Claude Code on first run)

### Recommended: Symlink Setup

Clone the repo to a permanent location, then run the link script:

```bash
CLONE_DIR="$HOME/code/claude-config"   # or wherever you want it
git clone <repo-url> "$CLONE_DIR"
cd "$CLONE_DIR"
bash link_to_main_claude.sh
```

The script creates symlinks from `~/.claude/rules/`, `~/.claude/skills/`, and
`~/.claude/agents/` into this repo. The output will look like:

```
=== Linking rules ===
[LINKED] rules/general_coding → ~/.claude/rules/general_coding
[LINKED] rules/flywheel_specific → ~/.claude/rules/flywheel_specific

=== Linking skills ===
[LINKED] skills/architect_planner → ~/.claude/skills/architect_planner
...

=== Linking agents ===
[LINKED] agents/code_writer.md → ~/.claude/agents/code_writer.md
...
```

The script is safe to re-run — it skips anything already linked.

### Why Symlinks?

Because Claude reads rules and skills directly from `~/.claude/` at runtime, symlinking
means **any `git pull` to this repo is immediately live** — no copy step needed. New
content from the remote shows up the next time Claude starts a session.

The one exception: **new skills or agent files** added to the repo require re-running
`link_to_main_claude.sh` to create the new symlinks. Existing symlinks update
automatically.

### Alternative: Copy Instead of Symlink

If you prefer not to keep the repo around, copy the directories manually:

```bash
cp -r rules/general_coding ~/.claude/rules/
cp -r rules/flywheel_specific ~/.claude/rules/
cp -r skills/* ~/.claude/skills/
cp agents/*.md ~/.claude/agents/
```

You'll need to repeat this after any updates.

---

## Rules

Rules are markdown files Claude reads as standing instructions. They define coding
standards and domain knowledge that Claude should apply across all tasks.

| Rule File | When Claude Uses It |
|---|---|
| `rules/general_coding/GeneralCoding.md` | Always — primary coding standards |
| `rules/general_coding/Functions.md` | When writing functions |
| `rules/general_coding/Classes.md` | When writing classes |
| `rules/general_coding/UnitTests.md` | When writing tests |
| `rules/flywheel_specific/bug_reports/BugReport.md` | When writing Flywheel bug reports |
| `rules/flywheel_specific/gears/NewGear.md` | When scaffolding a new Flywheel gear |
| `rules/flywheel_specific/gears/Readmes.md` | When writing gear README files |

---

## Skills

Skills are structured knowledge modules that Claude loads on demand. Each skill lives
in its own directory with a `SKILL.md` entry point and optional reference files for
deeper topics. Unlike rules, skills are only loaded when you invoke them (either
directly or via an agent that has the skill configured).

### `architect_planner`
Designs software architecture before code is written. Explores the codebase, asks
clarifying questions, then produces a written plan file covering file structure, module
responsibilities, data flow, and key design decisions. Use this when you're starting
something new and want a design reviewed before anyone writes code.

### `architect_reviewer`
Reviews written code against an existing plan. Produces a verdict: compliant,
non-compliant, partially compliant, or "plan needs rethinking" (for cases where the
implementation exposed flaws in the original design). Use after code is written to
validate it against the architecture.

### `change_planner`
Plans a focused change to an existing codebase for a feature request or ticket.
Narrower than `architect_planner` — it explores first, then designs the minimum change
needed without touching unrelated code. Outputs a plan file. Use for adding features
to an existing system.

### `code_writer`
Writes Python code following project conventions. Reads the relevant rule files, checks
its own output against them before presenting, and follows the established patterns in
the codebase. Use when a plan exists and you need implementation.

### `code_reviewer`
Reviews Python code for quality, correctness, and adherence to project conventions.
Checks naming, structure, error handling, and style. This is a code quality review —
not a plan compliance check (use `architect_reviewer` for that).

### `debugger`
Diagnoses broken or failing code. Uses a hypothesis-driven approach: reads the error,
forms a theory, looks for evidence, confirms or rules out before proposing a fix. Avoids
the "just try changing things" approach. Use when something is broken and you need root
cause, not guesses.

### `test_writer`
Writes `pytest` + `unittest.mock` unit tests following project conventions. Follows the
Arrange/Act/Assert pattern, tests one scenario per test, mocks at the right depth, and
flags code that is inherently hard to test as a design smell. Use after code is written
to get coverage.

### `doc_writer`
Writes technical documentation. Produces READMEs, module docs, and usage guides with an
opinionated, direct tone — not filler prose. Reads the code before writing so the docs
reflect reality. Use when you need human-facing documentation.

### `flywheel-sdk`
Reference library for writing Python code using the Flywheel SDK. Covers client setup,
the data model (groups → projects → subjects → sessions → acquisitions → files), search,
gear job launching, permissions, and more. Load this when writing any code that calls
the Flywheel API.

### `fw-gear`
Reference library for writing Flywheel gears using the `fw-gear` Python package. Covers
`GearContext` (the core gear runtime object), accessing config options and input files,
writing outputs and metadata, running external commands, ZIP utilities, and
`manifest.json` structure. Load this when writing or modifying gear code.

### `bootstrap_validator`
Validates and repairs the project development environment at the start of a session.
Checks Python version against `pyproject.toml`, runs `uv sync`, verifies the venv and
package imports, installs and validates pre-commit hooks, checks MCP config and
credential files for JSON syntax errors, and verifies git state. Attempts automatic
fixes for each failure, logs all actions to `.bootstrap_log.md`, and produces a final
health report as a markdown table. Use at the start of a session on a new or
recently-pulled project.

---

## Agents

Agents are subagent definitions for the Claude Code [agent teams
feature](https://docs.anthropic.com/en/docs/claude-code/agents). Each agent has a
focused role, specific tools, and one or more skills pre-loaded into its system prompt.

| Agent | Role | Skills |
|---|---|---|
| `pm` | Coordinates the team — breaks down tasks, sequences work, synthesizes results | none |
| `architect_planner` | Designs architecture, produces plan files | architect_planner |
| `architect_reviewer` | Reviews code against plan | architect_reviewer |
| `change_planner` | Plans focused feature changes | change_planner |
| `code_writer` | Implements Python code | code_writer, flywheel-sdk, fw-gear |
| `code_reviewer` | Reviews code quality | code_reviewer |
| `debugger` | Diagnoses bugs | debugger |
| `test_writer` | Writes unit tests | test_writer |
| `doc_writer` | Writes documentation | doc_writer |

Agents are only available when the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` environment
variable is set (add it to `~/.claude/settings.json`).

---

## Skills vs Agents: When to Use Which

**Use a skill** when you're working alone with Claude in a normal conversation and want
Claude to apply a specific methodology or load domain knowledge:

```
/code_writer     → Claude writes code following project rules
/debugger        → Claude approaches your bug systematically
/fw-gear         → Claude loads gear library reference before writing gear code
```

Skills inject their content into the current conversation context. They're lightweight
and immediate.

**Use an agent** when the task is complex enough to benefit from parallelism or
specialization — multiple distinct steps that can run independently, or where you want
true separation between roles (e.g., the reviewer genuinely hasn't seen what the writer
did):

- A new feature that needs design → planning → implementation → review → tests
- A bug that requires investigation before any code changes
- A large codebase task where you want a PM to coordinate and synthesize

Agents run as subprocesses with their own context windows. The PM agent is the right
entry point for most multi-step work — it will sequence and delegate to the right
specialists.

**Rule of thumb:** If the task fits in one focused session with one role, use a skill.
If it spans multiple roles or steps that benefit from independent context, use agents.
