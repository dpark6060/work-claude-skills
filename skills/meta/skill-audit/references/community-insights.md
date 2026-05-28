# Community Insights: Real-World Skill Patterns

> Supplementary context for the skill-creator skill. Load this file when helping a user
> build, optimize, or debug a skill — especially for questions about token efficiency,
> trigger rates, or patterns discovered through real-world usage.
>
> Sources: GitHub repositories, developer experiments, and community research (April 2026).

---

## Contents
- [The biggest real-world problem: undertriggering](#undertriggering)
- [Output token compression: the caveman technique](#caveman)
- [The learnings.md self-improvement pattern](#learnings)
- [Skills vs. CLAUDE.md: the core decision](#skills-vs-claudemd)
- [Token efficiency: the expert rules](#token-efficiency)
- [Community framework patterns (superpowers)](#superpowers)
- [The MUST/ALWAYS tension](#musts)
- [Quick reference: community rules of thumb](#quick-reference)

---

## Undertriggering: The Biggest Real-World Problem {#undertriggering}

Community researcher Ivan Seleznov ran 650 trials measuring skill activation rates:

| Description quality | Activation rate |
|---|---|
| Default / vague | ~20% |
| Optimized | ~50% |
| Optimized + examples in description | ~72–90% |

**Root cause:** Claude loads *only* the frontmatter of all available skills before deciding
what to do. Only after selecting a skill does it load the full body. A perfect body with a
poor description = skill never fires.

### What actually improves trigger rates

**Use exact phrases users would say:**
`"Use when the user says 'review this PR' or asks to check their code before merging"`
outperforms `"Useful for code review"`.

**List synonyms explicitly:**
`"report, memo, document, writeup, one-pager, summary"` rather than just `"report"`.

**Add the implicit-trigger phrase:**
`"even if they don't explicitly mention [X]"` captures indirect requests.

**MANDATORY TRIGGERS block** — a community convention with measurably higher activation:

```yaml
description: >
  Analyze Excel spreadsheets, create pivot tables, generate charts.
  MANDATORY TRIGGERS: Excel, spreadsheet, .xlsx, data table, budget,
  financial model, chart, graph, tabular data, xls
```

**Front-load the 250-char essentials.** Descriptions are truncated at ~250 chars in the
skill listing, but keywords beyond that point still influence triggering. Put the single
most important trigger phrase in the first 50 characters.

---

## Output Token Compression: The Caveman Technique {#caveman}

The [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) skill (562+ stars)
cuts output tokens by ~61% on average by stripping linguistic fluff while preserving all
technical content.

**Drop:** articles (a/an/the), filler words (just/really/basically/actually/simply),
pleasantries (sure/certainly/of course/happy to), hedging language.

**Keep:** all technical content, code, commands, exact values.

**Benchmarked reductions (verified with tiktoken):**
- Web search responses: 68%
- Code edits: 50%
- Q&A exchanges: 72%
- Average: **~61%**

**Critical safeguards:** Auto-clarity mode suspends caveman style for security warnings,
irreversible actions, and multi-step sequences where fragmentation risks misunderstanding.
Code, commits, and PRs always use normal writing.

**Minimal SKILL.md for caveman:**
```
Respond like smart caveman. Drop: articles (a/an/the), filler (just/really/basically/
actually/simply), pleasantries (sure/certainly/happy to), hedging.
Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for").
Pattern: [thing] [action] [reason]. [next step].

Auto-clarity: suspend for security warnings, irreversible actions, multi-step sequences
where fragmentation risks misunderstanding. Code/commits/PRs: write normal.
```

**Meta-lesson:** The most token-efficient skills are often the *shortest* ones, because
they rely on Claude's existing intelligence rather than trying to replicate it. If a skill
is growing long, ask: is each section earning its token cost, or am I explaining things
Claude already knows?

---

## The learnings.md Self-Improvement Pattern {#learnings}

A widely-adopted community pattern: bundle a `.learnings/` directory with any skill that
runs repeatedly. The skill captures what worked and what didn't, improving automatically
over time without manual maintenance.

**Structure to add to the skill directory:**
```
my-skill/
├── SKILL.md
└── .learnings/
    ├── LEARNINGS.md         ← what worked, key observations
    ├── ERRORS.md            ← failures and how they were fixed
    └── FEATURE_REQUESTS.md  ← identified gaps
```

**Entry format for LEARNINGS.md:**
```markdown
## [2026-03-14] | Priority: HIGH | Status: RESOLVED
**Area:** form-filling
**Summary:** pdfplumber fails on scanned PDFs
**Details:** OCR step required before text extraction
**Suggested action:** Added scanned-PDF detection before extraction step
```

**Critical implementation note:** Have Claude *summarize* the learnings file at the start
of each task, not just read it. Summarizing forces Claude to process and internalize the
content rather than skim past it. Add this to the skill body:

```markdown
## Before starting
Read and summarize .learnings/LEARNINGS.md and .learnings/ERRORS.md.
Summarizing (not just reading) forces you to internalize what has and hasn't
worked in previous runs of this skill.
```

**Write-back is equally important.** A skill that only reads learnings but never writes them
requires manual maintenance and defeats the purpose. Always add an "After finishing" section
alongside the "Before starting" section:

```markdown
## After finishing
If this session produced anything worth capturing, append to the relevant file:
- **.learnings/LEARNINGS.md** — a pattern that worked well, a non-obvious behavior, or a
  workflow adjustment that improved the result.
- **.learnings/ERRORS.md** — a failure, an error, or a wrong assumption and how it was fixed.

Don't write an entry if nothing went wrong and nothing surprising happened. Use the entry
format at the top of each file.
```

The "if worth it" gate matters — without it Claude writes boilerplate entries on every run
and the files become noise.

**Lifecycle:** As learnings accumulate, the most important ones get "promoted" into the
main SKILL.md body. The learnings file continues accumulating new observations each session.

**When to suggest:** Only when there's a genuine reason to accumulate knowledge over time —
external API integrations, data-processing skills with variable inputs, or workflows where
failure modes aren't fully known upfront. Do NOT suggest it for simple or deterministic
skills (text formatters, static command runners, single-purpose scripts). Adding learnings
files to a skill that doesn't need them just creates noise.

---

## Skills vs. CLAUDE.md: The Core Decision {#skills-vs-claudemd}

The most frequently debated topic in the community. The consensus:

| Put it here | When |
|---|---|
| `CLAUDE.md` | Universal rules needed in every session — project conventions, architecture, always-on coding style |
| Skill | Specialized workflow you need occasionally — deployment, PR reviews, document creation |

**The "repeat prompt" test:** If a user has typed the same prompt into Claude more than
~3 times across different conversations, it should be a skill.

**Why skills win on token cost:** CLAUDE.md loads into every conversation whether or not
it's relevant. Skills load on demand. For anything domain-specific or used less than daily,
a skill is strictly more efficient.

**The CLAUDE.md + skills hybrid** (widely used in production setups):
- CLAUDE.md contains only project context (architecture, key files, conventions)
- All behavioral instructions (how to commit, how to review, how to test) live in skills
- Keeps CLAUDE.md small and context-pressure low

---

## Token Efficiency: The Expert Rules {#token-efficiency}

From the community token-efficiency skill (90–95% cost reduction claimed):

> "Reading files costs tokens. Bash commands don't."

**Decision framework for file operations:**

| Situation | Approach | Token cost |
|---|---|---|
| Create new file | Write directly | Low |
| Short output (<100 lines) | Claude context | Low |
| Modify code | Read + Edit | Medium |
| Modify large data | Bash (sed, awk, cp) | Negligible |

**Always filter before reading:**
- `grep -n "error" logfile.txt` not reading the whole log
- `head -100 bigfile.py` not the full file
- `git status --short` not `git status`
- Check `package.json` or `requirements.txt` before reading large config files

**Two-model strategy (~50% cost reduction on analysis-heavy projects):**
- Use Opus once at project start for architecture/codebase comprehension
- Use Sonnet for all implementation, debugging, and routine tasks

---

## Community Framework Patterns: obra/superpowers {#superpowers}

The [obra/superpowers](https://github.com/obra/superpowers) framework (143k stars) is
worth knowing when helping users design dev-workflow skills. Key patterns that have
influenced the broader community:

**Mandatory pipeline stages:** brainstorm → workspace isolation → planning → execution →
testing → review → completion. Enforcing a planning stage before coding prevents the
"skip straight to implementation" anti-pattern that causes rework.

**Subagent-driven execution:** Fresh specialized agents per task rather than one long
conversation. Avoids context pollution; each agent has only the context it needs.

**Task granularity standard:** 2–5 minute units with exact file paths and complete code
snippets. Vague tasks produce inconsistent results; granular tasks produce reliable ones.

**When to surface these patterns:** When a user is building skills for software development
workflows, code review, CI/CD, or anything involving multi-step execution pipelines.

---

## The MUST/ALWAYS Tension {#musts}

The skill-creator SKILL.md flags `ALWAYS`/`NEVER` in all-caps as a yellow flag and
recommends explaining the *why* instead. The community frequently uses these directives
and reports they work. Both are right — they apply to different parts of the file:

**In the skill body (instructions):** skill-creator is correct. Heavy-handed directives
make instructions brittle. When Claude hits an edge case the directive didn't anticipate,
it over-applies or ignores it. Explaining the why produces more robust behavior.

**In descriptions and trigger phrases:** The community is correct. `MANDATORY TRIGGERS`
in all-caps in the description genuinely improves activation rates. This operates at the
skill-selection stage, before the body is even read — different signal, different context.

**Practical rule:** Reason-driven instructions in the body. ALLCAPS reserved for
trigger keywords and descriptions where you need to force activation.

---

## Quick Reference: Community Rules of Thumb {#quick-reference}

- "If you've typed the same prompt 3 times, make it a skill"
- "The best skills are often the shortest ones — trust Claude's intelligence"
- "Skills are portable; prompts are one-time; CLAUDE.md is always-on"
- "Test with Haiku first — if it works there, it's well-written"
- "Use `${CLAUDE_SKILL_DIR}` for all script paths, never hardcoded paths"
- "Version skills with git tags — rollback is sometimes needed"
- "Never install a skill from an untrusted source without reading every file"
- "Summarize your learnings file; don't just read it"
- "Descriptions truncate at ~250 chars in listing — front-load what matters"
- "Granular domain-specific skills beat one monolithic skill"
- "Baselines matter: always compare with-skill vs without-skill, not just output quality"
