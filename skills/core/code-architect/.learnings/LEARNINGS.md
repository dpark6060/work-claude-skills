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

## 2026-10-19 | Priority: MED | Status: OPEN
**Area:** detail mode, vendoring across sessions
**Summary:** When step N vendors shared models and step N+1 vendors the code that fills them, check both come from the same upstream commit.
**Details:** 4dv-archive-import session 1 vendors models.py from the validator's unmerged 2.0.0 branch, but design.md let session 2 fall back to 1.0.0, whose archive_db/archive_source populate fields 2.0.0 deleted. Caught by `git diff main..HEAD -- models.py` in the source repo. Also: an untracked same-named target dir (stale `__pycache__`) makes `git mv a b` nest `a` inside `b`; check the target path before a rename task.
**Action taken:** Pinned the vendor commit in the session doc and raised the fallback as a question.

## 2026-11-03 | Priority: MED | Status: OPEN
**Area:** detail mode, design.md that already carries signatures
**Summary:** When design.md lists both a dataclass's fields and the signature of the function that builds it, check every output field is derivable from the inputs before copying the signature into the session doc.
**Details:** 4dv-archive-import rev h gave `get_missing_files(manifest, placements) -> tuple[MissingFile, ...]` while `MissingFile` carries `archive_root`, which neither `ArchiveManifest` nor an empty `placements` tuple holds. Also: a design that says "subject = Patient.PID" without saying what a blank PID does leaves the session doc to pick raise-vs-default; raise (archive ERROR via the per-archive try) was the only choice consistent with the FileStatus set.
**Action taken:** Added the parameters in the session doc, recorded as an assumption, flagged for reconcile.

## 2026-11-03 | Priority: MED | Status: OPEN
**Area:** detail mode, a step outline that says "keep X" from a PoC
**Summary:** Before planning to "keep" a PoC helper the outline names, rg the repo for its behavior under another name; and when wiring a write step, check whether an earlier step already passes `dry_run` into the producer.
**Details:** v7-export-from-fw step 9b outline said "keep `storage_key_for`"; it already existed as `report._get_storage_key` (landed in step 8) and every `ExportedFile` carried the key, so a registrar-side copy would be dead code. Separately, step 5 had wired `submit_export(..., dry_run)` through, so a dry-run export produced a report whose keys never landed; the register call needed its own `config.dry_run` gate in 9b even though the dry-run output is step 11's. Also: `v7.py` had been added by an out-of-sequence ticket with no module-map row, which settled "new module vs. fold into v7.py" (folding changes the map, which detail must not do).
**Action taken:** Dropped `storage_key_for`, added the gate, recorded both as assumptions and flagged the module-map drift for reconcile.

## 2026-11-04 | Priority: MED | Status: OPEN
**Area:** detail mode, naming the target of a write
**Summary:** Don't address a write by a value the pipeline derived (e.g. a V7 item name split from an export dst_path); use the identifier the system of record just returned.
**Details:** v7-export-from-fw session 10 planned `set_acquisition_file_info(acq_id, linkback.item_name, ...)`. item_name came from the export template's leaf, so a template that renamed the leaf would write to the wrong (or no) Flywheel file. Implementation used `get_file(id).name` instead. Also for reconcile: design.md has space-padded markdown tables; a short script that splits on `|` and `ljust`s the cell keeps alignment where a hand Edit would not.
**Action taken:** Recorded as a plan deviation in the step-10 reconcile note.

## 2026-11-05 | Priority: MED | Status: OPEN
**Area:** detail mode, smart session doc template
**Summary:** The smart template in multistep.md has no blank line after its headings or before its list/fence bodies; copied literally it fails markdownlint MD022/MD031/MD032 (the disable line only covers MD013/025/040/041).
**Details:** 4dv-archive-import step 4 verification run; the mdlint hook rejected the first write with 17 findings. Also: SDK 22 upload accepts `metadata` with `info`, which would make upload + `info.4dv` one call and close the crash gap where an un-stamped file reads as CONFLICT on rerun.
**Action taken:** Added blank lines in the doc; template itself not edited (out of scope for the run).

## 2026-11-05 | Priority: MED | Status: OPEN
**Area:** detail mode, write-then-stamp sequences
**Summary:** When a design's rerun convergence depends on a stamp written after the upload, check the gap between the two calls.
**Details:** 4dv-archive-import step 4 (dumb verification run) uploads, then calls `set_4dv_info`. A crash in between leaves an unstamped file, and REQ-18 turns that into an acquisition CONFLICT on rerun, so the design's "rerun converges" claim fails exactly in the crash window it was written for. Also: the design's `get_file_archive_ids -> dict[name, archive_id]` can't feed `SKIPPED` entries, which need a file id. When re-detailing a step that already landed, read the code at the pre-step merge commit (`git show <sha>:path`), not HEAD.
**Action taken:** Recorded both as assumptions for reconcile; return type widened to `(file_id, archive_id)`.

## 2026-07-22 | Priority: LOW | Status: RESOLVED
**Area:** tooling
**Summary:** `.learnings/*.md` are dot-dir files; Glob `.learnings/*.md` returned nothing but the files existed.
**Details:** Check with the exact path / `ls` for dot-directories rather than trusting a glob miss.
**Action taken:** Read the files directly before appending.
