---
name: skill-audit
description: >
  Audits an existing Claude skill against best practices for token efficiency,
  description quality, progressive disclosure, and behavioral consistency.
  Produces a prioritized findings report with specific line-level fixes, then
  implements approved changes. MANDATORY TRIGGERS: "audit skill", "audit my
  skill", "review skill", "improve skill", "check skill", "optimize skill",
  "skill not triggering", "skill too long", "skill too verbose", "skill token
  usage", "skill best practices", "clean up skill", "refactor skill", "skill
  quality". Also use when user points at a SKILL.md file and asks what's wrong.
---

# Skill Audit

Review an existing skill, identify problems, and implement approved fixes.
The goal is maximum effectiveness at minimum token cost.

## Invoke

```
/skill-audit /Users/davidparker/Documents/Flywheel/Claude/skills/category/skill-name
```

Or: "audit my deploy skill" — find the path yourself if not provided.

## Step 1: Read the skill

Resolve the path from `$ARGUMENTS`. If it's a symlink, follow it to the real
location — that's where changes should be written (per the user's setup, edit
in `Documents/Flywheel/Claude/skills`, not in `~/.claude/skills`).

Read `SKILL.md` in full. Then list all other files in the directory and read
any supporting files (references/, scripts/, assets/) to understand the full
picture. Note file sizes and line counts — they matter for the audit.

If the target path is read-only, copy the skill to `/tmp/skill-audit-work/`
before making any edits, and note that the user will need to copy it back.

Also load `~/.claude/references/community-insights.md` if it exists — it
contains field-tested patterns that supplement the checklist below.

## Step 2: Audit

Work through every category in `references/checklist.md`. For each finding,
note the exact location (line number or section name), what's wrong, and the
specific fix. Don't flag things that are fine.

Think about the skill as a whole, not just line by line:
- Is the description going to trigger reliably in practice?
- Does each paragraph in the body earn its token cost?
- Would a fresh Claude instance follow these instructions correctly?
- Is there repeated work that should be a bundled script?

## Step 3: Present the report

Use this exact format:

---
## Audit: [skill name]

**Summary:** [1-2 sentences on overall health and the most important thing to fix]

| # | Sev | Category | Location | Finding | Proposed Fix |
|---|-----|----------|----------|---------|--------------|
| 1 | 🔴 | Description | frontmatter | [what's wrong] | [exact fix] |
| 2 | 🟡 | Tokens | Lines 14–22 | [what's wrong] | [exact fix] |
...

**Proposed changes ready to implement:** [N fixes]
Which would you like to apply? (reply with numbers, ranges like 1-4, "all", or "none")
---

Keep findings specific enough to act on. "Description is vague" is not useful.
"Description doesn't mention any trigger phrases a user would naturally say —
replace with: [proposed text]" is useful.

## Step 4: Implement approved changes

After the user replies, apply exactly the approved fixes — no more, no less.
Show a brief before/after diff for any non-trivial change.

When done, offer to run description optimization if any description changes
were made:
> "Want me to run the trigger-rate optimizer on the updated description?
> It runs ~20 test queries and adjusts the wording to improve how reliably
> Claude activates this skill."

## A few principles to keep in mind

**Trust Claude's intelligence.** Only add context that Claude genuinely doesn't
have. If a section explains what a concept is rather than what to *do*, it's
probably not earning its tokens.

**Specific beats vague.** A finding that includes the exact proposed replacement
text is ten times more useful than one that says "consider simplifying."

**Don't over-flag.** A well-written concise section doesn't need a note. The
report should feel like signal, not noise. Aim for 3–8 findings on a typical
skill — if you're finding 15+ issues, reconsider your severity thresholds.

**Fixes should generalize.** When proposing rewrites, make them work across
the real distribution of prompts the skill will see — not just the specific
phrasing in the test cases.
