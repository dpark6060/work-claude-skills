---
name: skill-maker
description: Creates new Claude Code skills (and optionally companion agents). Use when the user wants to build a new skill, add a slash command, or create a reusable prompt template. Triggers on "make a skill", "create a skill", "new skill", "build a skill".
---

You are building a new Claude Code skill in this repo. Your job is strategy and intake: decide whether a skill is even the right artifact, figure out its type and shape, gather the requirements, then write correctly-structured files to disk.

Skills live at `skills/<category>/<name>/SKILL.md` and are symlinked to `~/.claude/skills/<name>/` by `link_to_main_claude.sh`. Reference files go in `skills/<name>/references/`. Companion agents live at `agents/<name>.md` and are symlinked individually.

## The canonical rulebook — don't restate it, point to it

All structural and mechanical rules — directory layout, frontmatter fields, the 500-line limit, description-writing, progressive disclosure, anti-patterns — live in **`~/.claude/skills/shared/claude-skills-best-practices.md`**. That doc is the single source of truth. This skill owns *strategy* (what to build and why); the doc owns *mechanics* (how to write it correctly).

Read the relevant section as you reach each step — don't load the whole file (it's long; loading it wholesale is itself the anti-pattern it warns about):

| When you're... | Read |
|---|---|
| Deciding skill vs. CLAUDE.md vs. rule file | Community Insights → "Skills vs. CLAUDE.md" |
| Choosing the directory layout | §2 Anatomy (sanctioned structure) |
| Writing the description | §6 Descriptions — the highest-leverage part of the whole skill |
| Writing the body | §4 Lean SKILL.md, §5 Progressive Disclosure |
| Writing frontmatter / control flags | §8 Frontmatter Reference |
| Bundling scripts | §10 Bundled Scripts |
| Final sanity check | §13 Quick Checklist, §11 Anti-Patterns |

---

## Step 0 — Is a skill even the right answer?

Before building anything, confirm a skill is the correct artifact. The cost of a skill is a permanent description in every session's context, so it has to earn that.

| The need is... | Build a... |
|---|---|
| An always-on rule for every session (style, conventions, behavior) | CLAUDE.md addition |
| A standing coding/domain standard referenced on demand | `rules/` file |
| A specialized workflow needed *sometimes* | Skill (continue below) |
| A prompt you've pasted 3+ times | Skill (continue below) |

Rule of thumb: if the instructions wouldn't hurt to have loaded in *every* conversation, they belong in CLAUDE.md or a rule, not a skill. If it's only needed occasionally, it's a skill. (See the doc's "Skills vs. CLAUDE.md" section.) If a skill isn't the right call, say so and stop.

---

## The Three-Layer Architecture

This repo's system has three layers in a strict hierarchy: **Reference files → Skills → Agents**. Each does one job and never the job of the layer above or below it. (This framing is repo-specific and not in the rulebook — it's how skills plug into the agent system here.)

- **Layer 1 — Reference files** (`skills/<name>/references/*.md`): one sub-topic, maximum depth, loaded on demand. Full schemas, edge cases, advanced patterns for one use case. Never auto-loaded; the skill decides when to pull it in. Many reference files feed one skill. Structure them per the [OKF format](#reference-file-format-okf).
- **Layer 2 — Skills** (`skills/<name>/SKILL.md`): one domain, always-applicable rules, gateway to reference files. Overview, the rules that always apply, the workflow, quality standards, and explicit pointers telling Claude when to load which reference file. No deep single-topic detail (that's Layer 1), no cross-domain orchestration (that's Layer 3).
- **Layer 3 — Agents** (`agents/<name>.md`): one role, orchestration only, no domain knowledge. Which skills to invoke for which tasks and how to coordinate with other agents. Domain knowledge lives entirely in the skill and its references.

**Content allocation** — when deciding where something goes, ask *"does this apply every time, or only sometimes?"*

| Content type | Belongs in |
|---|---|
| Always-applicable rule for a domain | SKILL.md |
| Detail needed only for a specific sub-task | Reference file |
| Deep single-topic API/schema/example detail | Reference file |
| Which skill to use for which task | Agent body |
| How to coordinate across agents | PM agent body |

---

## Step 1 — Gather Requirements

Ask the user the following as a single grouped message. Don't proceed until you have answers.

1. **What does this skill do?** One clear sentence.
2. **What triggers it?** What phrases or situations should make Claude reach for it? (You'll turn these into the description per §6 — collect the user's actual words.)
3. **What does it produce?** Code written to files, a plan file on disk, a report in chat, guidance to follow before acting, etc.
4. **Skill type** — which fits best? (table below)
5. **Reference files needed?** Does it have sub-tasks where extra detail/examples/edge-cases are needed sometimes but not always? Those are reference-file candidates.
6. **Companion agent?** Should there also be an `agents/<name>.md` so the PM or other agents can invoke this as a subagent?

**Skill types:**

| Type | Description | Example |
|---|---|---|
| **Action** | Tells Claude how to do a task (before/during/after phases) | `code-writer`, `doc-writer`, `test-writer` |
| **Planning** | Multi-step workflow producing a deliverable (usually a file) | `change-planner`, `code-architect` |
| **Reference/Library** | Overview + guide index for a large domain; points to sub-files | `fw-gear`, `fw-client` |
| **Analysis/Review** | Reviews/audits/evaluates something; produces a report | `code-reviewer`, `code-architect-reviewer` |

**When reference files are worth it:** the skill covers several distinct sub-topics each noisy enough to clutter the base instructions; there are use-case-specific examples that only apply sometimes; SKILL.md is heading past the §4 length limit and some of that content is conditional. The canonical example is `fw-client`: SKILL.md covers instantiation, HTTP methods, and error handling (needed every time), while per-endpoint schemas live in `endpoints/*.md`, loaded only when a task needs that detail.

**When they're not:** the skill is narrow and everything applies on every invocation — splitting is just overhead. Don't split for the sake of structure.

---

## Step 2 — Design the Skill

Based on the answers, design the structure before writing. Match the body to the skill type:

**Action skill:** What rules files should it read before acting (check `rules/`)? What are the non-negotiables — the rules most likely to be violated? What are the Before / While / After phases?

**Planning skill:** What are the numbered steps (typical: Explore → Ask → Design → Present → Write)? What's the output file called and where does it go? Does it reference a shared format file (e.g. `~/.claude/skills/shared/plan_format.md`)?

**Reference/Library skill:** What's the overview content (install, key concepts, what it replaces)? What reference sub-files are needed and what does each cover? What's the guide-selection strategy (which guide for which task)?

**Analysis/Review skill:** What does it examine (code, a plan file, a PR diff, another skill's output)? What verdicts or output format does it produce? What concrete criteria does it use?

Before finalizing, sanity-check the layout against §2 (structure) and §5 (progressive disclosure) of the rulebook. Then present the structure to the user in plain language and let them adjust before anything is written to disk.

---

## Step 3 — Write the Files

Once the user confirms, write the files following the rulebook.

**Frontmatter** — see §8. Minimum is `name` + `description`; add control flags (`disable-model-invocation`, `user-invocable`, `allowed-tools`, `paths`, `context`/`agent`) only when the skill needs them. Do **not** add a `version` field — it isn't a sanctioned frontmatter field; this repo versions skills with git.

**Description** — see §6. This is the single highest-leverage thing in the skill: it's the only part Claude sees when deciding whether to invoke. Third person, front-load the key use case in the first ~250 chars, include the trigger phrases the user gave you in Step 1, and lean slightly pushy to avoid undertriggering.

**Body** — match the type pattern below, keep it under the §4 length limit, and split conditional detail into reference files rather than letting the body sprawl.

**Action skill body:**
```
You are [doing X]. Before [acting], consult [rules].

## Rules Reference        — table of rule files to read before acting
## Non-Negotiables        — the rules most likely to be violated (4-6 max)
## Before You [Act]       — checklist: what to read, check, ask
## While You [Act]        — principles to follow while working
## After You [Act]        — self-check questions; fix before presenting
```

**Planning skill body:**
```
You are acting as [role]. Your job is [goal]. Primary deliverable is [output].

## Your Mindset           — 3-5 principles
## Step 1 — [Explore]
## Step 2 — [Ask Targeted Questions]
## Step 3 — [Design]
## Step 4 — [Present to User]
## Step 5 — [Write to Disk]
```

**Reference/Library skill body:**
```
## Overview               — what it is, what it replaces, installation
## Guide Index            — table: guide file → what it covers
## Guide Selection Strategy — which guide to load for which task
## Key Concepts           — 5-8 critical concepts
## Quality Standards      — must-follow rules when using this library
```

**Analysis/Review skill body:**
```
You are reviewing [X]. Your job is [goal]. You produce [output].

## What You Are Evaluating  — in-scope vs. out-of-scope
## Evaluation Criteria      — concrete, specific criteria, not vague principles
## Verdicts / Output Format — what the output looks like
## What Good / Bad Looks Like — examples or heuristics
```

**Reference files (if any):** write each to `skills/<name>/references/<guide-name>.md` as a focused standalone guide on its topic — not a summary of SKILL.md. SKILL.md points to it; it holds the detail. Structure every reference file per the OKF format below.

**Companion agent (if any):**
```
---
name: <name>
description: <what it does; when to assign it>
tools: <see below>
model: sonnet        # use opus for judgment-heavy roles (architects, reviewers, debugger)
skills:
  - <skill-name>
---
```
Tool selection:
- Read-only agents (reviewers, planners): `Read, Glob, Grep`
- Writing agents (code, docs, tests): `Read, Glob, Grep, Edit, Write, Bash, Skill`
- Coordination agents (PM): `Read, Glob, Grep, Bash, Task`

Keep the agent body short — the skill does the heavy lifting (the `skills:` array injects the full skill into the agent's prompt). Include only cross-skill routing and sequencing.

---

## Reference File Format (OKF)

Reference files (Layer 1) follow the **Open Knowledge Format** — a domain-agnostic spec for knowledge concept documents. It applies *only* to files under `references/`. It does **not** touch `SKILL.md` or agent frontmatter: those keep the fields the Claude Code harness parses (`name`, `description`, control flags) exactly as §8 defines them. The harness never reads reference-file frontmatter, so OKF fields here are purely for discovery, indexing, and progressive disclosure.

**Frontmatter on each reference file** — YAML block at the top:

```yaml
---
type: <concept kind>          # required, non-empty. e.g. "API Endpoint Schema", "Config Reference", "Example Set"
title: <human-readable name>  # recommended
description: <one sentence>    # recommended — feeds index.md and search snippets
tags: [x, y, z]               # optional — cross-cutting categories
timestamp: 2026-07-07T00:00:00Z  # optional — ISO 8601, last meaningful change
resource: <uri>               # optional — the underlying asset; omit for abstract concepts
---
```

`type` is the only required field. Pick descriptive, self-explanatory values — it isn't a registered enum. Custom keys are allowed; consumers must preserve unknown keys.

**Reserved filenames** (optional, per directory):
- `references/index.md` — directory listing for progressive disclosure. **No frontmatter.** Markdown sections with bulleted links, each entry carrying the linked file's `description`. Add one once a skill has several reference files so the skill can point to the index instead of enumerating files inline.
- `references/log.md` — change history, newest first. ISO `YYYY-MM-DD` date headings; entries are prose, optionally prefixed `Update` / `Creation` / `Deprecation`.

**Standard section headings** (conventional, use when they fit): `# Schema` (column/field descriptions), `# Examples` (concrete usage), `# Citations` (external sources backing the doc, at the end, numbered `[1] [text](url)`).

Full spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

---

## Step 4 — Remind the User

After writing all files:

```
Run `./link_to_main_claude.sh` from the repo root to symlink the new skill (and agent if created).
```

If an agent was created, also remind them Claude Code may need a restart to pick it up (agent definitions load at session start).

---

## What NOT to Do

- Don't restate the rulebook's mechanics in the new SKILL.md — link to `~/.claude/skills/shared/claude-skills-best-practices.md` so there's one source of truth.
- Don't duplicate content between SKILL.md and its reference files — SKILL.md points, references hold the detail.
- Don't invent rule files that don't exist — only reference files that actually exist in `rules/`.
- Don't add logging instructions unless the skill type warrants it.
- Don't write implementation code in the skill file — skills are instructions, not implementations.
