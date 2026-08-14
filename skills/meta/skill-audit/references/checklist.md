---
type: Checklist
title: Skill Audit Checklist
description: Category-by-category checklist for auditing a skill's description, token efficiency, progressive disclosure, and behavioral consistency.
tags: [skill, audit, checklist]
timestamp: 2026-07-15T00:00:00Z
---

# Skill Audit Checklist

Work through every category. Only flag genuine issues — a well-written section
needs no comment. Severity guide: 🔴 High = likely causing real problems right
now. 🟡 Medium = noticeable drag on quality or cost. 🟢 Low = minor improvement.

---

## 1. Description (highest impact — undertriggering is the #1 real-world problem)

Community research (650 trials) shows vague descriptions drop activation to ~20%.
Optimized descriptions with trigger phrases reach 50–90%. Every description issue
is at minimum 🟡.

**Check:**
- [ ] Written in third person? ("Processes PDFs" not "I can help you with PDFs")
- [ ] Key use case in the first ~50 characters? (Descriptions truncate at ~250 chars
      in the skill listing — front-load what matters most)
- [ ] Includes specific trigger phrases users would naturally say? Not just the task
      name, but how someone would actually ask for it casually
- [ ] Lists synonyms for the core action? e.g. "report, memo, summary, writeup,
      one-pager" rather than just "report"
- [ ] Has "even if they don't explicitly mention X" language for implicit requests?
- [ ] Specific enough to differentiate from similar skills?
- [ ] Pushy enough? Undertriggering is more common than overtriggering. If the
      description is polite and passive, it will be ignored.

**🔴 Flag if:** Description is one generic sentence with no trigger phrases.
**🔴 Flag if:** First person ("I can", "This skill helps you").
**🟡 Flag if:** No synonym list for the core noun (document types, action verbs).
**🟡 Flag if:** Doesn't include "MANDATORY TRIGGERS" or equivalent keyword block
              for skills competing with similar ones.

**Fix pattern:**
```yaml
# Before (bad):
description: Helps with PDF files and document processing.

# After (good):
description: >
  Extracts text and tables from PDFs, fills forms, merges and splits documents,
  adds watermarks, and handles OCR on scanned files. Use whenever the user
  mentions a .pdf file or asks to produce one. MANDATORY TRIGGERS: PDF, .pdf,
  form, extract, merge, split, rotate, watermark, OCR, scanned document.
```

---

## 2. Token efficiency (second highest impact)

The context window is a shared resource. Every token in SKILL.md competes with
conversation history. Challenge each paragraph: does Claude genuinely need this?

**Check:**
- [ ] Body under 500 lines?
- [ ] Explains things Claude already knows? (What a PDF is, how git works, what
      JSON means, how to install npm — skip all of it)
- [ ] Uses prose where a code snippet or table would be clearer AND shorter?
- [ ] Contains filler phrases? ("It's important to note that...", "Please be sure
      to...", "Make sure you always...", "You should...")
- [ ] Has redundant instructions that repeat the same point in different words?
- [ ] Contains motivational or explanatory preamble that adds no new information?
- [ ] Inline scripts or code that runs every invocation but should be a bundled
      script instead?
- [ ] Large blocks of boilerplate that belong in a template file?

**🔴 Flag if:** Body is over 500 lines with no supporting file structure.
**🔴 Flag if:** More than ~20 lines explaining concepts rather than directing action.
**🟡 Flag if:** Filler phrases ("it's important to", "please make sure", "always
              remember to") appear more than 2–3 times.
**🟡 Flag if:** The same instruction is stated twice in different sections.
**🟢 Flag if:** Minor wordiness that could tighten without changing meaning.

**Token waste patterns to look for:**
```markdown
# Waste:
PDF files are a common document format that store text and images in a
portable way. To read them you'll need a library like pdfplumber...

# Better (50 tokens → 10 tokens):
Use pdfplumber for text extraction:
  import pdfplumber
```

---

## 3. Progressive disclosure

SKILL.md should be a table of contents, not an encyclopedia. Details belong in
supporting files that Claude loads only when relevant.

**Check:**
- [ ] Is SKILL.md acting as the full manual rather than a navigation hub?
- [ ] Are there multiple distinct domains/modes that could each have their own
      reference file? (e.g., "creating" vs "editing" vs "reading" workflows)
- [ ] Are reference files linked from SKILL.md with clear "read when you need X"
      guidance?
- [ ] Are references nested deeper than one level? (SKILL.md → a.md → b.md is
      bad — Claude may partially read and miss b.md entirely)
- [ ] Do reference files over ~100 lines have a table of contents at the top?
- [ ] Are large code blocks or templates sitting inline that could be files?

**🔴 Flag if:** SKILL.md is 400+ lines with no supporting files.
**🟡 Flag if:** Clearly separable sub-workflows are all crammed into one file.
**🟡 Flag if:** References are nested (A references B which references C).
**🟢 Flag if:** A long reference file is missing a table of contents.

---

## 4. Frontmatter and control flags

Small omissions here cause real operational problems.

**Check:**
- [ ] `disable-model-invocation: true` missing for side-effect commands?
      (deploy, commit, send-message, delete, push — anything with consequences
      the user should explicitly trigger)
- [ ] Scripts using hardcoded absolute paths instead of `${CLAUDE_SKILL_DIR}`?
      (Hardcoded paths break when the skill moves or is installed by someone else)
- [ ] Windows-style backslash paths anywhere? (`scripts\helper.py` → `scripts/helper.py`)
- [ ] `allowed-tools` missing for skills that always need specific tools?
      (Saves per-use approval prompts during execution)
- [ ] `paths` field worth adding? (Skills that only apply to specific file types
      or directories can use this to avoid loading unnecessarily)

**🔴 Flag if:** Side-effect command (deploy, commit, delete) is missing
              `disable-model-invocation: true` — Claude may run it spontaneously.
**🟡 Flag if:** Scripts use hardcoded paths.
**🟢 Flag if:** `allowed-tools` would reduce friction but is missing.

---

## 5. Behavioral consistency

Skills that don't produce consistent output usually lack examples or structure.

**Check:**
- [ ] Skill produces structured/formatted output but has no output template?
- [ ] Skill's quality depends heavily on style/tone but has no input→output examples?
      (2–5 examples are the most reliable way to convey desired style)
- [ ] Multi-step workflow with no checklist for Claude to track progress?
      (Checklists prevent step-skipping in complex flows)
- [ ] Operations that could fail silently with no validation step?
- [ ] Instructions use heavy-handed MUST/ALWAYS/NEVER without explaining why?
      (Reason-driven instructions generalize better than directives)
- [ ] Time-sensitive information? ("Before August 2025, use..." will become wrong)

**🟡 Flag if:** Structured output with no template — Claude will invent its own
              format and it will vary across invocations.
**🟡 Flag if:** Multi-step process with 4+ steps and no progress checklist.
**🟢 Flag if:** MUST/ALWAYS used where a rationale would be more robust.
**🟢 Flag if:** Dates or version-specific info not wrapped in a "legacy" section.

---

## 6. Community patterns (field experience)

These aren't in the official docs but come from real usage at scale.

**Check:**
- [ ] Would this skill genuinely benefit from a `.learnings/` directory?
      Only suggest it for skills where: failure modes aren't fully known upfront,
      the skill interacts with external systems/APIs, or behavior varies across runs
      in ways worth capturing. Do NOT suggest it for simple, deterministic skills
      (e.g. a skill that always runs the same command or formats text).
- [ ] Description would benefit from a MANDATORY TRIGGERS block?
      Community research shows this is the single highest-ROI description change.
- [ ] Skill invokes another model/tool in a complex way but doesn't specify which
      MCP tools to use by fully qualified name? (`BigQuery:bigquery_schema` not
      `bigquery_schema` — unqualified names fail when multiple MCPs are present)
- [ ] Skill is monolithic when it should be split?
      One granular skill per domain outperforms one large multi-domain skill.
      Trigger rates and description specificity both improve with granularity.

**🟢 Flag if:** Skill clearly benefits from learnings capture (external APIs, variable failure modes, repeated runs with non-obvious behavior). Skip for simple/deterministic skills.
**🟡 Flag if:** MCP tools referenced without server prefix.
**🟢 Flag if:** Skill covers multiple distinct domains and could be profitably split.

---

## 7. OKF conformance (references/ and sources/)

Reference files follow the Open Knowledge Format — spec vendored at
`~/.claude/skills/shared/okf-spec.md`, summary in
`~/.claude/skills/shared/skill-authoring/directory-structure.md`. Applies only
under `references/` (and `sources/` indexes); SKILL.md and agent frontmatter are
exempt (the harness owns those fields).

**Check:**
- [ ] Does every `references/*.md` (except `index.md`/`log.md`) open with YAML
      frontmatter carrying a non-empty `type`?
- [ ] Do concepts have `title` and a one-sentence `description`? (The description
      feeds index entries verbatim — flag multi-sentence or missing ones.)
- [ ] Does every directory with 4+ uncovered concept files have an `index.md`?
      (Uncovered = own files plus, recursively, files of subdirectories lacking
      their own index — an indexed subdirectory contributes zero. Run
      `python3 <repo>/scripts/okf_lint.py` rather than counting by hand.)
- [ ] Are index files clean: no frontmatter, only headings +
      `* [Title](relative-path) - description` bullets, subdirectories under
      `# Subdirectories` linking to `subdir/index.md`?
- [ ] Do index entry descriptions match the linked files' frontmatter descriptions?
- [ ] Is `log.md` (if present) newest-first with `## YYYY-MM-DD` headings?
- [ ] Are cross-links file-relative (not absolute filesystem paths)?
- [ ] Legacy artifacts: an uppercase `INDEX.md`, or index files carrying content
      instead of pointers?

**🔴 Flag if:** Reference files have no frontmatter at all, or an `INDEX.md`/index
              exists in a non-OKF format.
**🟡 Flag if:** Frontmatter exists but `type` is missing/empty, or a directory
              over the 4-uncovered-file threshold has no `index.md`.
**🟢 Flag if:** Descriptions are missing/multi-sentence, or index entries have
              drifted from frontmatter descriptions.

---

## Severity calibration

Before presenting the report, check:
- Are you flagging 3–8 things? Good.
- Flagging 12+? Raise your thresholds — not every imperfection is worth noting.
- Flagging 1–2? You may have missed something, or the skill is genuinely solid.
- Are all your findings actionable? Each one should have a specific proposed fix,
  not just an observation.
