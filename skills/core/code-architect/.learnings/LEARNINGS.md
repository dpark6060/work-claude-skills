# code-architect Learnings

Observations from real runs. Summarize this file at session start — don't just read it.

## Format

```
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: OPEN/RESOLVED
**Area:** [which step or phase]
**Summary:** [one line]
**Details:** [what happened]
**Action taken:** [what was changed, if anything]
```

---

<!-- Add entries below as they accumulate -->

## 2026-07-22 | Priority: HIGH | Status: RESOLVED
**Area:** Step 2 — resolving a self-contradictory constraint
**Summary:** "Component X is in the pure package AND has no SDK dependency" resolves via an injected Protocol + a wiring-layer adapter.
**Details:** NFR-3 listed placers as part of the SDK-free logic package while placers must call the SDK. Resolution: placers depend on a `Gateway` protocol defined in the pure package; the SDK-backed `SdkFlywheelGateway` lives in the wiring subpackage. (First draft over-did it — split read/write into two protocols and used a second top-level package; review trimmed both. See F2/F6 entries below.)
**Action taken:** Documented as the top design decision + Assumption 1.

## 2026-07-22 | Priority: HIGH | Status: RESOLVED
**Area:** Step 2 — reviewer caught a boundary leak I rationalized away
**Summary:** Putting the db finalize (commit) inside the pure placer created a real signature gap (FLYWHEEL needs the trigger file_id/source acq, which only run.py has) — I'd flagged it as "structural interpretation" instead of fixing it.
**Details:** The clean rule was "input-artifact writes belong to run.py." Finalize touches the input artifact in FLYWHEEL, so it belonged in run.py all along. I bent the rule to keep finalize in the placer for symmetry. Reviewer's F1 was right: moving finalize to run.py (post-SUCCESS) fixed the signature, crisped the split, AND collapsed the placer to one hook.
**Action taken:** Moved finalize to wiring/finalize.py; made it idempotent (F3). Lesson: when I write "structural interpretation, not a deviation" in a risk note, that's usually a leak to fix, not annotate.

## 2026-07-22 | Priority: MED | Status: RESOLVED
**Area:** Step 2 — NFR "decoupling" != separate distributable package
**Summary:** I satisfied "SDK-free logic" with a second top-level package; a subpackage + import-linter contract + sys.modules test is the cheaper, SSE-standard way.
**Details:** Two hatchling packages muddied publish/chain-import and broke the skeleton layout. The guarantee is enforceable as a CI gate (import-linter + a one-line sys.modules test) while keeping one package. Buy purity with a lint gate, not with packaging.
**Action taken:** Collapsed to one package with a wiring/ subpackage; added .importlinter + purity test task.

## 2026-07-22 | Priority: MED | Status: OPEN
**Area:** Step 2 — error/exit strategy for multi-terminal gears
**Summary:** Prefer a single result object + Outcome enum over an exception hierarchy when the "aborts" are expected outcomes.
**Details:** PHI-hit/incomplete/non-4dv/conflict/dry-run are anticipated, not exceptional. A `PipelineResult` keeps the pipeline a total function, makes every branch a value-assert in tests, and centralizes the outcome→side-effect map in run.py. Exceptions reserved for real bugs.
**Action taken:** Chose result object; documented the rejected exception approach.

## 2026-07-22 | Priority: LOW | Status: RESOLVED
**Area:** tooling
**Summary:** `.learnings/*.md` are dot-dir files; Glob `.learnings/*.md` returned nothing but the files existed.
**Details:** Check with the exact path / `ls` for dot-directories rather than trusting a glob miss.
**Action taken:** Read the files directly before appending.
