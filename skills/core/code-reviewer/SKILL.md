---
name: code-reviewer
description: Reviews Python code for quality, correctness, and adherence to project conventions. Use this skill when the user asks to review code, check code quality, look for issues, or get feedback on an implementation. This is a code quality review — not an architecture review. For checking whether code follows an architecture plan, use code-architect-reviewer instead.
version: 1.3.0
---

You are conducting a code quality review. Your job is to find real problems — correctness issues, structural violations, and readability failures. Do not rubber-stamp code. Do not invent problems that aren't there. Be direct.

This skill covers code quality. It does not check plan compliance — that is `code-architect-reviewer`'s job.

## Step 1 — Determine What Changed

If the user provides a specific file, function, or code snippet, that is your review scope — skip to Step 2.

Otherwise, run `git diff HEAD` to get the diff. If the user specifies a base branch or SHA (e.g. "review against main"), run `git diff <base>...HEAD` instead.

From the diff:
- Note which files changed and which line ranges are new (`+` lines)
- For each changed hunk, use `Read` with `offset`/`limit` to pull the **full function or class** containing the change — not just the diff lines

This gives you enough context to evaluate rules that span a whole function — whether the logic is actually correct, single responsibility, nesting depth — which can't be judged from a few diff lines alone.

**Scope rule**: Only report findings on code that appears as `+` lines in the diff. If you spot a pre-existing issue in unchanged context lines, note it once at the end under "Pre-existing issues (not in scope)" — do not include it in severity counts or the verdict.

## Step 2 — Read the Rules

Read the rule files that apply to what you're reviewing:
- `~/.claude/skills/shared/coding/general-coding.md` — always
- `~/.claude/skills/shared/coding/functions.md` — if reviewing functions or methods
- `~/.claude/skills/shared/coding/classes.md` — if reviewing classes
- `~/.claude/skills/shared/coding/unit-tests.md` — if the diff touches tests

Do not rely on memory. Read them.

---

## What to Look For

Work through these in priority order — it mirrors the team's review pyramid in `CODE_REVIEW_GUIDE.md`. Functionality and design are what block a merge; clarity issues warrant requested changes; tests, docs, and style are mostly clean-up that can follow. Not every category will have findings — that's fine.

**1. Functionality — does it work?**
- Logic that fails on edge cases (empty input, None, unexpected types), including inputs the docstring or schema declares valid (`restrict_to_keys=None` documented as "all keys", body iterates `None`)
- Swallowed errors: `except Exception: ... return None`, bare `except:`, a function whose other paths raise or return an object falling off the end with `return`, a worker thread whose exception ends the thread and nothing else
- Log where the contract is to raise: a validator that logs the failure and continues, so the caller that depends on the raise never sees it
- Work skipped with no signal: a guard that refuses to write with no return value and no log; a per-value fallback that silently returns the input
- Validation that stops early: a per-item check gated on an accumulator (`if valid:` where `valid` spans prior items), continuing after a failed type check, `valid &= False`
- Validation that reaches the network, or recursion over user-supplied structure with no visited set
- An explicit argument overridden by an env var, global, or lookup tested before "was it passed?"
- `setattr` from parsed data; a flat dict passed into a nested pydantic model (keys dropped silently without `extra="forbid"`)
- Env vars used without conversion (`os.environ.get("X", 100)` is `int` unset, `str` set); `Path = None` instead of `Path | None = None`; a `str` where a set is expected (`exclude="fs"`); a scalar check (`pd.isna`, `[0]`) on a value that can be an array or a filtered Series
- Handles opened without a context manager (`fs.open(...).read()`, `sqlite3.connect`, `NamedTemporaryFile(delete=False)` never unlinked)
- Secrets in a plain field that any `model_dump` or log line will print
- An irreversible step (delete, move, publish) with fallible work after it, or rollback code instead of writing the commit file last
- State mutations that happen in the wrong place or at the wrong time
- Concurrency or ordering assumptions that don't hold
- Does the code actually accomplish what the change set out to do?

**2. Design — is this the right approach?**
- Solving a symptom instead of the real problem
- Change in the wrong architectural layer, or bypassing existing abstractions
- Excess coupling, or responsibilities landing on the wrong methods/classes
- Over-engineering for hypothetical future needs
- A constructor that fetches: network calls, filesystem builds, directory creation in `__init__` (the test file will be mock scaffolding)
- I/O at import time: `json.load` at module level, `warnings.filterwarnings` at module level, env reads in a constants module
- A read-sounding name that writes: `setup_paths` running `makedirs`, `infer_schema` mutating its DataFrame, a serializer nulling and restoring `self`
- A bool parameter that skips steps (`connect(first=False)`) or switches behaviour; that is two methods
- More than three mutually exclusive branches in one function; it is a dispatcher plus one function per branch
- Another object's `_private` attribute read or written from outside the class; a public accessor that exists and nothing calls
- One field holding different types depending on which code path filled it
- Call order between methods enforced only by a comment or a TODO
- A whole object taken as a parameter to read two fields from it at construction
- A module with no single theme (six unrelated concerns in one file); a function-local import added to dodge a cycle; a name imported through a re-export instead of from its definition
- A second implementation of something that already exists (an abandoned refactor, a passthrough with a copy-pasted docstring, the same file parsed in five places); a helper that exists and is reimplemented inline
- A function whose whole body calls another function and returns its result (`raw = _build_raw(ctx); return validate_config(raw)`); collapse the pair into one function
- Persisting inside the loop that mutates (`save()` per item)
- A relationship between names derived by string surgery (`name[:-1]` for the singular) instead of a declared mapping; one customer's schema or column names hardcoded in a general path (`if table == "participants"`)
- A sentinel that changes a field's meaning (`version == "latest"`) re-resolved in every consumer
- A dict API bolted onto a pydantic model (`get` without default, `__getitem__` via `getattr`); a method named after a framework method it shadows (`@model_serializer def model_dump`)
- Raw dicts where a dataclass or Pydantic model belongs (any dict whose keys are referenced by name); complex return values with no defined return type
- Machinery the requirement never asked for — a report builder, an aggregator, a summary, an extra status field. Ask which sentence of the requirement demands it; if there isn't one, it is a design choice and has to pay for itself
- Placeholders standing in for work that didn't happen, or a `skipped`-style flag that makes the object's other fields meaningless (a skipped check with `passed=True`)
- Work performed that a config flag turned off
- A structure whose shape changes with the count — a key promoted to the top level "when there's only one"
- The same fact recorded in two places (per-item problems flattened into a top-level list *and* kept in the item entries)

**3. Clarity — can someone understand and maintain this?**
- Methods that do more than one thing (AND/THEN test)
- Public methods carrying implementation detail instead of delegating to private helpers
- Nesting deeper than two levels
- Logic wrapped in an `if` block that should use an early return instead
- Names that don't convey what the thing is or does
- Two names in the same module that differ only by a plural or a suffix — the reader has to diff them to tell them apart
- A name whose meaning takes a sentence to explain; that sentence usually contains the better name
- A condition whose plain-English reading is absurd (`if not checkable: return VALIDATED` reads "if we could not check it, call it valid"), even when the surrounding logic is right
- A deliberate non-obvious choice with no inline comment saying why the obvious alternative was rejected
- An annotation that disagrees with the return (`-> Path` returning `bool`, `list[str]` returning `list[Path]`)
- One name used for unrelated functions across modules
- A parameter rebound to a different type partway through the function
- A `try` wrapping more than one call, or nested inside another `try`; a lookup chain or a conditional inside an f-string
- A swallowed exception without a named type, a one-call scope, and a one-line comment saying why ignoring it is correct

**4. Tests — will they catch regressions?**
- New or changed behavior is covered
- Tests fail when the code breaks and don't false-positive on an internal refactor
- Test names describe the scenario; assertions are simple
- Coverage level (unit/integration) matches the risk
- A test that asserts a method exists, is callable, or has a parameter in its signature, and never calls it
- A real method run against `MagicMock(spec=Class)` as `self`: every `self.x` is an auto-mock, so a non-existent attribute passes
- A call-count assertion that pins an inefficiency (an `Environment` rebuilt in a loop, `save()` per item)
- A fixture whose awkward value (the `None`, the empty list) sits where a naive implementation would not trip on it
- Two test names with one body; the untested branch is usually the default
- Tests for code with no callers; a coverage gate set below current coverage

**5. Documentation — is the context captured?**
- Missing or inadequate docstrings (all functions need them; complex ones need full Google-style)
- A docstring documenting parameters that do not exist, a default the body does not handle, or a return type the body does not produce
- Comments explain WHY, not WHAT; obsolete comments removed; TODOs reference a ticket
- Comments that narrate the edit: "removed", "previous", "was lines N-M", "OPTIMIZATION", "extracted", "STEP N", a comment restating the line below it, trailing initials, authoring markers
- A TODO that names a defect in the code it sits on
- Unrendered template placeholders (`{{gear_package}}`)
- A duplicated block, or a line whose indentation disagrees with its neighbours (the signature of an edit made without reading the function)

**6. Style / convention — is it consistent?**
- Missing or incorrect type hints
- Naming that doesn't follow conventions (`get_`, `is_`, `validate_`, etc.)
- Using a complex one-liner where readable multi-line code is clearer
- `print()` in library code; f-strings in log calls (use lazy `%` args); `log.error(msg)` followed by `log.exception(e)` for one event
- Unused imports, especially ones that make dead code look live
- A CLI (`argparse`) inside the importable package

---

## Output Format

```
## Code Review: [file or feature name]

### [Finding category]
**[Severity: Critical | Major | Minor]**
[Specific finding. Quote the relevant code. Explain why it's a problem and what to do instead.]

---

[Repeat for each finding]

---

### Summary
- Critical (must fix before shipping): N
- Major (should fix): N
- Minor (clean up when convenient): N

### Verdict
[One of: Approve | Approve with minor fixes | Needs work | Major rework required]

---

### Pre-existing issues (not in scope)
[List any issues spotted in unchanged code. These do not affect the verdict.]
```

**Severity guide:**
- **Critical** — Correctness bug, or a structural violation that needs a rewrite rather than a tweak.
- **Major** — Real problem that will cause pain (testing difficulty, maintenance burden, likely bug vector) but doesn't require full rewrite.
- **Minor** — Convention or readability issue. Correct it, but it doesn't block anything.

If the code is genuinely good, say so clearly. "No significant findings" is a valid and useful review outcome.

After delivering the review, write the full review report to `claude-work/code_reviewer/code-review.md` in the project root. Create the `claude-work/code_reviewer/` directory if it doesn't exist. This file is used by other skills (e.g. `jira-comment`) to summarize session work. See `~/.claude/skills/shared/output-conventions.md` for the full output directory convention.

Start the review file (and any copy written into the repo, e.g. `docs/reviews/`) with the line `<!-- markdownlint-disable MD013 MD025 MD040 MD041 -->` — repos gate committed docs with markdownlint in pre-commit, and review formatting legitimately violates those four rules. If the dispatch names a different output path, this line still goes first.
