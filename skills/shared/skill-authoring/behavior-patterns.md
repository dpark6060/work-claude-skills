---
type: Pattern Library
title: Skill Behavior Patterns
description: Reusable patterns for making a skill produce consistent behavior — templates, few-shot examples, gotchas, plan-validate-execute, checklists, and validation loops.
tags: [skills, patterns, consistency]
timestamp: 2026-07-31T00:00:00Z
---

# Skill Behavior Patterns

> **Load when:** a skill's output needs to come out the same way every run, or a multi-step
> workflow keeps getting steps skipped. Browse for the pattern that fits — you don't need to read
> it end to end. Companion to
> [claude-skills-best-practices.md](../claude-skills-best-practices.md) (the core rulebook).

Not every skill needs all of these. Pick the ones that fit the task.

## Template pattern

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

Short templates live inline like these. A long template, or one needed only in certain cases, goes
in `assets/` and gets referenced from SKILL.md so it loads only when that case comes up — and
because it's an asset, it carries no OKF frontmatter to leak into the output. See
[directory-structure.md](directory-structure.md).

## Examples pattern (few-shot in skills)

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

## Gotchas sections

Often the highest-value content in a skill: environment-specific facts that defy reasonable
assumptions. Not general advice ("handle errors appropriately") — concrete corrections to mistakes
the agent *will* make otherwise.

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include `WHERE deleted_at IS NULL`
  or results include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service, and `accountId`
  in the billing API. All three are the same value.
- `/health` returns 200 as long as the web server is up, even with the database down.
  Use `/ready` for real service health.
```

**Keep gotchas in the SKILL.md body, not a reference file.** A reference only loads when the agent
recognizes the trigger to load it — and the whole point of a gotcha is that the agent doesn't know
the trap is there. This is the one category where inline token cost is clearly worth it.

Every time you have to correct the agent mid-task, that correction belongs here. This pairs with
`.learnings/` ([directory-structure.md](directory-structure.md)): learnings accumulate raw during
runs, hot ones get promoted into this section.

## Plan-validate-execute for batch or destructive work

Before a batch or irreversible operation, have the agent write an intermediate plan in a structured
format, validate it against a source of truth, and only then execute.

```markdown
## PDF form filling

1. Extract form fields: `python scripts/analyze_form.py input.pdf` → `form_fields.json`
   (every field name, type, and whether it's required)
2. Create `field_values.json` mapping each field name to its intended value
3. Validate: `python scripts/validate_fields.py form_fields.json field_values.json`
   (checks names exist, types are compatible, required fields present)
4. If validation fails, revise `field_values.json` and re-validate
5. Execute: `python scripts/fill_form.py input.pdf field_values.json output.pdf`
```

Step 3 is the whole pattern — a validator that checks the *plan* against the *source of truth*
before anything is written. Without it, this is just a checklist.

## Workflow checklists for complex tasks

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

## Feedback loops

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

## Avoid time-sensitive information

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

# Examples

Complete skills showing these patterns and the frontmatter flags from
[frontmatter-reference.md](frontmatter-reference.md).

## Minimal reference skill

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

## Task skill with subagent isolation

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

## Safe deploy skill (user-only invocation)

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

## Skill with dynamic context injection

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
