---
type: Comparison Analysis
title: Alignment with the Anthropic skill-creator Skill
description: How this repo's skill rulebook compares to Anthropic's official skill-creator — where they agree, what skill-creator covers more rigorously, and the one genuine tension.
tags: [skills, meta, comparison]
timestamp: 2026-07-31T00:00:00Z
---

# Alignment with the Anthropic `skill-creator` Skill

> **Load when:** you want the rigorous tooled evaluation workflow (parallel baselines, graders,
> benchmark aggregation, blind A/B), you're auditing this rulebook itself for gaps, or you hit the
> MUST/ALWAYS question. **Not needed to author a skill.** Companion to
> [claude-skills-best-practices.md](../claude-skills-best-practices.md) (the core rulebook).

This compares the rulebook against Anthropic's official `skill-creator` SKILL.md — the tool used to
build, evaluate, and improve skills from within Claude itself. It maps what aligns, what the
rulebook underemphasizes, and where the two sources are in genuine tension.

---

## Where the rulebook and skill-creator agree

The core structural guidance is consistent throughout:

- Three-level progressive disclosure (metadata → body → supporting files)
- Keep SKILL.md under 500 lines; move detail to referenced files
- Description is the primary triggering mechanism
- Bundle scripts for repeated work rather than having Claude regenerate them
- Explain the "why" behind instructions, not just the "what"
- Write → test → review → iterate as the fundamental development loop
- Progressive disclosure for reference files; one level deep from SKILL.md

---

## What skill-creator covers that the rulebook underemphasizes

**The evaluation loop is a tooled, measured process — not just a suggestion**

The rulebook says "build evaluations" across roughly one section (see
[evaluation.md](evaluation.md)). The skill-creator devotes most of its length to the mechanics of
doing this rigorously:

- Spawn **parallel** with-skill AND baseline subagents **in the same turn** (not sequentially — all runs start together so they finish around the same time)
- Capture `total_tokens` and `duration_ms` from each task notification — this data arrives once in the notification and is gone; process it immediately
- Grade assertions via `agents/grader.md` using exact field names (`text`, `passed`, `evidence`)
- Aggregate with `scripts/aggregate_benchmark <workspace>/iteration-N --skill-name <name>` to produce `benchmark.json` with pass rate, time, and token deltas
- Run an analyst pass (see `agents/analyzer.md`) to surface non-discriminating assertions, high-variance evals, and time/token tradeoffs
- Launch the visual reviewer: `python eval-viewer/generate_review.py <workspace>/iteration-N --benchmark benchmark.json`

The key implication: **token efficiency is a measured variable, not just a design goal.** You can see exactly how many tokens each run consumed and compare across iterations.

**Always run a baseline**

Every test run should have a companion:
- **New skill:** run without the skill at all (`without_skill/outputs/`)
- **Improving a skill:** run against the previous version (`old_skill/outputs/`)

Without a baseline, you cannot know whether your changes actually helped. Covered in
[evaluation.md](evaluation.md) ("No gap, no skill") for the new-skill case; the
improving-an-existing-skill baseline is still weaker here than in skill-creator.

**Read the transcripts, not just the final outputs**

skill-creator explicitly instructs: *read the transcripts from the test runs and notice if the skill is making the model waste time doing things that are unproductive. If all 3 test cases resulted in the subagent writing a `create_docx.py`, that's a signal the skill should bundle that script.*

Now covered in [evaluation.md](evaluation.md) ("Read execution traces, not just final outputs") — transcripts reveal latent waste that output quality scores completely miss.

**Beware of overfitting to your test cases**

skill-creator has an important caution the rulebook lacks:

> "We're trying to create skills that can be used a million times across many different prompts. Here you and the user are iterating on only a few examples. If the skill works only for those examples, it's useless."

Fiddly, over-specific changes that fix one failing test often make the skill more brittle across the real distribution of prompts. The corrective: try different metaphors, different patterns, or restructured workflows rather than adding narrow guardrails.

**Description optimization is an automated loop with scripts**

The rulebook mentions "optimize your description" generically. skill-creator specifies the actual mechanism:

```bash
python -m scripts.run_loop \
  --eval-set trigger-eval.json \
  --skill-path path/to/skill \
  --model claude-sonnet-4-6 \
  --max-iterations 5
```

This runs a 60/40 train/test split, evaluates each query **3 times** for a reliable trigger rate (not once), proposes improvements based on failures, and selects the best description on held-out test score — specifically to avoid overfitting to the training queries. The rulebook's description optimization guidance is much weaker than this.

**Blind comparison for rigorous A/B testing**

skill-creator includes an advanced evaluation mode (see `agents/comparator.md` and `agents/analyzer.md`) where two skill versions are shown to an independent agent without labeling which is which, then analyzed for *why* the winner won. This produces more objective quality judgments than self-evaluation. The rulebook doesn't mention this at all.

**Packaging for distribution**

skill-creator ends with `scripts/package_skill.py` producing a distributable `.skill` file. The rulebook has no equivalent — it treats skills as local configurations rather than artifacts to be shared or versioned.

**Cowork-specific mechanics**

skill-creator has a dedicated section for Cowork environments:
- No subagents → run test cases sequentially, skip baselines
- No display → use `--static <output_path>` for a standalone HTML viewer file instead of a live server
- "Submit All Reviews" downloads `feedback.json` rather than posting to a server
- Packaging still works via `package_skill.py`

The rulebook acknowledges Cowork briefly but doesn't document these mechanics.

---

## What the rulebook covers that skill-creator does not

These topics are out of scope for skill-creator (which focuses on the creation/eval workflow), but are real and useful:

- Complete frontmatter field reference (`paths`, `effort`, `model`, `hooks`, `context`, `agent`, `shell`, argument substitution with `$ARGUMENTS[N]` and `${CLAUDE_SKILL_DIR}`) — [frontmatter-reference.md](frontmatter-reference.md)
- Dynamic context injection (`` !`command` `` and `` ```! `` block syntax) — [frontmatter-reference.md](frontmatter-reference.md)
- Invocation control nuances: `disable-model-invocation` vs `user-invocable` and when each applies
- Domain-organized reference file pattern with per-domain loading
- Shared context factored across multiple skills and agents
- Anti-patterns section (Windows paths, deeply nested references, assuming packages installed, MCP tool name qualification)
- The seven-subdirectory layout standard and OKF rules for `references/` — [directory-structure.md](directory-structure.md)
- The entire community section: caveman compression, learnings.md self-improvement pattern, trigger rate research, superpowers framework, Skills vs. CLAUDE.md decision framework

---

## One genuine tension

skill-creator says: *"Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag."*

The community notes report the opposite experience: many developers find that explicit `MUST`/`ALWAYS` directives reliably improve compliance for behaviors that are otherwise inconsistent. Community trigger research even recommends `MANDATORY TRIGGERS` in all-caps as a description technique.

**The reconciliation:** skill-creator's advice targets the *body* of the skill — where over-directive language can make instructions brittle and hard to generalize. The community advice tends to target *descriptions* and *trigger phrases*, where more aggressive language genuinely helps Claude pick the right skill. The two recommendations apply to different parts of the file and are not actually contradictory once you separate them.

---

## Summary table

| Topic | This rulebook | skill-creator |
|---|---|---|
| Progressive disclosure | ✅ Complete | ✅ Complete |
| 500-line limit | ✅ | ✅ |
| Description as trigger | ✅ Complete | ✅ Complete |
| Bundle scripts | ✅ | ✅ |
| Explain the why | ✅ | ✅ |
| Eval loop mechanics (scripts, viewer, grader) | ⚠️ Surface level | ✅ Detailed |
| Baseline comparisons | ✅ evaluation.md ("no gap, no skill") | ✅ Required |
| Read transcripts, not just outputs | ✅ evaluation.md | ✅ |
| Overfitting / generalization warning | ❌ Missing | ✅ |
| Token/timing as measured metric | ❌ Conceptual only | ✅ Measured |
| Description optimization automation | ⚠️ Mentioned | ✅ Scripted loop |
| Blind A/B comparison | ❌ Missing | ✅ |
| Packaging (.skill files) | ❌ Missing | ✅ |
| Cowork-specific mechanics | ⚠️ Brief | ✅ Dedicated section |
| Frontmatter field reference | ✅ Complete | ⚠️ Partial |
| Dynamic context injection | ✅ | ❌ |
| Anti-patterns | ✅ Section | ⚠️ Scattered |
| Community insights | ✅ Full section | ❌ Out of scope |
| Skills vs. CLAUDE.md | ✅ Community | ❌ Out of scope |
