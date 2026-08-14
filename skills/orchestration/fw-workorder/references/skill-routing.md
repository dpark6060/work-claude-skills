---
type: Dispatch Table
title: fw-workorder Skill Routing
description: Binding dispatch table mapping every fw-workorder phase to the skill or agent that owns it, plus the rule for what to do when a capability is missing.
tags: [routing, orchestration, jira, clockify, gitlab, pm]
timestamp: 2026-08-12T00:00:00Z
---

# fw-workorder Skill Routing

> **Load when:** starting any phase that touches Jira, Clockify, GitLab, code, or a live
> Flywheel instance — which is most of them.

This table is binding. `fw-workorder` owns intake parsing, the gear index, the depth rubric,
and phase sequencing. Everything else is dispatched.

# Schema

| Phase | Need | Dispatch to | Mode / how |
|---|---|---|---|
| 0 | Read a Slack thread | Slack MCP | `slack_read_thread` with `channel_id` + `message_ts` parsed from the permalink |
| 0 | Read an email | Microsoft 365 MCP | `outlook_email_search` / `read_resource` |
| 0 | Pull action items from a meeting | `meeting-tickets` | Its `sweep` mode already parses transcripts — do not reimplement transcript parsing |
| 1–2 | Find epics by client + gear name | `Skill(jira)` | find-epic mode → `~/.claude/skills/jira/references/find-epic.md` |
| 3 | Gear name → local repo | **owned here** | `scripts/build_gear_index.py`, see [gear-index.md](gear-index.md) |
| 3b | Reconcile a dirty repo | **owned here** | `git` via Bash, see [gear-index.md](gear-index.md) |
| pre-flight | Claim about Flywheel behavior needs proving | `Skill(fw-verify)` | Only when the change rests on an unverified behavioral claim |
| pre-flight | Need live-instance facts | `Skill(fw-instance-inspector)` | e.g. "does this field actually exist on those projects?" |
| 4 | Reopen a closed epic, fix `SOW`/`Hourly` labels | `Skill(jira)` | → `~/.claude/skills/jira/references/transition-issue.md` |
| 4 | Create a story | `Skill(jira)` | → `~/.claude/skills/jira/references/create-ticket.md` |
| 2b | Read a closed epic's Clockify task status | `Skill(clockify)` | Read-only. Task also closed → **hard stop, flag at the gate** |
| 4b | Create a missing Clockify task | `Skill(clockify)` | → `~/.claude/skills/shared/tools/clockify/jira-sync.md`. Trigger the sync schedule and **wait for the pipeline** |
| 5 | Write the code in one repo | `Agent(pm)` | One dispatch per repo, in parallel, with a depth directive — see [delivery.md](delivery.md) |
| 6 | Push and open a draft MR | `Skill(gitlab)` | End-of-session MR workflow; `origin` only |
| 6 | Watch a failing pipeline | `Skill(pipeline-babysitter)` | Only if the user asks — not part of the default run |
| 7 | Comment on the story | `Skill(jira)` | → `~/.claude/skills/jira/references/post-comment.md` |
| 7 | Log the time | `Skill(clockify)` | **unattended** mode → `~/.claude/skills/clockify/references/ai-work-estimation.md` |

## Gear-domain skills available to `pm` dispatches

You do not call these yourself; name them in the dispatch when the work touches their
domain so `pm`'s teammates load them:

| Skill | When the change involves |
|---|---|
| `fw-gear` | `run.py`, `parser.py`, `manifest.json`, GearContext, gear config/inputs |
| `fw-client` | Raw Flywheel HTTP API calls |
| `flywheel-sdk` | Flywheel SDK Python code |
| `flyw-cli` | CLI invocations or shell scripts around them |
| `fw-gear-debugger` | Reproducing a failed job locally |
| `bids-expert` | BIDS curation, templates, relabel CSVs |
| `fw-import-rules` | Import rule YAML |
| `fw-reader-tasks`, `fw-v3-reader-tasks` | Reader task protocols, form JSON |
| `fw-condor` | Engine config, job routing |

# The missing-capability rule

When a phase needs something none of these provide:

1. **Do not** implement it inline, and do not implement it in this skill.
2. Identify the skill that owns that domain. Jira mechanics → `jira`. Time → `clockify`.
   Git forge → `gitlab`. Code → `pm`.
3. Add the capability there as a new reference file, and add a row to this table.
4. If genuinely no skill owns the domain, that is a new skill — a `skill-maker` job with a
   human in the loop, not something to improvise mid-run. Log it in `.learnings/ERRORS.md`
   and fall back.

The failure mode this prevents: the conductor slowly absorbing every domain until it is an
unmaintainable monolith and none of the capabilities are reusable outside it.

# Deliberate overrides

- **Clockify's confirmation table is skipped.** `clockify` normally shows a confirmation
  table and waits before posting a time entry. `fw-workorder` invokes it with an explicit
  `unattended` argument, which posts and reports instead. This is a user-chosen override
  recorded in both skills. Interactive `clockify` use is unchanged.
- **`pm` does not select its own pipeline.** `pm` normally picks its workflow by judgment.
  Here the depth directive in the dispatch decides, because `pm` sees one repo and cannot
  judge scope across the work order.
