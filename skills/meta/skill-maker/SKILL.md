---
name: skill-maker
description: Creates new Claude Code skills (and optionally companion agents). Use when the user wants to build a new skill, add a slash command, or create a reusable prompt template. Triggers on "make a skill", "create a skill", "new skill", "build a skill".
version: 1.0.0
---

You are building a new Claude Code skill. Your job is to ask the right questions, then write the correct files to disk.

Skills live at `skills/<name>/SKILL.md` in this repo. They are symlinked to `~/.claude/skills/<name>/` by `link_to_main_claude.sh`. Some skills have additional reference files in `skills/<name>/references/`.

Companion agents live at `agents/<name>.md` and are symlinked individually by `link_to_main_claude.sh`.

---

## The Three-Layer Architecture

Before building anything, understand where the piece you're building fits. The system has three layers in a strict hierarchy: **Reference files → Skills → Agents**. Each layer has one job and should not do the job of the layer above or below it.

### Layer 1: Reference Files (`skills/<name>/references/*.md`)

**One topic. Maximum depth. Loaded on demand.**

A reference file covers exactly one sub-topic at full detail — specific API parameters, edge-case examples, a single endpoint group, advanced patterns for one use case. It is never loaded automatically; the skill decides when the task needs it and loads it conditionally.

- Scope: one sub-topic per file
- Content: full schemas, complete examples, edge cases, gotchas
- When loaded: only when the current task requires that specific detail
- What it does NOT contain: overview, workflow, rules that always apply — those belong in the skill

Many reference files feed one skill.

### Layer 2: Skills (`skills/<name>/SKILL.md`)

**One domain. Always-applicable rules. Gateway to reference files.**

A skill covers everything needed to work in a domain (e.g., gear writing, code review, test writing). It defines the always-applicable rules, workflow phases, quality standards, and quality checks. Its secondary job is to know which reference file to load for which sub-task and to tell Claude explicitly when to reach for one.

- Scope: the whole domain/capability
- Content: overview, always-applicable rules, workflow, quality standards, conditional pointers to reference files
- When loaded: always, whenever the skill is invoked
- What it does NOT contain: deep single-topic detail (that's a reference file), or orchestration across multiple domains (that's an agent)

Many reference files serve one skill. One skill serves one or more agents.

### Layer 3: Agents (`agents/<name>.md`)

**One role. Orchestration only. No domain knowledge.**

An agent represents a specific engineering role (code writer, reviewer, PM). It defines which skills to invoke for which tasks and how to coordinate with other agents. Domain knowledge lives entirely in the skill and reference files — the agent body should be short and contain only sequencing logic and cross-skill routing.

- Scope: one engineering role
- Content: which skills to use and when, coordination with other agents, sequencing rules
- When loaded: when the agent is assigned a task by the user or the PM
- What it does NOT contain: domain knowledge, rules about how to write code/tests/docs — those live in skills

One agent invokes one or more skills. The PM agent coordinates across multiple agents.

### The Content Allocation Rule

When deciding where something belongs, ask: *"Does this apply every time, or only sometimes?"*

| Content type | Belongs in |
|---|---|
| Always-applicable rule for a domain | SKILL.md |
| Detail only needed for a specific sub-task | Reference file |
| Which skill to use for which task | Agent body |
| How to coordinate across agents | PM agent body |
| Deep single-topic API/schema/example detail | Reference file |

---

## Step 1 — Gather Requirements

Ask the user the following as a single grouped message. Do not proceed until you have answers.

**Required:**
1. **What does this skill do?** One clear sentence.
2. **What triggers it?** What phrases or situations should make Claude reach for this skill?
3. **What does it produce?** (e.g., code written to files, a plan file on disk, a report in chat, instructions to follow, guidance before writing)
4. **Skill type** — which best fits? (see types below)
5. **Reference files needed?** Does the skill have specific sub-tasks or use cases where extra detail, examples, or edge cases are needed — but not always? If so, those sub-topics are candidates for reference files that are loaded on demand. See the reference file philosophy below.
6. **Companion agent?** Should there also be an agent `.md` file so this skill can be invoked as a subagent by the PM or other agents?

**Skill types:**

| Type | Description | Example |
|---|---|---|
| **Action** | Tells Claude how to do a task (phases: before/during/after) | `code_writer`, `doc_writer`, `test_writer` |
| **Planning** | Multi-step workflow that produces a deliverable (usually a file) | `change_planner`, `code_architect` |
| **Reference/Library** | Overview + guide index for a large domain; points to sub-files | `fw-gear`, `fw-client` |
| **Analysis/Review** | Reviews, audits, or evaluates something; produces a report | `code_reviewer`, `code_architect_reviewer` |

**Reference file philosophy:**

Skills follow a two-tier structure within Layer 2:
- **SKILL.md** — core, always-applicable instructions. What the skill does, the rules that always apply, the workflow, and conditional pointers to reference files.
- **Reference files (Layer 1)** — detail, examples, and edge cases for specific sub-tasks. Only pulled into context when the task actually needs them. See the three-layer architecture above for what belongs here vs. in SKILL.md.

The `fw-client` skill is the canonical example: SKILL.md covers instantiation, HTTP methods, response handling, and error handling — things needed on every invocation. The endpoint schema detail lives in `endpoints/*.md` files, one per API tag. SKILL.md tells Claude to check an index file first, then load the specific tag file only if it needs full parameter/body schemas. The detailed endpoint files never pollute context for tasks that don't need them.

The default behavior is: **answer from SKILL.md first**. Only load a reference file if the task requires detail that isn't in SKILL.md. SKILL.md should contain enough to handle common questions and typical usage. Reference files exist for when the task pushes past that — specific endpoint schemas, edge-case examples, advanced patterns.

SKILL.md should tell Claude explicitly when to reach for a reference file:
> "If you need full parameter/schema detail for a Core API endpoint, read `endpoints/core_<tag>.md`."
> "If writing example code, see `references/examples.md`."

Claude reads these conditionals, decides if the current task triggers them, and only loads the file if it does.

**When to use reference files:**
- The skill covers multiple distinct sub-topics, each with enough detail to be noisy if always present
- There are use-case-specific examples that only apply sometimes
- There's domain-specific edge case detail that clutters the base instructions
- SKILL.md is getting large but some of that content is only needed for specific cases — split those cases out

**When NOT to use reference files:**
- The skill is narrow and focused — everything fits cleanly in one file
- All content applies to every invocation (splitting would just be overhead)
- The skill is already small; don't split for the sake of structure

---

## Step 2 — Design the Skill

Based on the answers, design the skill structure before writing anything:

**For Action skills:**
- What rules files (if any) should it read before acting? (check `rules/` for relevant guides)
- What are the non-negotiables — the rules most likely to be violated?
- What are the Before / While / After phases?
- Does it end with a log entry? (most skills do)

**For Planning skills:**
- What are the numbered steps? (typical: Explore → Ask → Design → Present → Write → Log)
- What is the output file called and where does it go?
- Does it reference a shared format file (e.g., `shared/plan_format.md`)?

**For Reference/Library skills:**
- What is the overview content? (installation, key concepts, what it replaces)
- What reference sub-files are needed? What does each cover?
- What is the guide selection strategy? (which guide for which task)

**For Analysis/Review skills:**
- What does it examine? (code, a plan file, a PR diff, output of another skill)
- What verdicts or output format does it produce?
- What are the concrete criteria it uses to evaluate?

Present the structure to the user in plain language before writing. Give them the opportunity to adjust before you write anything to disk.

---

## Step 3 — Write the Files

Once the user confirms the structure, write the files.

### SKILL.md Frontmatter

```
---
name: <skill-name>
description: <what it does and when to use it. Include trigger phrases.>
version: 1.0.0
---
```

### SKILL.md Body

Match the structure to the skill type:

**Action skill body pattern:**
```
You are [doing X]. Before [acting], consult [rules].

## Rules Reference
[table of rule files to read before acting]

## Non-Negotiables
[the rules most likely to be violated — 4-6 items max]

## Before You [Act]
[numbered checklist: what to read, what to check, what to ask]

## While You [Act]
[principles to follow while doing the work]

## After You [Act]
[self-check questions; fix before presenting]

[log entry instruction if applicable]
```

**Planning skill body pattern:**
```
You are acting as [role]. Your job is [goal]. Primary deliverable is [output].

## Your Mindset
[3-5 principles]

## Step 1 — [Explore/Understand]
## Step 2 — [Ask Targeted Questions]
## Step 3 — [Design]
## Step 4 — [Present to User]
## Step 5 — [Write to Disk]
## Step 6 — [Write Log Entry]
```

**Reference/Library skill body pattern:**
```
## Overview
[What the library/tool is; what it replaces; installation]

## Guide Index
[table: guide file → what it covers]

## Guide Selection Strategy
[which guide to load for which task]

## Key Concepts
[5-8 bullet points on critical concepts]

## Quality Standards / Usage Rules
[must-follow rules when using this library]
```

**Analysis/Review skill body pattern:**
```
You are reviewing [X]. Your job is [goal]. You produce [output].

## What You Are Evaluating
[what to look at; what counts as in-scope vs. out-of-scope]

## Evaluation Criteria
[concrete, specific criteria — not vague principles]

## Verdicts / Output Format
[what the output looks like; verdict categories if applicable]

## What Good Looks Like / What Bad Looks Like
[examples or heuristics]
```

### Reference files (if needed)

Write each reference file to `skills/<name>/references/<guide-name>.md`. Each should be a focused, standalone guide covering its stated topic — not a summary of the SKILL.md.

### Companion agent (if needed)

Agent frontmatter:
```
---
name: <name>
description: <what it does; when to assign it>
tools: <comma-separated list — see below>
model: sonnet
skills:
  - <skill-name>
---
```

**Tool selection:**
- Read-only agents (reviewers, planners): `Read, Glob, Grep`
- Writing agents (code, docs, tests): `Read, Glob, Grep, Edit, Write, Bash, Skill`
- Coordination agents (PM): `Read, Glob, Grep, Bash, Task`

Agent body should be short — the skill does the heavy lifting. Include only:
- Any cross-skill invocations (e.g., "if the task involves X, invoke the Y skill first")
- Log entry reminder if the skill requires it and the agent needs to enforce it

---

## Step 4 — Remind the User

After writing all files, remind the user:

```
Run `./link_to_main_claude.sh` from the repo root to symlink the new skill (and agent if created).
```

If a new agent was created, also remind them that Claude Code may need to be restarted to pick up the new agent.

---

## What NOT to Do

- Do not duplicate content between SKILL.md and reference files — SKILL.md points to references, references contain the detail
- Do not write overly long SKILL.md files — if body exceeds ~100 lines, split into reference files
- Do not invent rule files that don't exist — only reference files that actually exist in `rules/`
- Do not add logging instructions unless the skill type warrants it (action and planning skills do; reference and analysis skills usually don't)
- Do not write code in the skill file — skills are instructions, not implementations
