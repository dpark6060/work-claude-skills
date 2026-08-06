# LEARNINGS

Patterns that worked, non-obvious behaviors, workflow adjustments. Append-only; newest first.

## 2026-08-06 — gear version discovery: `include_invalid` is mandatory, `disabled` is a timestamp

Mode 3 reuses one fixed-name gear (`claude-test-gear`) and uploads a new version per run,
deactivating it afterwards. That makes "what versions already exist?" a correctness
question, and the default answer is wrong.

`GET /gears` **hides deactivated versions** unless you pass `include_invalid=True`.
Measured live on 22.3.9:

| Query | Result |
|---|---|
| `get_all_gears(all_versions=True)` | 1081 |
| `get_all_gears(all_versions=True, include_invalid=True)` | 1124 |
| `filter="gear.name=dicom-qc"` | 11 versions |
| same + `include_invalid=True` | 16 versions (`0.6.0-rc0`…`rc4` were hidden) |

Since every run deactivates the version it used, the *visible* list is precisely the
list that excludes our own history — compute "next version" from it and you re-mint an
existing version and the upload fails. The verified discovery call is
`fw.get_all_gears(all_versions=True, include_invalid=True, filter=f"gear.name={name}")`,
wrapped as `get_gear_versions` in `cleanup.py`. Server-side filtering, so it returns one
gear's versions instead of all 1124, and `[]` for a name that has never been uploaded.

Two more traps in the same area:

- **`disabled` is a datetime or `None`, not a boolean.** All 43 hidden versions carried a
  disable timestamp; every visible one had `None`. `if gear.disabled:` is correct, but
  anything expecting `True`/`False` (a `== True`, a JSON dump, a schema) gets a datetime.
- **`fw.delete_gear` is a disable, not a delete.** Its own SDK docstring reads "Delete a
  gear (not recommended) / Disable a gear by id", and the 43 disabled-but-still-returned
  versions are consistent with that. Source-verified; not yet executed by this skill, so
  the first mode-3 run must confirm the version goes `disabled` rather than vanishing.

Naming note: manifest gear names allow only lowercase letters, numbers and hyphens, so
the gear is `claude-test-gear` and never `claude_test_gear`. The `[fwv-probe]` log prefix
in the template's `run.py` is deliberately left alone — it is a log namespace for
separating plumbing lines from `[fwv]` payload lines, not the gear name.

## 2026-08-06 — strip a new project's gear rules; otherwise the site rewrites your fixture

A new project inherits the site's default gear rules, so the first upload queues the
instance's own gears against it. On a stock site that is Metadata import then
file-classifier, and file-classifier *replaces* file classification when it finishes —
minutes or seconds after your write, whichever the queue decides. `build_project.py` now
calls `delete_project_rules` right after project creation, before anything is uploaded.

Measured on alatest (22.3.9), fresh project, same spec:

| | rules left in place | rules stripped |
|---|---|---|
| gear jobs spawned | 2 (Metadata import, file-classifier) | **0** |
| `classification.Intent` | wiped to `{}` | survives |
| `image.dcm` `info` keys | `SeriesDescription`, `header`, `qc` | just `SeriesDescription` |
| build wall-clock | ~32s (2 classification attempts) | ~20s (1 attempt) |

The fixture is now exactly what the spec asked for, with nothing the gears injected. That
matters for a verification skill — gear-added `qc`/`header` keys on a fixture can confound
the very claim you are testing.

Note the site still has two enabled *site-level* rules with those names. They did not fire
after the project strip, so on this site site rules are templates copied into each new
project's rule list rather than independent triggers. Do not assume that holds everywhere:
a site whose rules fire independently, or an API key that cannot remove project rules,
would put the race back. That is why `is_classification_durable` stays as a safety net
rather than being deleted — it costs ~12s per classified file and is the only thing that
would catch a clobber if the strip ever fails.

## 2026-08-06 — possible future improvement: poll ingest jobs instead of timed reads

Not implemented. A more deterministic alternative to `is_classification_durable`'s
delayed-read agreement: poll the file's own jobs (`fw.jobs.iter_find(f"parents.project=
{pid}")`, states `pending`/`running`) until none are active, then write metadata. That
replaces a statistical guess about how long a gear takes with a real terminal-state check.
Worth doing if rule-stripping ever proves insufficient; unnecessary while it holds, since
a stripped project spawns no jobs at all.

## 2026-08-06 — verify metadata only on a reloaded container

`fw.subjects.find_first(...)` returns `info == {}` and files with `info == None` even when
the metadata is there. List endpoints hand back a projection that omits `info` and
`classification`. Reading a finder result straight off looks exactly like "the write
didn't stick" and cost a whole wrong diagnosis. Call `.reload()` (or
`fw.get_subject(id)` / `fw.get_project(id)`) before asserting on metadata — in the skill's
own probes as much as in the build script.

## 2026-08-06 — painpoint: cleanup's gear scan is site-wide and slow

Gears have no group, so `cleanup.py` has to scan every gear on the site to find run-id
matches. `fw.get_all_gears(all_versions=True)` returns 1081 gear versions on alatest;
the sweep costs ~7s of the cleanup's runtime and grows with the site. Acceptable, but do
not put it in a loop, and never reach for `fw.gears.iter_find` instead — that one never
terminates (see ERRORS.md).
