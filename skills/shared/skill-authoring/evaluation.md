---
type: Process Guide
title: Skill Sourcing, Evaluation & Iteration
description: Where skill content should come from, and how to test and iterate on a skill once it exists — baselines, trace reading, eval sets, and description optimization.
tags: [skills, evaluation, iteration]
timestamp: 2026-07-31T00:00:00Z
---

# Skill Sourcing, Evaluation & Iteration

> **Load when:** deciding whether a skill is worth writing, grounding its content in real material,
> or testing and iterating on a skill that already exists. Companion to
> [claude-skills-best-practices.md](../claude-skills-best-practices.md) (the core rulebook).

## Start from real expertise, not the model's general knowledge

The most common way skills fail is being generated from a prompt alone. Ask a model to write a
skill with no domain context and you get vague procedures — "handle errors appropriately", "follow
authentication best practices" — instead of the specific API quirks, edge cases, and project
conventions that make a skill worth loading. **If the model could have written the content without
your input, the skill is not adding anything.**

Two ways to ground it:

**Extract from a hands-on task.** Do the real task in conversation first, steering as you go. Then
extract the reusable pattern. Harvest specifically:
- the sequence of steps that actually worked
- every correction you made ("use X not Y", "check for edge case Z") → these become gotchas
- the input and output formats you saw
- project-specific facts you had to supply because the model didn't know them

**Synthesize from existing artifacts.** Feed real project material in, not a generic article. A
data-pipeline skill built from your team's incident reports and runbooks captures *your* schemas
and failure modes; one built from "data engineering best practices" captures nothing. Good sources:
internal runbooks and style guides, API specs and schemas, code review comments and issue trackers
(recurring reviewer concerns), git history — especially patches and fixes, since what changed
reveals what people get wrong — and real failure cases with their resolutions.

## No gap, no skill

Run the task without the skill first. If the model already handles it well, don't write the skill —
you'd be spending permanent description tokens plus a body load to buy nothing. The baseline run is
what tells you this, which is why it comes before authoring, not after.

## Read execution traces, not just final outputs

Grade the outputs, but read the transcripts too. Output scores miss latent waste that traces make
obvious:

| What you see in the trace | What it means |
|---|---|
| Agent tries several approaches before one works | Instructions too vague |
| Agent follows a step that doesn't apply to this task | Skill is over-comprehensive (core rulebook §4) |
| Agent stalls choosing between options | No clear default (core rulebook §8, anti-patterns) |
| Every test case independently writes the same helper script | Bundle it in `scripts/` (core rulebook §7) |

## Evaluation-driven development

Build evaluations *before* writing extensive documentation. This ensures the skill solves real problems.

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate library",
    "Extracts text from all pages without missing any",
    "Saves extracted text to output.txt in a readable format"
  ]
}
```

Process:
1. Run Claude on representative tasks *without* the skill → document failures
2. Create 2–3 evaluations targeting the gaps
3. Write minimal instructions to address gaps
4. Execute evaluations, compare against baseline
5. Iterate

## The Claude A / Claude B development loop

The most effective method uses two Claude instances:

- **Claude A** (your conversation) — refines the skill with you, has full context
- **Claude B** (fresh instance with skill loaded) — tests it on real tasks

Observe where Claude B struggles:
- Unexpected exploration paths (structure isn't intuitive)
- Missed file connections (links need to be more explicit)
- Overreliance on one section (that content should be in SKILL.md)
- Ignored content (unnecessary or poorly signaled)

Bring observations back to Claude A: *"When I asked Claude B for a regional sales report, it forgot to filter out test accounts. The skill mentions it, but maybe it's not prominent enough?"*

## Description optimization

After the skill content is stable, run the description through an optimization loop with trigger evals:

```json
[
  {"query": "ok so my boss sent me this xlsx file...", "should_trigger": true},
  {"query": "can you write a python script to parse csv?", "should_trigger": false}
]
```

Test with queries realistic enough that Claude would genuinely benefit from the skill (simple, one-step queries won't trigger skills regardless of description quality).

For the rigorous, tooled version of this loop — parallel baseline subagents, graders, aggregated
benchmarks, blind A/B comparison — see
[skill-creator-alignment.md](skill-creator-alignment.md).
