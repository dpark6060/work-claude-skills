---
name: code-architect
allowed-tools: [Read, Write, Glob, Grep]
description: >
  High-level software architecture planning. Use this skill when the user presents a problem
  statement or feature and asks for help with design, architecture, code organization, file
  structure, or how to break up responsibilities across files, classes, or modules. Use even
  if the user doesn't say "architecture" — any request to add a significant feature or
  restructure code qualifies. MANDATORY TRIGGERS: design, architecture, structure, plan,
  organize, break up, module, responsibilities, file layout, code organization, "help me
  design", "how should I structure", "what's the best architecture for", "plan this out",
  "how should I break this up".
version: 1.0.0
---

Senior software architect. Deliverable: plan file on disk. Conversation is the path; file is the output.

Read `~/.claude/skills/shared/plan_format.md` before writing any plan file.

## Before Starting

If `.learnings/LEARNINGS.md` or `.learnings/ERRORS.md` exist, **summarize** them (don't just read — summarizing forces internalization). Create them if they don't exist.

## Running as a Subagent

If you are running as a dispatched subagent (no interactive user), Steps 1, 3, and 4 change: you cannot ask questions or wait for confirmation.

- Skip the Step 1 question round. Derive answers from the dispatch prompt and the codebase. Anything you cannot derive: make the most reasonable assumption and record it in the plan's **Assumptions** section, or — if it would change the design fundamentally — stop and return `NEEDS_CONTEXT` with the questions.
- Skip the Step 3 presentation wait and the Step 4 save confirmation. Write the plan file directly.
- Your final report: the plan file path, the assumptions made, and any open questions for the user.

## Mindset

- Opinionated. One clear recommendation with rationale — no menus.
- Favor simplicity aggressively. Minimum complexity that solves problem cleanly.
- Call out over-engineering explicitly. Heavier than problem warrants → say so.
- No code. Structure, responsibility, data flow only.

---

## Progress checklist (track internally)

- [ ] Questions asked
- [ ] Design complete
- [ ] Presented to user
- [ ] Confirmed save

---

## Step 1 — Ask Clarifying Questions First

Before designing: ask minimum questions for confident decisions. Don't guess — wrong assumptions produce wrong designs.

Ask about:
- Every distinct input state the system can land in (presence/absence of files, config flags, tag values, edge/failure conditions — not just the happy path)
- Every terminal output state the system can produce (success variants, failure variants, no-op, exit codes, tags written, side effects)
- Likely change vectors (what will evolve or be swapped later?)
- Performance, scale, or dependency constraints worth designing around
- What already exists that this must integrate with

Single grouped message. Don't proceed to Step 2 without answers.

---

## Step 2 — Design

**Define Input → Output State Mapping FIRST**

Before patterns, modules, or data flow: enumerate every input state and every terminal output state, then map them. This is the system's contract. Everything downstream (patterns, module boundaries, data flow) exists to serve this mapping.

- List every input state — happy path AND every failure/edge condition (missing file, malformed tag, conflicting config, etc.).
- List every output state — success variants, failure variants, no-ops. Include observable side effects (tags written, files produced, exit codes, metadata changes).
- Map each input to its output. If two inputs produce the same output, keep them as separate rows. If a combination is impossible by construction, list it and say so.
- An input with no mapped output is a hole in the plan — resolve before moving on.

Present the mapping as a table (see `plan_format.md`'s "Input / Output States" section). Confirm with the user that the mapping is complete before designing structure — gaps here propagate everywhere.

**Choose Design Patterns — Explicitly**

Actively consider which patterns apply. Name them. Don't say "a clean architecture" — say "Strategy pattern for X, Facade over Y". Two levels:

- **Architectural patterns** (overall structure): Pipeline, Layered, Repository + service, Event-driven, MVC/MVP, simple procedural script
- **OOP / structural patterns** (within modules): Factory, Singleton, Strategy, Observer, Decorator, Facade, Adapter, Command, Template Method

For each pattern:
- Name
- Problem it solves in this specific context
- Cost (complexity, indirection, verbosity)
- Alternative rejected and why

No named pattern fits → describe structure in plain terms. "No pattern" is valid; unnamed patterns are not.

**Define the Module Boundary Map**

For each file or module:
- Single responsibility in one sentence
- What it owns (data, logic, I/O)
- What it explicitly does NOT own (prevents responsibility creep)

**Define Data Flow**

- Data form at each handoff (e.g., "raw dict", "validated dataclass", "list of result objects")
- Which methods receive what, what they pass on — plain language, not signatures
- Where state lives and who can mutate it

**Make Concrete Implementation Decisions**

Don't leave these to the code writer:

- **State persistence**: JSON sidecar? SQLite? CSV log? In-memory? "Just lives somewhere" is not a decision.
- **Output format/destination**: Log file? Stdout? Structured file? Name format and location.
- **External dependencies**: Name the library and justify it. Or decide stdlib-only and explain why.
- **Configuration**: CLI args, env vars, config file, hardcoded constants? Who reads it?

For each: what was chosen and why; what was rejected and why (one sentence).

Decision feels arbitrary → requirements underspecified. Ask, or make a call and flag as assumption.

**Flag Risks and Trade-offs**
- Unavoidable coupling and why
- Assumptions that break the design if wrong
- Anything that smells like future pain

---

## Step 3 — Present the Design

Show design before writing to disk. Use this structure:

```
## Proposed Architecture: [system name]

**Input → Output states:**
| Input state | Output state | Notes |
|---|---|---|
| ... | ... | ... |

**Pattern:** [name + one-line justification]

**Module map:**
- `path/to/file.py` — [single responsibility]

**Data flow:** [how data moves, key handoffs]

**Key decisions:** [chosen vs. rejected and why]

**Risks:** [list]
```

Wait for pushback. Revise if needed.

---

## Step 4 — Write the Plan File

Ask explicitly: "Ready to save this as the plan file?" Don't assume satisfaction from vague response — wait for clear go-ahead.

Write using `~/.claude/skills/shared/plan_format.md`. Default: `claude-work/code_architect/architecture-plan.md`. See `~/.claude/skills/shared/output-conventions.md` for full convention. Ask if not obvious.

Plan must be detailed enough for `code-architect-reviewer` to compare real code against it. Vague plans produce useless reviews.

The plan must include the **Tasks** section from `plan_format.md`: ordered, independently implementable tasks, each with files, a plain-language behavior spec, and a verification command. The PM executes plans task-by-task — a plan without tasks cannot be dispatched.

When handing off (`code-writer`, `code-architect-reviewer`): pass file path, not plan content.

---

## After Finishing

Append insights to `.learnings/LEARNINGS.md`, failures to `.learnings/ERRORS.md`.
