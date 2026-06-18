# Claude Skills Best Practices
### Minimizing Token Usage & Creating Consistent Behavior

> **Sources:** Anthropic official documentation ([code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), [platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)), internal skill-creator SKILL.md, and real-world skill examples.

---

## Table of Contents

1. [What Skills Are](#1-what-skills-are)
2. [Anatomy of a Skill](#2-anatomy-of-a-skill)
   - [Sanctioned directory structure (this repo's standard)](#sanctioned-directory-structure-this-repos-standard)
3. [Token Efficiency: The Core Model](#3-token-efficiency-the-core-model)
4. [Writing a Lean SKILL.md](#4-writing-a-lean-skillmd)
5. [Progressive Disclosure Patterns](#5-progressive-disclosure-patterns)
6. [Descriptions: The Triggering Mechanism](#6-descriptions-the-triggering-mechanism)
7. [Consistent Behavior Patterns](#7-consistent-behavior-patterns)
8. [Frontmatter Reference & Control Flags](#8-frontmatter-reference--control-flags)
9. [Dynamic Context Injection](#9-dynamic-context-injection)
10. [Bundled Scripts: Token-Free Execution](#10-bundled-scripts-token-free-execution)
11. [Anti-Patterns to Avoid](#11-anti-patterns-to-avoid)
12. [Evaluation & Iteration Workflow](#12-evaluation--iteration-workflow)
13. [Quick Checklist](#13-quick-checklist)

---

## 1. What Skills Are

A **skill** is a directory containing a `SKILL.md` file that gives Claude a detailed playbook for a specialized task. Claude discovers available skills from their metadata and loads the full instructions only when relevant. Skills support slash-command invocation (`/skill-name`) and automatic model-triggered invocation.

```
~/.claude/skills/my-skill/
├── SKILL.md          ← Required entrypoint
├── reference.md      ← Loaded on demand
├── examples.md       ← Loaded on demand
└── scripts/
    └── helper.py     ← Executed, not loaded into context
```

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

### Frontmatter field quick reference

| Field | Required | Notes |
|---|---|---|
| `name` | No (uses dir name) | Lowercase, hyphens, max 64 chars |
| `description` | **Recommended** | Max 1024 chars; truncated at ~250 chars in skill listing |
| `disable-model-invocation` | No | `true` = only user can invoke |
| `user-invocable` | No | `false` = only Claude invokes, hidden from `/` menu |
| `allowed-tools` | No | Pre-approve tools without per-use prompts |
| `context` | No | `fork` = run in isolated subagent |
| `agent` | No | Which subagent type when `context: fork` |
| `paths` | No | Glob patterns; skill auto-loads only for matching files |
| `model` | No | Model override for this skill |
| `effort` | No | `low`/`medium`/`high`/`max` |

---

### Sanctioned directory structure (this repo's standard)

> This is **this repo's** convention layered on top of the official loading model in §3 — not
> Anthropic guidance. It exists so every skill has the same shape and tooling (`skill-maker`,
> `skill-audit`) can assume it.

**The base directory holds only `SKILL.md`.** Everything else goes in one of six sanctioned
subdirectories. All are optional — add one only when the skill needs it. Don't invent siblings;
`server/` was added precisely so MCP servers stopped being a one-off.

| Subdir | Holds | Loading | Index? |
|---|---|---|---|
| `references/` | Detailed agent-ready markdown, split by topic/domain | Lazy — zero tokens until read | Only past ~8–10 files |
| `sources/` | Raw data (API dumps, large JSON/CSV) too costly to load casually | Lazy — high token cost, dig in only when needed | Only past ~8–10 files |
| `scripts/` | Executable code Claude **runs**, not reads | Token-free — executed, never loaded | **Never** — describe at call site |
| `server/` | Long-running / hosted processes (e.g. MCP servers) | Started, not loaded | **Never** — describe at call site |
| `cache/` | Runtime/generated state a script writes and later reads | Not loaded — runtime only | n/a — gitignored, never committed |
| `.learnings/` | Accumulated gotchas (`LEARNINGS.md`, `ERRORS.md`) | Read + summarized at task start | n/a — execution skills only |

```
skills/<category>/<skill-name>/
├── SKILL.md            # the only file in the base dir
├── references/         # topic docs, lazy-loaded; index.md only past ~8–10 files
│   └── <topic>.md
├── sources/            # raw data; high token cost; index.md only past ~8–10 files
├── scripts/            # run via ${CLAUDE_SKILL_DIR}/scripts/...; never indexed
├── server/             # long-running processes (MCP servers); never indexed
├── cache/              # runtime state a script generates; gitignored, never committed
└── .learnings/         # execution skills only
    ├── LEARNINGS.md
    └── ERRORS.md
```

**This is an organization standard, not a token optimization.** Flat vs nested doesn't change
what loads — per §3, only the SKILL.md body loads on trigger, references/sources cost nothing
until read, and scripts/server never load. The subdirs buy authoring consistency, not fewer
tokens. The one real token lever is `index.md`, and it cuts both ways (below).

**`index.md` — `references/` and `sources/` only, and only at scale.** SKILL.md is the index by
default: it lists the files and says *when* to load each ("writing a new gear? load
gear-basics.md"). Add an `index.md` only once a folder grows past ~8–10 files and enumerating
them inline would bloat SKILL.md. Below that, an index is a redundant read hop and a second
thing to keep in sync. Keep it a pure pointer list (filename + one line) — an index that holds
content Claude actually needs creates the `SKILL.md → index.md → file` two-hop that §5 and §11
warn against.

**`scripts/` and `server/` are described at their call site, never indexed.** The caller doesn't
browse to pick a script — it needs the invocation contract (args in, what it writes/returns, exit
codes) inline next to the `${CLAUDE_SKILL_DIR}/scripts/foo.py` call. Always use
`${CLAUDE_SKILL_DIR}` for paths so they survive being symlinked into `~/.claude` and cloned
elsewhere.

**`.learnings/` is for execution skills only.** A pure reference/lookup skill has no "runs" to
learn from. It's writable and append-only, so periodically promote hot learnings into the SKILL.md
body and prune — otherwise it drifts from reality.

**`cache/` is where runtime state goes — never the base dir.** If a skill's script needs to write
generated state (a workspace dump, a resolved-ID lookup, anything fetched-then-reused), it writes
to `cache/` under the skill root, e.g. `${CLAUDE_SKILL_DIR}/cache/`. It's gitignored repo-wide by
`skills/*/*/cache/`, so it's never committed and doesn't count as authored skill content — a
script can rebuild it from scratch. Don't scatter runtime files at the skill root or invent
per-skill names for them.

**Data policy for `sources/` and `scripts/` fixtures.** Raw data and fixtures bloat a repo that's
cloned and symlinked into `~/.claude`. Commit small representative samples; fetch large dumps via
a script or keep them out of the repo.

---

## 3. Token Efficiency: The Core Model

Skills use a **three-level loading system** that keeps token costs low by default:

| Level | What's loaded | Token cost |
|---|---|---|
| **Metadata** (always) | `name` + `description` from all skills | ~100 words per skill |
| **SKILL.md body** (on trigger) | Full instructions | Loaded once, persists in session |
| **Supporting files** (on demand) | `reference.md`, `examples.md`, etc. | Zero until Claude reads them |
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

### Keep it under 500 lines

Once the body exceeds ~500 lines, move detailed content to supporting files. This is both a performance guideline and a design signal: if your SKILL.md is growing large, you likely have content that should be loaded conditionally.

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

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude loads `FORMS.md`, `REFERENCE.md`, or `EXAMPLES.md` only when needed — zero token cost until then.

### Pattern 2: Domain-organized references

When a skill covers multiple domains, split reference files by domain. Claude reads only the relevant one.

```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md      ← revenue, billing metrics
    ├── sales.md        ← opportunities, pipeline
    ├── product.md      ← API usage, features
    └── marketing.md    ← campaigns, attribution
```

```markdown
# BigQuery Data Analysis

## Available datasets

- **Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
- **Sales**: Opportunities, pipeline → See [reference/sales.md](reference/sales.md)
- **Product**: API usage, features → See [reference/product.md](reference/product.md)
- **Marketing**: Campaigns, attribution → See [reference/marketing.md](reference/marketing.md)
```

When the user asks about revenue, Claude reads `reference/finance.md` only. The other files consume zero tokens.

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

### Keep references one level deep

Avoid nesting references inside other referenced files. Claude may partially read nested files and miss critical information.

**Bad (too deep):**
```
SKILL.md → advanced.md → details.md → actual info
```

**Good (one level):**
```
SKILL.md → advanced.md (complete info)
SKILL.md → reference.md (complete info)
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

## 7. Consistent Behavior Patterns

### Template pattern

Providing exact output templates is the most reliable way to enforce consistent formatting:

```markdown
## Report structure

Use this exact template:

```markdown
# [Analysis Title]

## Executive Summary
[One-paragraph overview of key findings]

## Key Findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
```

When some flexibility is appropriate, signal it explicitly:

```markdown
## Report structure

Use this as a sensible default, adapting sections based on what you discover:

```markdown
# [Analysis Title]
## Executive Summary
## Key Findings
## Recommendations
```
Adjust sections as needed — for instance, if findings cluster differently.
```

### Examples pattern (few-shot in skills)

Input/output examples are the most reliable way to communicate desired style and detail level. Include 2–5 pairs:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation on a new line.
```

### Workflow checklists for complex tasks

For multi-step tasks where skipped steps cause failures, provide a checklist Claude copies and tracks:

```markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
This extracts form fields and saves to `fields.json`.

**Step 3: Validate mapping**
Run: `python scripts/validate_fields.py fields.json`
Fix any validation errors before continuing.
```

### Feedback loops

The validate-fix-repeat loop dramatically improves output quality:

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python scripts/pack.py unpacked_dir/ output.docx`
```

Make validation scripts verbose with specific error messages like: `"Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed"` — specific errors help Claude fix the issue on the next attempt.

### Avoid time-sensitive information

Content tied to specific dates will become wrong. Use a "legacy patterns" section instead:

**Bad:**
```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**Good:**
```markdown
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Legacy patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>
The v1 API used: `api.example.com/v1/messages`
This endpoint is no longer supported.
</details>
```

---

## 8. Frontmatter Reference & Control Flags

### Controlling invocation

```yaml
# Only the user can invoke (good for /deploy, /commit — side-effect commands)
disable-model-invocation: true

# Only Claude invokes (good for background reference skills)
user-invocable: false
```

| Frontmatter | User can `/invoke` | Claude auto-loads | Context loading |
|---|---|---|---|
| (default) | Yes | Yes | Description always; full body on invoke |
| `disable-model-invocation: true` | Yes | No | Description not in context |
| `user-invocable: false` | No | Yes | Description always; full body on invoke |

### Pre-approving tools

Avoid per-use approval prompts for skills with known tool needs:

```yaml
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
```

### Path-scoped skills

Automatically load a skill only when working with specific files:

```yaml
paths: "packages/frontend/**/*.tsx, packages/frontend/**/*.ts"
```

### Subagent isolation

Run a skill in its own forked context (no conversation history):

```yaml
context: fork
agent: Explore   # Built-in: Explore, Plan, general-purpose; or custom subagent name
```

### Argument substitution

```yaml
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

# Or with indexed args:
Migrate the $0 component from $1 to $2.
```

---

## 9. Dynamic Context Injection

The `` !`command` `` syntax executes shell commands *before* the skill content reaches Claude. The output replaces the placeholder inline:

```yaml
---
name: pr-summary
description: Summarize a pull request with live diff data
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request: what changed, why, and any concerns.
```

For multi-line injection, use a fenced code block with `` ```! ``:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

This runs entirely as preprocessing — Claude only sees the final rendered result.

---

## 10. Bundled Scripts: Token-Free Execution

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

## 11. Anti-Patterns to Avoid

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
SKILL.md → advanced.md → details.md → actual info  ← Claude may miss this

# Good
SKILL.md → advanced.md (complete)
SKILL.md → reference.md (complete)
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

## 12. Evaluation & Iteration Workflow

### Evaluation-driven development

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

### The Claude A / Claude B development loop

The most effective method uses two Claude instances:

- **Claude A** (your conversation) — refines the skill with you, has full context
- **Claude B** (fresh instance with skill loaded) — tests it on real tasks

Observe where Claude B struggles:
- Unexpected exploration paths (structure isn't intuitive)
- Missed file connections (links need to be more explicit)
- Overreliance on one section (that content should be in SKILL.md)
- Ignored content (unnecessary or poorly signaled)

Bring observations back to Claude A: *"When I asked Claude B for a regional sales report, it forgot to filter out test accounts. The skill mentions it, but maybe it's not prominent enough?"*

### Description optimization

After the skill content is stable, run the description through an optimization loop with trigger evals:

```json
[
  {"query": "ok so my boss sent me this xlsx file...", "should_trigger": true},
  {"query": "can you write a python script to parse csv?", "should_trigger": false}
]
```

Test with queries realistic enough that Claude would genuinely benefit from the skill (simple, one-step queries won't trigger skills regardless of description quality).

---

## 13. Quick Checklist

### Before writing a single line

- [ ] What gaps exist when Claude works without this skill?
- [ ] What does the skill do, and what should trigger it?
- [ ] Are there scripts that should be bundled to avoid repeated generation?

### Description quality
- [ ] Written in third person
- [ ] Front-loads the key use case (first 250 chars are what matter most)
- [ ] Includes specific trigger keywords users would say
- [ ] Slightly "pushy" to prevent undertriggering

### SKILL.md body
- [ ] Under 500 lines
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

### Behavioral consistency
- [ ] Output templates provided for format-critical tasks
- [ ] 2–5 input/output examples for style-critical outputs
- [ ] Workflow checklists for multi-step processes
- [ ] Validation/feedback loops for quality-critical tasks

### Control & safety
- [ ] `disable-model-invocation: true` for side-effect commands (`/deploy`, `/commit`)
- [ ] `allowed-tools` set for tools needed without per-use approval
- [ ] No Windows-style paths (all forward slashes)
- [ ] Dependencies explicitly documented with install commands

### Testing
- [ ] At least 3 evaluations created
- [ ] Tested with the model(s) you plan to use
- [ ] Tested with real usage scenarios, not just obvious cases
- [ ] Trigger eval set reviewed to confirm the description fires correctly

---

## Real-World Examples

### Minimal reference skill

```yaml
---
name: api-conventions
description: API design patterns for this codebase. Use when writing or reviewing
  API endpoints, designing new routes, or asking about request/response formats.
user-invocable: false
---

When writing API endpoints:
- Use RESTful naming conventions (`/users/{id}`, not `/getUser`)
- Return consistent error format: `{"error": {"code": "...", "message": "..."}}`
- Include request validation before any database calls
- Paginate list endpoints with `cursor` (not `page`/`offset`)
```

### Task skill with subagent isolation

```yaml
---
name: deep-research
description: Thoroughly researches a topic across the codebase with file references.
  Use when the user asks to "research", "find all usages of", "understand how X works",
  or needs a comprehensive summary of how something is implemented.
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references and line numbers
```

### Safe deploy skill (user-only invocation)

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(npm *) Bash(git *)
---

Deploy $ARGUMENTS to production:

1. Run the test suite: `npm test`
2. Build: `npm run build`
3. Confirm with user before pushing
4. Push to deployment target
5. Verify the deployment succeeded
```

### Skill with dynamic context injection

```yaml
---
name: pr-summary
description: Summarize the current pull request with live data. Use when the user
  asks to summarize a PR, write a PR description, or review what changed in a branch.
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

Summarize this pull request: what changed, why it was changed, potential concerns,
and a one-sentence description suitable for a changelog entry.
```

---

---

## Community Insights: What Developers Are Actually Doing

> This section summarizes findings from GitHub repositories, developer blogs, community experiments, and forum discussions as of April 2026. These are practitioner discoveries, not official guidance — treat them as field reports.

---

### The Skills vs. CLAUDE.md Decision

One of the most-discussed topics in the community is where to put instructions. The consensus, widely documented in repositories like [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) and [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice), is:

> "Skills are more token-efficient because Claude Code only loads them when needed. If you want something simpler, you can put a condensed version in `~/.claude/CLAUDE.md` instead, but that gets loaded into every conversation whether you need it or not."

**Community rule of thumb:**
- `CLAUDE.md` → universal rules you need in every session (coding style, project conventions, always-on behavior)
- Skills → specialized workflows you need occasionally (deployment, PR reviews, document creation)
- If you find yourself typing the same prompt repeatedly across multiple conversations → it's time to create a skill

The popular heuristic: if it wouldn't hurt to have the instructions loaded for *every* conversation, put it in CLAUDE.md. If it's only needed sometimes, make it a skill.

---

### Trigger Rate Research: Real Numbers from the Community

The biggest real-world pain point developers report is skills that simply don't activate when expected. Community researcher Ivan Seleznov ran 650 trials ([documented on Medium](https://medium.com/@ivan.seleznov1/why-claude-code-skills-dont-activate-and-how-to-fix-it-86f679409af1)) and found:

| Description quality | Activation rate |
|---|---|
| Default/vague description | ~20% |
| Optimized description | ~50% |
| Optimized + examples in description | ~72–90% |

Key finding: **Claude loads only the frontmatter of all available skills before deciding what to do.** Only after choosing the right skill does it load the full content. This means a poorly written description guarantees the skill is never invoked — even if the body is perfect.

**What the community found works best:**
- Front-load the exact phrase a user would say: `"Use when the user says 'review this PR'"` outperforms `"Useful for code review"`
- Include MANDATORY TRIGGERS in all-caps as a block in the description
- List synonyms and alternate phrasings: `"report, memo, document, writeup, summary"` rather than just `"report"`
- Add `"even if they don't explicitly mention [X]"` to catch implicit requests

---

### The "Caveman" Technique: Output Token Compression

One of the most viral community discoveries of 2025-2026 is the **caveman skill** ([JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), 562+ stars), which cuts output tokens by constraining Claude's communication style:

> "why use many token when few token do trick"

The skill instructs Claude to drop articles (a/an/the), filler words (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), and hedging — while keeping all technical content and code intact.

**Benchmarked results** (verified with tiktoken):

| Task type | Output token reduction |
|---|---|
| Web search responses | 68% |
| Code edits | 50% |
| Q&A exchanges | 72% |
| Average | **~61%** |

The skill includes auto-clarity safeguards that automatically suspend caveman mode for security warnings, irreversible actions, or multi-step sequences where fragmentation risks misunderstanding. Code, commits, and PRs always use normal writing.

**The actual SKILL.md for caveman is elegantly minimal:**

```yaml
---
name: caveman
description: Reduce output tokens by ~65% by responding in terse, article-free language.
  Use when the user asks for caveman mode, wants shorter responses, or wants to reduce
  token usage. Drops: articles (a/an/the), filler, pleasantries, hedging.
---

Respond like smart caveman. Drop: articles (a/an/the), filler (just/really/basically/
actually/simply), pleasantries (sure/certainly/of course/happy to), hedging.
Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for").
Pattern: [thing] [action] [reason]. [next step].

Auto-clarity: suspend caveman for security warnings, irreversible actions, or
multi-step sequences where fragmentation risks misunderstanding.
Code/commits/PRs: write normal.
```

It demonstrates a core principle many developers have internalized: **the most token-efficient skills are often the shortest ones, because they rely on Claude's existing intelligence rather than trying to replicate it.**

---

### The `learnings.md` Pattern: Self-Improving Skills

A popular community pattern emerging from [MindStudio](https://www.mindstudio.ai/blog/self-learning-claude-code-skill-learnings-md) and the [openclaw-skills](https://lobehub.com/skills/openclaw-skills-self-improving-agent-1-0-2) project is the **self-learning skill**: bundling a `learnings.md` file alongside your SKILL.md that captures what worked and what didn't.

**Structure:**
```
my-skill/
├── SKILL.md
└── .learnings/
    ├── LEARNINGS.md     ← what worked, observations
    ├── ERRORS.md        ← failures and how they were fixed
    └── FEATURE_REQUESTS.md  ← gaps identified during use
```

Each entry in `LEARNINGS.md` uses a structured format:
```markdown
## [2026-03-14] Timestamp | Priority: HIGH | Status: RESOLVED
**Area:** form-filling
**Summary:** pdfplumber fails on scanned PDFs
**Details:** OCR step required before extraction for any PDF created by scanning
**Suggested action:** Add check for scanned PDFs before running extraction
```

**Key insight from the community:** Have Claude *summarize* the learnings file at the very start of a task rather than just reading it. Summarizing forces Claude to process and internalize the content rather than skimming past it.

The learnings file gets referenced from SKILL.md:
```markdown
## Before starting

Read and summarize .learnings/LEARNINGS.md and .learnings/ERRORS.md to
internalize what has worked and what has failed in previous runs.
```

Over time, the most important learnings get "promoted" into the main SKILL.md body, while the learnings file continues accumulating new observations.

---

### The `obra/superpowers` Framework: Battle-Tested Patterns

The [obra/superpowers](https://github.com/obra/superpowers) repository (143k stars) is the most prominent community skills framework, built around a **mandatory seven-stage pipeline** that runs automatically:

```
brainstorm → workspace isolation → planning → execution → testing → review → completion
```

Key design principles that have influenced the broader community:

**Subagent-driven execution:** Fresh specialized agents are dispatched per task rather than using a monolithic conversation. This avoids context pollution and maintains consistent behavior across sessions.

**Two-stage review:** Every piece of work goes through specification compliance validation *then* code quality assessment. Separating these concerns prevents one from masking failures in the other.

**Task granularity standard:** Tasks are broken into 2–5 minute units with exact file paths and complete code snippets. Vague, open-ended tasks produce inconsistent results; granular tasks don't.

**Red-green-refactor enforcement:** Code written before a corresponding failing test is automatically deleted. The discipline is non-negotiable in the skill instructions.

**Community verdict on superpowers:** Developers consistently report it works well for software development workflows but can feel over-engineered for lighter use cases. The underlying principles (subagents, test-first, explicit planning stage) are widely borrowed even by developers who don't use the framework wholesale.

---

### The Token-Efficiency Expert Skill: A Community Benchmark

The [token-efficiency SKILL.md](https://github.com/Delphine-L/claude_global/blob/main/skills/claude-meta/token-efficiency/SKILL.md) community skill codified what many developers had learned informally. Its central insight:

> "Reading files costs tokens. Bash commands don't."

**Decision framework from the skill:**

| Operation | Approach | Token cost |
|---|---|---|
| Create a new file | Write directly | Low |
| Short output (<100 lines) | Claude context | Low |
| Modify code | Read + Edit | Medium |
| Modify large data files | Bash commands (sed, awk, cp) | Negligible |

**The 90-95% claim:** The skill's author documents a realistic drop from ~500K tokens/week (wasteful approach) to 30–50K tokens/week by applying these rules: always filter before reading, never read an entire log file, use `grep`/`head`/`tail` first, check `git status --short` and `package.json` before opening large files.

**Two-model strategy:** The community widely uses Opus for the "understanding" phase (architecture, codebase comprehension, design decisions — one-time 10–15 minute investment) and Sonnet for all execution. This alone delivers ~50% cost reduction for projects requiring deep initial analysis.

---

### Community Debates and Unresolved Questions

**"Skills vs. CLAUDE.md" is not settled.** Some developers argue that a well-structured `CLAUDE.md` with clear sections is easier to maintain than a collection of skills, since you always know where everything is. Others counter that the on-demand loading of skills is the only real way to manage a large collection of specialized workflows without constant context pressure.

**On description verbosity:** There's tension between the official recommendation to keep descriptions concise (truncated at 250 chars in listing) and the community finding that longer, keyword-rich, trigger-explicit descriptions improve activation rates significantly. The practical answer: front-load the 250-char essentials, then extend with keyword lists after the truncation point — they still influence activation even if they don't appear in the listing.

**On skill granularity:** Should you build one large "document processing" skill or separate `pdf-processing`, `docx-editing`, and `xlsx-analysis` skills? Community consensus leans toward **granular skills** because descriptions are more specific and triggers are more reliable. Monolithic skills tend to have vague descriptions that undertrigger.

**On MUST/ALWAYS directives:** The community is split. Many developers report that explicit `MUST`/`ALWAYS` directives in all caps do improve compliance for stubborn behavioral requirements. Others find them brittle — when Claude encounters an edge case the directive didn't anticipate, it either over-applies the rule or ignores it entirely. The middle path most developers land on: use strong directives sparingly, and always accompany them with a rationale.

---

### Quick Hits: Tips Widely Shared Across the Community

- **Version skills with git tags.** Skills evolve; being able to roll back to a known-good version has saved many developers from regressions in production workflows.

- **The "repeat prompt" test.** Before building a skill, notice if you've pasted the same prompt into Claude more than three times. That's the threshold most developers cite as the trigger to formalize it into a skill.

- **Security review before install.** Skills execute arbitrary code. The community consensus is firm: never install a skill from an untrusted source without reading every file, including all scripts. This is especially important in team environments.

- **Test skills with Haiku first.** If a skill works with Haiku, it's well-written. Haiku has less reasoning overhead to compensate for ambiguous instructions, so skills that work on Haiku tend to be robust across all models. Skills that only work on Opus may have instructions that are doing less work than you think.

- **The `${CLAUDE_SKILL_DIR}` variable is underused.** Many community skills hardcode paths that break when installed to a different location. Using `${CLAUDE_SKILL_DIR}` for all script references makes skills truly portable.

- **CLAUDE.md + skills hybrid:** Several popular community setups use CLAUDE.md solely for project context (architecture, conventions, key files), while all *behavioral* instructions (how to commit, how to review, how to test) live in skills. This keeps CLAUDE.md small and focused.

---

### Notable Community Resources

| Resource | What it offers |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Official Anthropic skill repository — production reference implementations |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Curated list of 1,234+ community skills |
| [obra/superpowers](https://github.com/obra/superpowers) | 7-stage dev pipeline framework, 143k stars |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Token compression via caveman-mode communication |
| [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | 45 practical Claude Code tips including skills |
| [Delphine-L/claude_global](https://github.com/Delphine-L/claude_global) | Token efficiency skill and global skill patterns |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 135 agents, 35 skills, 42 commands mega-toolkit |
| [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Comprehensive beginner-to-power-user guide |

---

*Last updated: April 2026*
*Official sources: [Extend Claude with skills](https://code.claude.com/docs/en/skills) · [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) · [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)*
*Community sources: [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) · [obra/superpowers](https://github.com/obra/superpowers) · [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) · [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) · [Delphine-L token-efficiency](https://github.com/Delphine-L/claude_global) · [anthropics/skills](https://github.com/anthropics/skills)*

---

---

## Appendix: Alignment with the Anthropic `skill-creator` Skill

> This section compares the guide against Anthropic's official `skill-creator` SKILL.md — the tool used to build, evaluate, and improve skills from within Claude itself. It maps what aligns, what the guide underemphasizes, and where the two sources are in genuine tension.

---

### Where this guide and skill-creator agree

The core structural guidance is consistent throughout:

- Three-level progressive disclosure (metadata → body → supporting files)
- Keep SKILL.md under 500 lines; move detail to referenced files
- Description is the primary triggering mechanism
- Bundle scripts for repeated work rather than having Claude regenerate them
- Explain the "why" behind instructions, not just the "what"
- Write → test → review → iterate as the fundamental development loop
- Progressive disclosure for reference files; one level deep from SKILL.md

---

### What skill-creator covers that this guide underemphasizes

**The evaluation loop is a tooled, measured process — not just a suggestion**

This guide says "build evaluations" across roughly one section. The skill-creator devotes most of its length to the mechanics of doing this rigorously:

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

Without a baseline, you cannot know whether your changes actually helped. The guide implies this but never states it as a requirement.

**Read the transcripts, not just the final outputs**

skill-creator explicitly instructs: *read the transcripts from the test runs and notice if the skill is making the model waste time doing things that are unproductive. If all 3 test cases resulted in the subagent writing a `create_docx.py`, that's a signal the skill should bundle that script.*

The guide is entirely output-focused. Transcripts reveal latent waste that output quality scores completely miss.

**Beware of overfitting to your test cases**

skill-creator has an important caution this guide lacks:

> "We're trying to create skills that can be used a million times across many different prompts. Here you and the user are iterating on only a few examples. If the skill works only for those examples, it's useless."

Fiddly, over-specific changes that fix one failing test often make the skill more brittle across the real distribution of prompts. The corrective: try different metaphors, different patterns, or restructured workflows rather than adding narrow guardrails.

**Description optimization is an automated loop with scripts**

The guide mentions "optimize your description" generically. skill-creator specifies the actual mechanism:

```bash
python -m scripts.run_loop \
  --eval-set trigger-eval.json \
  --skill-path path/to/skill \
  --model claude-sonnet-4-6 \
  --max-iterations 5
```

This runs a 60/40 train/test split, evaluates each query **3 times** for a reliable trigger rate (not once), proposes improvements based on failures, and selects the best description on held-out test score — specifically to avoid overfitting to the training queries. The guide's description optimization guidance is much weaker than this.

**Blind comparison for rigorous A/B testing**

skill-creator includes an advanced evaluation mode (see `agents/comparator.md` and `agents/analyzer.md`) where two skill versions are shown to an independent agent without labeling which is which, then analyzed for *why* the winner won. This produces more objective quality judgments than self-evaluation. The guide doesn't mention this at all.

**Packaging for distribution**

skill-creator ends with `scripts/package_skill.py` producing a distributable `.skill` file. The guide has no equivalent — it treats skills as local configurations rather than artifacts to be shared or versioned.

**Cowork-specific mechanics**

skill-creator has a dedicated section for Cowork environments:
- No subagents → run test cases sequentially, skip baselines
- No display → use `--static <output_path>` for a standalone HTML viewer file instead of a live server
- "Submit All Reviews" downloads `feedback.json` rather than posting to a server
- Packaging still works via `package_skill.py`

The guide acknowledges Cowork briefly but doesn't document these mechanics.

---

### What this guide covers that skill-creator does not

These topics are out of scope for skill-creator (which focuses on the creation/eval workflow), but are real and useful:

- Complete frontmatter field reference (`paths`, `effort`, `model`, `hooks`, `context`, `agent`, `shell`, argument substitution with `$ARGUMENTS[N]` and `${CLAUDE_SKILL_DIR}`)
- Dynamic context injection (`` !`command` `` and `` ```! `` block syntax)
- Invocation control nuances: `disable-model-invocation` vs `user-invocable` and when each applies
- Domain-organized reference file pattern with per-domain loading
- Anti-patterns section (Windows paths, deeply nested references, assuming packages installed, MCP tool name qualification)
- The entire community section: caveman compression, learnings.md self-improvement pattern, trigger rate research, superpowers framework, Skills vs. CLAUDE.md decision framework

---

### One genuine tension

skill-creator says: *"Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag."*

The community section of this guide reports the opposite experience: many developers find that explicit `MUST`/`ALWAYS` directives reliably improve compliance for behaviors that are otherwise inconsistent. Community trigger research even recommends `MANDATORY TRIGGERS` in all-caps as a description technique.

**The reconciliation:** skill-creator's advice targets the *body* of the skill — where over-directive language can make instructions brittle and hard to generalize. The community advice tends to target *descriptions* and *trigger phrases*, where more aggressive language genuinely helps Claude pick the right skill. The two recommendations apply to different parts of the file and are not actually contradictory once you separate them.

---

### Summary table

| Topic | This guide | skill-creator |
|---|---|---|
| Progressive disclosure | ✅ Complete | ✅ Complete |
| 500-line limit | ✅ | ✅ |
| Description as trigger | ✅ Complete | ✅ Complete |
| Bundle scripts | ✅ | ✅ |
| Explain the why | ✅ | ✅ |
| Eval loop mechanics (scripts, viewer, grader) | ⚠️ Surface level | ✅ Detailed |
| Baseline comparisons | ⚠️ Implied | ✅ Required |
| Read transcripts, not just outputs | ❌ Missing | ✅ |
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
