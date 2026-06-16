# Output Conventions

This file defines where skills write their output files. All skills must follow this convention — change it here, and all skills pick it up.

## Directory Structure

```
<project-root>/
└── claude-work/            ← skill output files (no permission issues)
    └── <skill-name>/       ← one subdirectory per skill
        └── <output-file>
```

## claude-work/

Skill-specific output files go in `claude-work/<skill-name>/`. Create the directory if it doesn't exist — `mkdir -p claude-work/<skill-name>`.

**Do not use `.claude/work/`.** That path sits inside the `.claude/` config directory, which requires elevated permissions to write to and will interrupt the workflow with a permission prompt.

### Registered skill outputs

| Skill | Directory | File |
|-------|-----------|------|
| `code-architect` | `claude-work/code_architect/` | `architecture-plan.md` |
| `change-planner` | `claude-work/change_planner/` | `change-plan.md` |
| `debugger` | `claude-work/debugger/` | `debug-findings.md` |
| `process-architect` | `claude-work/process_architect/` | `process-design.md` |
| `code-reviewer` | `claude-work/code_reviewer/` | `code-review.md` |
| `code-architect-reviewer` | `claude-work/code_architect_reviewer/` | `architecture-review.md` |
| `code-writer` | `claude-work/code_writer/` | `implementation-notes.md` |
| `pipeline-babysitter` | `claude-work/pipeline-babysitter/` | `failure-report.md` |
| `lint-fixer` | `claude-work/pipeline-babysitter/` | `fix-result.md` (co-located with failure report) |

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

`claude-work/` is a generated artifact. Whether to commit it is a per-project call. To exclude it:

```
claude-work/
```
