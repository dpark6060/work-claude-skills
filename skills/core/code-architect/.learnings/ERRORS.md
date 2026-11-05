# code-architect Errors

Failures and how they were fixed. Summarize this file at session start — don't just read it.

## Format

```
## [YYYY-MM-DD] | Status: OPEN/RESOLVED
**Step:** [which step failed]
**What went wrong:** [description]
**Root cause:** [why it happened]
**Fix applied:** [what changed]
```

---

<!-- Add entries below as they accumulate -->

## 2026-11-03 | Status: RESOLVED
**Step:** detail 3, 4dv-archive-import — guard-vs-pass-through for unlabelable rows
**What went wrong:** The rev h session doc made a blank PID, an unparseable `FileName` and a rowless manifest raise `FourdvError` (archive ERROR). The user reversed all three the same day: the design's stated process was "problems are logged and the run carries on", and a mapping that refuses an archive is a gate the design had just removed.
**Root cause:** I picked the raise because the `FileStatus` set had no "unplaceable" value, treating the enum as the constraint instead of the design's "no gate" decision. The right move was pass-through (literal label, row dropped to leftovers, fallback labels) and recording it as an assumption.
**Fix applied:** Rev i session doc flips all three; new rule of thumb: when a design says "trust the process", a missing enum value is a reason to not need a status, not a reason to raise.

## 2026-07-22 | Status: OPEN
**Step:** Session-doc sync — a task that required a file rename (`mv`/`git mv`)
**What went wrong:** Told to rename `session-07-finalize-entrypoint.md` → `session-08-...`. My tool set was Read/Edit/Write/Glob/Grep only — no Bash — so I couldn't move or delete a file.
**Root cause:** Write can create a new path but cannot delete the old one; no rename primitive exists without Bash.
**Fix applied:** Wrote the new correctly-named file, then overwrote the old file with a one-line tombstone pointing to the new name and flagged it for manual deletion. Note for future runs: when a dispatch assumes Bash (`mv`, `rm`, `git mv`) and it's not in the tool set, surface the limitation and leave a tombstone rather than silently leaving a stale duplicate.
