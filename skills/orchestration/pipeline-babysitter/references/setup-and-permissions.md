# Pipeline Babysitter — Setup & Permissions Guide

The babysitter runs a polling loop and invokes shell tools, git, glab, and
sub-agents without user interaction. Without pre-approved permissions, Claude
will pause and ask for approval on every command — defeating the "walk away"
model. Add the entries below once and you're set for all gear repos.

---

## 1. Global permissions — `~/.claude/settings.json`

These permissions apply to every project. Add them to the `permissions.allow`
array and to `additionalDirectories`.

### `permissions.allow` additions

```json
"Bash(~/.claude/skills/shared/tools/gitlab/mr_info.sh:*)",
"Bash(~/.claude/skills/shared/tools/gitlab/mr_comments.sh:*)",
"Bash(~/.claude/skills/shared/tools/gitlab/mr_pipelines.sh:*)",
"Bash(~/.claude/skills/shared/tools/gitlab/pipeline_jobs.sh:*)",
"Bash(~/.claude/skills/shared/tools/gitlab/job_trace.sh:*)",
"Bash(sleep:*)",
"Bash(mkdir:*)",
"Bash(rm:*)",
"Bash(rmdir:*)",
"Bash(jq:*)",
"Bash(pre-commit:*)"
```

> Most of the others the babysitter needs (`git:*`, `glab:*`, `uv:*`) are
> already in the global settings from prior setup.

### `additionalDirectories` additions

The babysitter clones repos into `/tmp/pipeline-babysitter/`. Claude needs
explicit permission to read from and write to paths outside the project root.

```json
"additionalDirectories": [
  "/Users/davidparker/.claude",
  "/tmp/pipeline-babysitter"
]
```

Full `permissions` block after edits:

```json
"permissions": {
  "allow": [
    "Bash(chmod:*)",
    "Bash(ls:*)",
    "Bash(grep:*)",
    "Bash(uv:*)",
    "Bash(git:*)",
    "Bash(cat:*)",
    "Bash(glab:*)",
    "Bash(python3:*)",
    "Bash(which:*)",
    "Glob",
    "Read",
    "Bash(~/.claude/skills/shared/tools/gitlab/mr_info.sh:*)",
    "Bash(~/.claude/skills/shared/tools/gitlab/mr_comments.sh:*)",
    "Bash(~/.claude/skills/shared/tools/gitlab/mr_pipelines.sh:*)",
    "Bash(~/.claude/skills/shared/tools/gitlab/pipeline_jobs.sh:*)",
    "Bash(~/.claude/skills/shared/tools/gitlab/job_trace.sh:*)",
    "Bash(sleep:*)",
    "Bash(mkdir:*)",
    "Bash(rm:*)",
    "Bash(rmdir:*)",
    "Bash(jq:*)",
    "Bash(pre-commit:*)"
  ],
  "additionalDirectories": [
    "/Users/davidparker/.claude",
    "/tmp/pipeline-babysitter"
  ]
}
```

---

## 2. Per-project permissions — `.claude/settings.local.json`

Each gear repo that will be babysit needs its own local settings file.
Create `.claude/settings.local.json` at the repo root if it doesn't exist.

The `claude-work/pipeline-babysitter/` paths are where the babysitter and
`lint-fixer` sub-agent exchange their `failure-report.md` and `fix-result.md`
files. They are project-specific because they live inside the clone at
`/tmp/pipeline-babysitter/<project-name>/claude-work/pipeline-babysitter/`.

### Template

```json
{
  "permissions": {
    "allow": [
      "Bash(uv run pre-commit run:*)",
      "Bash(uv run pre-commit run --all-files:*)",
      "Bash(~/.claude/skills/shared/tools/gitlab/mr_pipelines.sh:*)",
      "Bash(~/.claude/skills/shared/tools/gitlab/pipeline_jobs.sh:*)",
      "Bash(~/.claude/skills/shared/tools/gitlab/job_trace.sh:*)",
      "Bash(~/.claude/skills/shared/tools/gitlab/mr_info.sh:*)",
      "Bash(~/.claude/skills/shared/tools/gitlab/mr_comments.sh:*)"
    ]
  }
}
```

> The tool script entries are redundant with the global settings but repeating
> them here means the project works even if the global entries are absent.

---

## 3. What each permission covers

| Permission | Used by | Why |
|---|---|---|
| `glab:*` | babysitter | All GitLab API calls |
| `git:*` | babysitter, lint-fixer | Clone, pull, commit, push |
| `uv:*` | lint-fixer | `uv run pre-commit run --all-files` |
| `pre-commit:*` | lint-fixer | Fallback if uv unavailable |
| `mr_info.sh:*` | babysitter | Resolve MR from branch |
| `mr_comments.sh:*` | babysitter | Check MR comments |
| `mr_pipelines.sh:*` | babysitter | Get pipeline list, detect auto-fix pipeline |
| `pipeline_jobs.sh:*` | babysitter | List jobs in a pipeline |
| `job_trace.sh:*` | babysitter | Read job log for failure classification |
| `sleep:*` | babysitter | 3-minute poll interval |
| `mkdir:*` | babysitter, lint-fixer | Create `/tmp/pipeline-babysitter/` and `claude-work/` |
| `rm:*` | babysitter | Cleanup clone on success |
| `rmdir:*` | babysitter | Cleanup empty `/tmp/pipeline-babysitter/` |
| `jq:*` | babysitter | Parse JSON from glab API calls |
| `/tmp/pipeline-babysitter` (dir) | babysitter, lint-fixer | Read/Write the repo clone and all work files |

---

## 4. Handoff files

The babysitter and `lint-fixer` sub-agent communicate via two files inside
the clone. Their paths follow this pattern:

```
/tmp/pipeline-babysitter/<project-name>/claude-work/pipeline-babysitter/failure-report.md
/tmp/pipeline-babysitter/<project-name>/claude-work/pipeline-babysitter/fix-result.md
```

Both are covered by the `additionalDirectories` entry for `/tmp/pipeline-babysitter`.
No additional `Write` permission entries are needed — file-level write restrictions
are not enforced separately once the directory is in `additionalDirectories`.

---

## 5. Quick checklist

Before running the babysitter on a new repo:

- [ ] `~/.claude/settings.json` has the 11 new `allow` entries from Section 1
- [ ] `~/.claude/settings.json` has `/tmp/pipeline-babysitter` in `additionalDirectories`
- [ ] `~/.claude/settings.json` has `git:*` and `glab:*` and `uv:*` (from earlier setup)
- [ ] Gear repo has `.claude/settings.local.json` with the entries from Section 2
- [ ] `glab auth status` passes (authenticated to GitLab)
- [ ] Docker is running (pre-commit hooks run inside Docker containers)
