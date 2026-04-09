# Output Conventions

This file defines where skills write their output files. All skills must follow this convention — change it here, and all skills pick it up.

## Directory Structure

```
<project-root>/
├── claude_log.md           ← shared activity log (all skills append here)
└── claude-work/            ← skill output files (no permission issues)
    └── <skill-name>/       ← one subdirectory per skill
        └── <output-file>
```

## claude_log.md

Lives at the project root. Every skill appends a brief entry after completing a task. See `~/.claude/skills/shared/logging.md` for the entry format and rules.

Do not put `claude_log.md` inside `claude-work/` — it's a cross-skill artifact that belongs at the top level.

## claude-work/

Skill-specific output files go in `claude-work/<skill-name>/`. Create the directory if it doesn't exist — `mkdir -p claude-work/<skill-name>`.

**Do not use `.claude/work/`.** That path sits inside the `.claude/` config directory, which requires elevated permissions to write to and will interrupt the workflow with a permission prompt.

### Registered skill outputs

| Skill | Directory | File |
|-------|-----------|------|
| `code_architect` | `claude-work/code_architect/` | `architecture-plan.md` |
| `change_planner` | `claude-work/change_planner/` | `change-plan.md` |
| `debugger` | `claude-work/debugger/` | `debug-findings.md` |
| `process_architect` | `claude-work/process_architect/` | `process-design.md` |
| `code_reviewer` | `claude-work/code_reviewer/` | `code-review.md` |
| `code_architect_reviewer` | `claude-work/code_architect_reviewer/` | `architecture-review.md` |
| `code_writer` | `claude-work/code_writer/` | `implementation-notes.md` |
| `pipeline_babysitter` | `claude-work/pipeline-babysitter/` | `failure-report.md` |
| `lint_fixer` | `claude-work/pipeline-babysitter/` | `fix-result.md` (co-located with failure report) |

### Adding a new skill

When a new skill needs to write output files:
1. Use `claude-work/<skill-name>/` as the output directory
2. Add a row to the table above
3. Add this line near the top of the skill's SKILL.md:
   > **Output**: See `~/.claude/skills/shared/output-conventions.md` for directory conventions.

## Reading across skills

Skills that aggregate work from multiple skills (e.g., `jira-comment`) should read:

```bash
find claude-work -name "*.md" 2>/dev/null | sort | xargs cat 2>/dev/null
```

## .gitignore note

`claude-work/` and `claude_log.md` are generated artifacts. Whether to commit them is a per-project call. To exclude them:

```
claude-work/
claude_log.md
```
