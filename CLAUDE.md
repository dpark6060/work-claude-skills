# Repository Guide

This repo is a version-controlled Claude Code configuration: coding rules, skills, agent
definitions, and the personal global instructions. It is cloned once and **symlinked** into
`~/.claude/` so a `git pull` updates your live Claude config with no copy step.

This file is the guide for working *in this repo*. It is NOT the global instructions Claude
loads. The global instructions (`~/.claude/CLAUDE.md`) are now owned and linked by the Personal
Claude config repo (`~/Projects/Personal/PersonalClaude/global_config/CLAUDE.md`). A copy is kept here
in `global_config/CLAUDE.md` for reference only — this repo no longer links it.

## Layout

```
CLAUDE.md                  # this file — guide for editing the repo
global_config/CLAUDE.md    # reference copy of global instructions (linked by Personal repo, not here)
link_to_main_claude.sh     # creates all the ~/.claude symlinks (safe to re-run)
README.md                  # human-facing overview (may lag the actual layout)
rules/                     # standing instructions Claude reads as rules → ~/.claude/rules/
  general_coding/          #   GeneralCoding, Functions, Classes, UnitTests
  flywheel_specific/       #   sdk/, gears/, bug_reports/ guides
skills/                    # on-demand skill modules → ~/.claude/skills/ (flattened)
  core/                    #   code-architect, code-writer, code-reviewer, debugger, ...
  flywheel/                #   fw-gear, fw-client, flyw-cli, fw-instance-inspector, ...
  meta/                    #   skill-maker, skill-audit, bootstrap-validator, write-claudemd
  orchestration/           #   pipeline-babysitter, lint-fixer
  tools/                   #   gitlab, jira
  shared/                  #   reference files shared across skills (no SKILL.md)
agents/                    # subagent definitions (one .md each) → ~/.claude/agents/
hooks/  scripts/  misc/    # supporting material, not linked
```

## How linking works

`link_to_main_claude.sh` is the install step. It:
- symlinks each subdir of `rules/` → `~/.claude/rules/<name>`
- finds every `skills/**/SKILL.md`, symlinks its **parent dir** into `~/.claude/skills/<name>`
  — the category dirs (`core/`, `flywheel/`, …) are organizational only and get **flattened**
  at the `~/.claude/skills/` level, so every skill directory name must be globally unique
- symlinks `skills/shared/` explicitly (it has no SKILL.md)
- symlinks each `agents/*.md` → `~/.claude/agents/<name>.md`

Re-run it after adding a new skill, agent, or rule subdir. Existing symlinks pick up edits and
`git pull`s automatically. The script never clobbers a real (non-symlink) file at a target.

## Conventions

- **Names are hyphenated**, not underscored: `code-writer`, `code-architect`, `fw-gear`. A skill
  dir name, its `SKILL.md` `name:` field, and the matching `agents/<name>.md` must all agree.
  Any underscored name is stale.
- **A skill dir = a directory containing `SKILL.md`** plus optional reference `.md` files. Use
  the `skill-maker` skill to scaffold new ones rather than hand-rolling.
- **Before creating or restructuring a skill, read `skills/shared/claude-skills-best-practices.md`** —
  especially the "Sanctioned directory structure" section (§2). It defines the required layout:
  `SKILL.md` alone in the base dir, with optional `references/`, `sources/`, `scripts/`, `server/`,
  and `.learnings/` subdirs. New skills must follow it.
- **Agents reference skills by name** via the `skills:` array in their frontmatter; that injects
  the full skill content into the agent's system prompt at startup.
- **Agent/skill changes need a Claude Code restart** to take effect — definitions load at session
  start.
- **Don't duplicate rule content into skills** — reference the rule file path instead.
- Editing `global_config/CLAUDE.md` changes your global Claude behavior the moment it's saved
  (it's symlinked live). Treat it with care.

## Setup on a fresh clone

```bash
git clone <repo-url> ~/code/claude-config
cd ~/code/claude-config
bash link_to_main_claude.sh
```

Agent teams also require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `~/.claude/settings.json`.
