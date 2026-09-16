---
type: Best Practices Guide
title: Claude Skills Best Practices
description: Canonical rulebook for authoring skills — token efficiency, lean SKILL.md, progressive disclosure, and consistent behavior.
tags: [skills, best-practices, tokens]
timestamp: 2026-07-31T00:00:00Z
---

# Claude Skills Best Practices
### Minimizing Token Usage & Creating Consistent Behavior

> **Sources:** Anthropic official documentation ([code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), [platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)), the Agent Skills open standard ([agentskills.io/skill-creation/best-practices](https://agentskills.io/skill-creation/best-practices), [agentskills.io/specification](https://agentskills.io/specification)), internal skill-creator SKILL.md, and real-world skill examples.

---

## Table of Contents

1. [What Skills Are](#1-what-skills-are)
2. [Anatomy of a Skill](#2-anatomy-of-a-skill)
3. [Token Efficiency: The Core Model](#3-token-efficiency-the-core-model)
4. [Writing a Lean SKILL.md](#4-writing-a-lean-skillmd)
5. [Progressive Disclosure Patterns](#5-progressive-disclosure-patterns)
6. [Descriptions: The Triggering Mechanism](#6-descriptions-the-triggering-mechanism)
7. [Bundled Scripts: Token-Free Execution](#7-bundled-scripts-token-free-execution)
8. [Anti-Patterns to Avoid](#8-anti-patterns-to-avoid)
9. [Quick Checklist](#9-quick-checklist)

## Companion files

This file covers what you read *while writing* a SKILL.md. The rest lives in
[`skill-authoring/`](skill-authoring/index.md) — load by need, not by default:

| Load this | When |
|---|---|
| [directory-structure.md](skill-authoring/directory-structure.md) | Scaffolding a skill, or deciding which subdirectory a file belongs in |
| [frontmatter-reference.md](skill-authoring/frontmatter-reference.md) | Writing frontmatter, control flags, `paths`, arg substitution, `` !`command` `` injection |
| [behavior-patterns.md](skill-authoring/behavior-patterns.md) | Output must be consistent run to run: templates, few-shot, gotchas, checklists, validation loops. Also has complete example skills |
| [evaluation.md](skill-authoring/evaluation.md) | Before authoring (is there a real gap? where does the content come from?) and after (testing, iteration) |
| [community-insights.md](community-insights.md) | Trigger-rate research, caveman compression, `.learnings/` pattern, Skills vs. CLAUDE.md |
| [skill-creator-alignment.md](skill-authoring/skill-creator-alignment.md) | You want the rigorous tooled eval workflow, or you're auditing this rulebook |

---

## 1. What Skills Are

A **skill** is a directory containing a `SKILL.md` file that gives Claude a detailed playbook for a specialized task. Claude discovers available skills from their metadata and loads the full instructions only when relevant. Skills support slash-command invocation (`/skill-name`) and automatic model-triggered invocation.

```
~/.claude/skills/my-skill/
├── SKILL.md              ← Required entrypoint; the only file in the base dir
├── references/           ← Loaded on demand
│   ├── <topic>.md
│   └── examples.md
└── scripts/
    └── helper.py         ← Executed, not loaded into context
```

See [directory-structure.md](skill-authoring/directory-structure.md) for the full sanctioned layout.

Skills follow the [Agent Skills open standard](https://agentskills.io) and work across Claude Code, the API, and Cowork.

---

## 2. Anatomy of a Skill

Every `SKILL.md` has two parts:

```yaml
---
name: skill-name            # Becomes /skill-name slash command
description: What it does and when to use it. Front-load the key use case.
---

# Your instructions here (markdown body)
```

The two required fields are `name` and `description`. Everything else is optional control flags —
who can invoke, which tools are pre-approved, whether it runs forked, which files auto-load it.
**Full field table and flag semantics: [frontmatter-reference.md](skill-authoring/frontmatter-reference.md).**

The body is ordinary markdown. Nothing about it is special except that it all loads at once, which
is what §3 and §4 are about.

### Where files go

The base directory holds only `SKILL.md`. Everything else goes in one of seven sanctioned
subdirectories — `references/`, `assets/`, `sources/`, `scripts/`, `server/`, `cache/`,
`.learnings/`. Two rules worth knowing before you read the full standard:

- **`references/` is consumed by the agent** (read into context, costs tokens, carries OKF
  frontmatter). **`assets/` is consumed by the deliverable** (copied or filled in, often never
  read at all, no frontmatter — it would leak into the output).
- **Nesting is an organization standard, not a token optimization.** Per §3, nothing under the
  skill dir loads until it's read. Layout buys consistency and tooling, not fewer tokens.

**Full standard — the seven subdirs, what belongs in each, and the OKF rules for `references/`:
[directory-structure.md](skill-authoring/directory-structure.md).**

---

## 3. Token Efficiency: The Core Model

Skills use a **three-level loading system** that keeps token costs low by default:

| Level | What's loaded | Token cost |
|---|---|---|
| **Metadata** (always) | `name` + `description` from all skills | ~100 words per skill |
| **SKILL.md body** (on trigger) | Full instructions | Loaded once, persists in session |
| **Supporting files** (on demand) | `references/<topic>.md`, `sources/*`, etc. | Zero until Claude reads them |
| **Scripts** | `scripts/helper.py`, etc. | Zero — executed, not loaded |

### Key insight: the context window is a shared resource

Skill descriptions are always in context so Claude knows what's available. Full skill content loads only when invoked. After invocation, the content **stays in context for the rest of the session** — Claude Code does not re-read the file on later turns. Write guidance that should persist as standing instructions, not one-time steps.

### The "challenge every token" principle

Before adding content to SKILL.md, ask yourself:

- Does Claude already know this?
- Does this paragraph justify its token cost?
- Can I move this to a supporting file loaded on demand?

**Verbose (150 tokens) — avoid:**
```markdown
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but
pdfplumber is recommended because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

**Concise (50 tokens) — preferred:**
```markdown
## Extract PDF text

Use pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

The concise version trusts that Claude knows what PDFs are and how libraries work.

---

## 4. Writing a Lean SKILL.md

### Keep it under 500 lines and ~5,000 tokens

The spec's limit is both: 500 lines **and** 5,000 tokens. Lines are the easier proxy, but a
500-line body that's mostly dense tables or code can blow the token budget while looking compliant —
check tokens when the body is table- or example-heavy. Past either limit, move detailed content to
supporting files. This is a performance guideline and a design signal: a large SKILL.md usually
means content that should be loading conditionally.

### Scope each skill as a coherent unit

Scoping a skill is like scoping a function: it should encapsulate one coherent unit of work that
composes with other skills.

- **Too narrow** → several skills load for one task, adding overhead and conflicting instructions.
- **Too broad** → the description can't trigger precisely, so it fires on the wrong prompts or not
  at all.

"Query this database and format the results" is probably one unit. Adding database administration
to it is not.

### Aim for moderate detail

The failure mode of an over-comprehensive skill isn't just token cost — the agent struggles to
find what's relevant and **actively pursues unproductive paths triggered by instructions that
don't apply to the current task.** Concise stepwise guidance plus one working example beats
exhaustive documentation. When you're writing out every edge case, ask which ones the agent's own
judgment already handles.

### Favor procedures over declarations

Teach the agent *how to approach* a class of problems, not *what to produce* for one instance.

**Declarative (only works for this exact task):**
```markdown
Join `orders` to `customers` on `customer_id`, filter `region = 'EMEA'`, sum `amount`.
```

**Procedural (works for any query in the domain):**
```markdown
1. Read the schema from `references/schema.yaml` to find relevant tables
2. Join using the `_id` foreign key convention
3. Apply the user's filters as WHERE clauses
4. Aggregate numeric columns and format as a markdown table
```

Specific details are still fine — output templates, "never output PII", tool-specific invocations.
The *approach* is what has to generalize.

### Set appropriate degrees of freedom

Match the specificity of instructions to the task's fragility:

**High freedom** — use when multiple approaches are valid or context determines the right path:
```markdown
## Code review process

1. Analyze code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

**Medium freedom** — use when a preferred pattern exists but some variation is acceptable:
```markdown
## Generate report

Use this template and customize as needed:
```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```
```

**Low freedom** — use when operations are fragile, order-dependent, or must be exact:
```markdown
## Database migration

Run exactly this script — do not modify flags:
```bash
python scripts/migrate.py --verify --backup
```
```

> **Analogy:** Think of Claude as navigating a path. A narrow bridge over a cliff needs guardrails and exact instructions. An open field with no hazards just needs a general direction.

### Explain the why, not just the what

Instead of heavy-handed `MUST`/`ALWAYS` directives, explain the reasoning. Claude is smart — when it understands why something matters, it applies the principle correctly across novel situations.

**Directive-only (fragile):**
```markdown
ALWAYS include a table of contents. NEVER skip section headers.
```

**Reason-driven (robust):**
```markdown
Include a table of contents when the document has more than 3 sections — it
helps readers navigate without reading everything, which is the main reason
people reference documentation rather than narrative prose.
```

### Use consistent terminology

Pick one term and use it everywhere. Inconsistency forces Claude to infer equivalence, which introduces errors.

- Choose one: "API endpoint" / "URL" / "API route" / "path" → use only one
- Choose one: "field" / "box" / "element" / "control" → use only one
- Choose one: "extract" / "pull" / "get" / "retrieve" → use only one

---

## 5. Progressive Disclosure Patterns

### Pattern 1: High-level guide with conditional references

The SKILL.md acts as a table of contents. Claude reads reference files only when a specific sub-task is needed.

```markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents.
  Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Additional resources

- **Form filling**: See [references/forms.md](references/forms.md) for complete guide
- **API reference**: See [references/api.md](references/api.md) for all methods
- **Examples**: See [references/examples.md](references/examples.md) for common patterns
```

Claude loads `references/forms.md`, `references/api.md`, or `references/examples.md` only when
needed — zero token cost until then.

### Pattern 2: Domain-organized references

When a skill covers multiple domains, split reference files by domain. Claude reads only the relevant one.

```
bigquery-skill/
├── SKILL.md
└── references/
    ├── index.md        ← required at 4+ files (see directory-structure.md)
    ├── finance.md      ← revenue, billing metrics
    ├── sales.md        ← opportunities, pipeline
    ├── product.md      ← API usage, features
    └── marketing.md    ← campaigns, attribution
```

```markdown
# BigQuery Data Analysis

## Available datasets

- **Finance**: Revenue, ARR, billing → See [references/finance.md](references/finance.md)
- **Sales**: Opportunities, pipeline → See [references/sales.md](references/sales.md)
- **Product**: API usage, features → See [references/product.md](references/product.md)
- **Marketing**: Campaigns, attribution → See [references/marketing.md](references/marketing.md)
```

When the user asks about revenue, Claude reads `references/finance.md` only. The other files consume zero tokens.

### Pattern 3: Conditional workflow branching

```markdown
## Document modification workflow

1. Determine the modification type:
   - **Creating new content?** → Follow "Creation workflow" below
   - **Editing existing content?** → Follow "Editing workflow" below

2. **Creation workflow:**
   - Use docx-js library
   - Build document from scratch

3. **Editing workflow:**
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

### Pattern 4: Shared context authored once, referenced everywhere

**Context that applies to more than one skill or agent gets authored in exactly one place.** A
`SKILL.md` is use-case-specific and rarely reusable — it's the *instructions*. The domain knowledge
those instructions operate on usually isn't specific to one use case at all.

The canonical case is a pair of roles that need identical knowledge and opposite instructions:

```
skills/shared/api-conventions.md      ← the knowledge, authored once
        ↑                      ↑
skills/api-author/SKILL.md    skills/api-reviewer/SKILL.md
  "build endpoints that…"       "flag endpoints that…"
```

Duplicating the conventions into both bodies means every future correction has to be made twice,
and the two copies silently diverge — at which point the reviewer starts rejecting what the author
was told to write.

**Three mechanisms, in order of preference:**

| Mechanism | Use when | How |
|---|---|---|
| Shared reference file | 2+ skills need the same knowledge | Put it in `skills/shared/`, point at `~/.claude/skills/shared/<file>.md` from each SKILL.md with a load-when trigger |
| Skill referenced by multiple agents | Several agents need the same full playbook | List the skill in each agent's `skills:` frontmatter array — the content is injected into every one of their system prompts |
| CLAUDE.md | The guidance must apply in every session regardless of skill | Put it in the global CLAUDE.md. Keep it to a few lines — it costs tokens in every conversation |

**Reference a shared file exactly like a local one** — absolute path plus the condition that should
make Claude read it. It's still progressive disclosure; the file just isn't inside the skill dir:

```markdown
Authoring a new endpoint? Read `~/.claude/skills/shared/api-conventions.md` first —
it has the naming, versioning, and error-shape rules this repo enforces.
```

**The cost:** a path outside the skill directory is a dependency that doesn't travel. It breaks if
the skill is packaged as a standalone `.skill`, cloned somewhere without the same `~/.claude`
layout, or the shared file moves. That's an acceptable trade for knowledge two skills genuinely
share; it's a bad trade for a couple of lines that could just live in both bodies. Share knowledge,
not phrasing.

### Keep references one level deep

Avoid nesting references inside other referenced files. Claude may partially read nested files and miss critical information.

**Bad (too deep):**
```
SKILL.md → references/advanced.md → references/details.md → actual info
```

**Good (one level):**
```
SKILL.md → references/advanced.md (complete info)
SKILL.md → references/api.md (complete info)
```

### Add a table of contents to long reference files

For any reference file over ~100 lines, include a ToC at the top. This ensures Claude sees the full scope even when previewing with partial reads.

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples
```

---

## 6. Descriptions: The Triggering Mechanism

The `description` field is the **primary mechanism** that determines whether Claude invokes a skill. It must balance two goals: tell Claude **what** the skill does and **when** to use it.

### Rules

- Write in **third person** (the description is injected into the system prompt)
- **Front-load** the key use case — descriptions are truncated at ~250 chars in the skill listing
- Include specific **trigger keywords** users would naturally say
- Be specific enough that Claude picks the right skill from 100+ available

**Good description — specific, with triggers:**
```yaml
description: Extracts text and tables from PDF files, fills forms, and merges documents.
  Use when working with PDF files or when the user mentions PDFs, forms, or document
  extraction.
```

**Good description — includes MANDATORY TRIGGERS (pushy is better than undertriggering):**
```yaml
description: |
  Analyze Excel spreadsheets, create pivot tables, generate charts.
  MANDATORY TRIGGERS: Excel, spreadsheet, .xlsx, data table, budget, financial model,
  chart, graph, tabular data, xls
```

**Bad description — too vague:**
```yaml
description: Helps with documents
```

**Bad description — wrong point of view:**
```yaml
description: I can help you process Excel files  # Wrong — first person
description: You can use this to process Excel files  # Wrong — second person
```

### Make descriptions "pushy" to prevent undertriggering

Claude tends to undertrigger skills. To compensate, make descriptions slightly more aggressive about when to invoke:

```yaml
# Too passive:
description: Helps with code explanation

# Better:
description: Explains code with visual diagrams and analogies. Make sure to use this
  skill whenever the user asks how code works, wants a walkthrough, mentions 'explain',
  'how does this work', or asks about a codebase, even if they don't say 'diagram'
  or 'analogy' explicitly.
```

---

## 7. Bundled Scripts: Token-Free Execution

Scripts in the `scripts/` directory can be executed without loading their source into context. This is the most powerful token-efficiency technique for complex skills.

**When to bundle a script:** Look for tasks that would otherwise require Claude to write similar code on every invocation. If test runs of your skill all independently produce a `create_docx.py` or `build_chart.py`, that's a strong signal to bundle it.

**Bundle and reference:**
```
my-skill/
├── SKILL.md
└── scripts/
    ├── analyze_form.py
    ├── validate.py
    └── fill_form.py
```

In SKILL.md, tell Claude to execute — not read — the scripts:

```markdown
## Utility scripts

**analyze_form.py** — Extract all form fields from a PDF:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/analyze_form.py input.pdf > fields.json
```

**validate.py** — Check for errors before applying changes:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/validate.py fields.json
# Returns: "OK" or lists conflicts
```
```

Use `${CLAUDE_SKILL_DIR}` so paths work regardless of the current working directory.

### Script quality guidelines

Write scripts that handle errors rather than failing silently:

```python
# Good — handle errors explicitly with helpful output
def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, "w") as f:
            f.write("")
        return ""

# Bad — punt to Claude
def process_file(path):
    return open(path).read()
```

Document constants so Claude understands them if it needs to adjust:

```python
# Good — self-documenting
REQUEST_TIMEOUT = 30  # HTTP requests typically complete within 30 seconds

# Bad — magic numbers
TIMEOUT = 47  # Why 47?
```

---

## 8. Anti-Patterns to Avoid

### Offering too many options

```markdown
# Bad — confusing
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

# Good — one default, one escape hatch
"Use pdfplumber for text extraction:
  import pdfplumber
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
```

### Deep nested references

```markdown
# Bad
SKILL.md → references/advanced.md → references/details.md → actual info  ← Claude may miss this

# Good
SKILL.md → references/advanced.md (complete)
SKILL.md → references/api.md (complete)
```

### Windows-style paths

```
# Bad (breaks on Unix)
scripts\helper.py

# Good (cross-platform)
scripts/helper.py
```

### Assuming packages are installed

```markdown
# Bad
"Use the pdf library to process the file."

# Good
"Install required package: pip install pypdf

Then use it:
from pypdf import PdfReader
reader = PdfReader('file.pdf')"
```

### Vague names

```
# Bad
helper, utils, tools, documents, data

# Good
processing-pdfs, analyzing-spreadsheets, managing-databases
```

### Unqualified MCP tool references

```markdown
# Bad — may fail with multiple MCP servers
Use the bigquery_schema tool to retrieve schemas.

# Good — fully qualified
Use the BigQuery:bigquery_schema tool to retrieve schemas.
```

---

## 9. Quick Checklist

### Before writing a single line — [evaluation.md](skill-authoring/evaluation.md)

- [ ] Ran the task without the skill — there's a real gap, not an imagined one
- [ ] Content comes from a real task trace or real project artifacts, not model general knowledge
- [ ] Scope is one coherent unit of work — not two jobs, not half a job
- [ ] What does the skill do, and what should trigger it?
- [ ] Are there scripts that should be bundled to avoid repeated generation?

### Description quality
- [ ] Written in third person
- [ ] Front-loads the key use case (first 250 chars are what matter most)
- [ ] Includes specific trigger keywords users would say
- [ ] Slightly "pushy" to prevent undertriggering

### SKILL.md body
- [ ] Under 500 lines and ~5,000 tokens
- [ ] Gotchas section present, in the body (not a reference file)
- [ ] Instructions are procedural (generalize) rather than answers to one instance
- [ ] Every token earns its place — Claude doesn't need explanations of things it already knows
- [ ] Explains the "why" behind instructions, not just the "what"
- [ ] Consistent terminology throughout (pick one term per concept)
- [ ] No time-sensitive information (or isolated in a "legacy patterns" section)
- [ ] File references are one level deep from SKILL.md
- [ ] Long reference files (>100 lines) have a table of contents

### Supporting files
- [ ] Reference files exist for domain-specific content loaded on demand
- [ ] Scripts bundled for deterministic or repetitive operations
- [ ] `${CLAUDE_SKILL_DIR}` used in script paths for portability

### Behavioral consistency — [behavior-patterns.md](skill-authoring/behavior-patterns.md)
- [ ] Output templates provided for format-critical tasks
- [ ] 2–5 input/output examples for style-critical outputs
- [ ] Workflow checklists for multi-step processes
- [ ] Validation/feedback loops for quality-critical tasks
- [ ] Plan validated against a source of truth before batch or destructive work

### Control & safety — [frontmatter-reference.md](skill-authoring/frontmatter-reference.md)
- [ ] `disable-model-invocation: true` for side-effect commands (`/deploy`, `/commit`)
- [ ] `allowed-tools` set for tools needed without per-use approval
- [ ] No Windows-style paths (all forward slashes)
- [ ] Dependencies explicitly documented with install commands

### Testing — [evaluation.md](skill-authoring/evaluation.md)
- [ ] At least 3 evaluations created
- [ ] Tested with the model(s) you plan to use
- [ ] Tested with real usage scenarios, not just obvious cases
- [ ] Trigger eval set reviewed to confirm the description fires correctly

---

## Community Insights

Field-tested patterns from real-world usage — undertriggering / trigger-rate research, the
caveman token-compression technique, the `.learnings/` self-improvement pattern, the
Skills-vs-CLAUDE.md decision, the MUST/ALWAYS tension, and a table of notable community repos —
live in a companion file: **`~/.claude/skills/shared/community-insights.md`**. Read it when a
task touches token efficiency, trigger reliability, or community best practices. It's kept
separate because it's field reports, not official guidance, and evolves on its own cadence.

---

*Last updated: July 2026*
*Official sources: [Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)*
*Open standard: [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) · [Specification](https://agentskills.io/specification) · [Evaluating skills](https://agentskills.io/skill-creation/evaluating-skills) · [Optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)*
*Community sources: [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) · [obra/superpowers](https://github.com/obra/superpowers) · [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) · [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) · [Delphine-L token-efficiency](https://github.com/Delphine-L/claude_global) · [anthropics/skills](https://github.com/anthropics/skills)*

---
