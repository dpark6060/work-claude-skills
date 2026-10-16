---
type: Reference
title: "Code Review Mode: mr"
description: "Merge-readiness review: approval bar, non-starters, category-to-severity pyramid, review-judgment checks, security and conditional checks, and the verdict output format."
---

# Mode: mr

Is this change ready to merge?

**Approval bar:** approve once the change definitely improves overall code health, even if it
isn't perfect.

## Non-starters

Check these first. If any is present, report it as the first finding and review no further than
needed to show it:

- Unrelated changes mixed together, or a large refactor combined with a feature
- Debug code or commented-out blocks left throughout
- Hardcoded secrets or a committed credentials file (`.env`, `secrets.json`)

## What to look for, in priority order

Functionality and design are what block a merge; clarity issues warrant requested changes;
tests, docs, and style are clean-up that can follow.

| Category | Question | Severity range |
|---|---|---|
| 1. Functionality | Does it work? | Critical, Major |
| 2. Design | Is this the right approach? | Critical, Major |
| 3. Clarity | Can someone maintain this? | Major, Minor |
| 4. Tests | Are the tests correct? | Minor |
| 5. Documentation | Is the context captured? | Minor |
| 6. Style | Is it consistent? | Nit |

Beyond the rules in the standards, check for what they cannot express:

- Does the code actually accomplish what the change set out to do?
- Solving a symptom instead of the real problem
- A change in the wrong architectural layer, or one that bypasses an existing abstraction
- Excess coupling, or responsibilities landing on the wrong methods/classes
- Inputs the docstring or schema declares valid that the body mishandles
  (`restrict_to_keys=None` documented as "all keys", body iterates `None`)
- State mutations that happen in the wrong place or at the wrong time
- Concurrency or ordering assumptions that don't hold
- Something you had to work out because the code didn't say it. That is a Clarity finding;
  the explanation belongs in the code, not the review.
- A duplicated block, or a line whose indentation disagrees with its neighbours (the signature of
  an edit made without reading the function)
- Unrendered template placeholders (`{{gear_package}}`)

**Tests** are reviewed for correctness only: they exercise the change, fail when it breaks,
survive an internal refactor, and follow unit-tests.md. Never ask for more coverage.

**Security quick check:** input validation at system boundaries, no command injection
(`subprocess` with `shell=True` or a string built from input), no secrets in plain fields that a
`model_dump` or log line will print.

**Conditional checks:**

- Dependency added: justified and version-pinned
- Flywheel gear changed: `manifest.json` version bumped
- API or SDK calls inside a loop over containers or files (N+1)
- Build, test or deploy behavior changed: README updated

## Output

```
## Code Review: [file or feature name]

### [Category]: [short title]
**[Severity: Critical | Major | Minor | Nit]**
[Specific finding. Quote the relevant code. Explain why it's a problem and what to do instead.]

---

[Repeat for each finding]

### Summary
- Critical (must fix before merge): N
- Major (should fix): N
- Minor (clean up when convenient): N
- Nits: N (do not affect the verdict)

### Verdict
[One of: Approve | Approve with minor fixes | Needs work | Major rework required]

### Pre-existing issues (not in scope)
[One line each. These do not affect the verdict.]
```

**Severity guide:**
- **Critical** — Correctness bug, or a structural violation that needs a rewrite rather than a tweak.
- **Major** — Real problem that will cause pain (testing difficulty, maintenance burden, likely bug vector) but doesn't require full rewrite.
- **Minor** — Readability, test or documentation issue. Correct it, but it doesn't block anything.
- **Nit** — Style. Listed, never counted toward the verdict.

If the code is genuinely good, say so clearly. "No significant findings" is a valid and useful
review outcome.
