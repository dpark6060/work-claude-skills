---
type: Reference
title: "Architect Mode: design"
description: "Single-plan architecture for a new feature or system: input-to-output state mapping first, patterns only where they earn their place, module boundaries, data flow, concrete decisions, all with reasoning."
---

# Mode: design

Decide the architecture of a new feature or system, at full depth, in one plan file.

## Questions

Before designing, ask the minimum questions for confident decisions:

- Every distinct input state the system can land in (presence/absence of files, config flags,
  tag values, edge/failure conditions — not just the happy path)
- Every terminal output state the system can produce (success variants, failure variants, no-op,
  exit codes, tags written, side effects)
- Likely change vectors (what will evolve or be swapped later?)
- Performance, scale, or dependency constraints worth designing around
- What already exists that this must integrate with

## Define the Input → Output state mapping FIRST

Before patterns, modules, or data flow: enumerate every input state and every terminal output
state, then map them. This is the system's contract. Everything downstream exists to serve it.

- List every input state — happy path AND every failure/edge condition (missing file, malformed
  tag, conflicting config, etc.).
- List every output state — success variants, failure variants, no-ops. Include observable side
  effects (tags written, files produced, exit codes, metadata changes).
- Map each input to its output. If two inputs produce the same output, keep them as separate
  rows. If a combination is impossible by construction, list it and say so.
- An input with no mapped output is a hole in the plan — resolve it before moving on.

Present the mapping as a table ([plan-template.md](plan-template.md)'s "Input / Output States" section). With a user
present, confirm the mapping is complete before designing structure — gaps here propagate
everywhere.

## Choose design patterns for key or complex features

Use a named pattern when the feature has a variation point (several interchangeable
implementations now or in the requirements), crosses a module or external-system boundary, or
has a fixed skeleton with swappable steps. Anything smaller — roughly a single module and 2-3
methods with no variation point — is plain functions with no pattern named. Don't add a pattern
for a variation the requirements don't name.

- **Architectural patterns** (overall structure): Pipeline, Layered, Repository + service,
  Event-driven, MVC/MVP, simple procedural script
- **OOP / structural patterns** (within modules): Factory, Singleton, Strategy, Observer,
  Decorator, Facade, Adapter, Command, Template Method

For each pattern used: its name, the problem it solves in this context, its cost (complexity,
indirection, verbosity), and the close contender rejected and why.

## Decompose the workflow

State how many main parts the workflow has, what each does, and why it splits there: what each
split buys (an independent test seam, a swap point, a boundary around an external system) and
why it isn't fewer or more parts.

## Define the module boundary map

For each file or module:

- Single responsibility in one sentence
- What it owns (data, logic, I/O)
- What it explicitly does NOT own (prevents responsibility creep)
- Why the boundary sits there

## Define the data flow

- Data form at each handoff (e.g. "raw dict", "validated dataclass", "list of result objects")
- Which methods receive what, and what they pass on — plain language, not signatures
- Where state lives and who can mutate it

## Make concrete implementation decisions

Don't leave these to the code writer:

- **State persistence**: JSON sidecar? SQLite? CSV log? In-memory? "Just lives somewhere" is not
  a decision.
- **Output format/destination**: log file? stdout? structured file? Name the format and location.
- **External dependencies**: name the library and justify it, or decide stdlib-only and explain
  why.
- **Configuration**: CLI args, env vars, config file, hardcoded constants? Who reads it?

For each: what was chosen and why; what was rejected and why. A decision that feels arbitrary
means the requirements are underspecified — ask, or make a call and flag it as an assumption.

## Flag risks and trade-offs

- Unavoidable coupling and why
- Assumptions that break the design if wrong
- Anything that smells like future pain

## Present

```
## Proposed Architecture: [system name]

**Input → Output states:**
| Input state | Output state | Notes |
|---|---|---|
| ... | ... | ... |

**Pattern:** [name, why it fits this problem, contender rejected and why — or "plain functions"]

**Workflow:** [N main parts, what each does, why it splits there]

**Module map:**
- `path/to/file.py` — [single responsibility]

**Data flow:** [how data moves, key handoffs]

**Key decisions:** [chosen vs. rejected and why]

**Risks:** [list]
```
