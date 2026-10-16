---
type: Reference
title: "Code Review Mode: conformance"
description: "Standards conformance review: walk the coding standards against changed code and return a numbered violation list citing each rule's anchor."
---

# Mode: conformance

Did this code follow the standards?

Walk general-coding.md (and unit-tests.md when tests changed) section by section against the
changed code. Every violation is a finding, style included. No verdict, no approval bar, and no
findings that aren't a rule violation.

## Output

```
## Conformance Review: [file or feature name]

1. `path.py:LINE` — [rule heading](~/.claude/skills/shared/coding/general-coding.md#anchor)
   [What the code does, quoted, and what the rule requires instead.]

[Repeat for each violation]

### Pre-existing issues (not in scope)
[One line each.]
```

Cite each rule by its section anchor so the fixer can read the exact rule. If nothing violates a
rule, say "No violations."
