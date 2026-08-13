# LEARNINGS

Patterns that worked, non-obvious behaviors, workflow adjustments. Append-only; newest first.

## 2026-08-13 (fwv-0813-a6eb) — `=~` regex filter semantics, SDK 22.0.0, sse-latest-azure
- `=~` is an UNANCHORED, case-sensitive regex substring match. Not prefix-anchored,
  not full-match. `^`, `$`, `.*`, alternation `(a|b)`, char classes `[...]`,
  negated classes `[^-]` all parse and evaluate server-side.
- `.` IS a wildcard; `\.` correctly restricts to a literal dot AND still matches.
  Prefix-boundary-safe form (verified): `^<re.escape(prefix)>(/|$)` — matches
  `<prefix>` and `<prefix>/...`, rejects `<prefix><extra-chars>`. Proven with
  real-data proxies (`^Archive1_Normal(/|$)`=0 vs `^Archive1_Normal`=62).
- **QUOTING A `=~` VALUE SILENTLY RETURNS 0.** `info.x=~"pat"` → 0, `info.x=~pat`
  → 62. FinderBehaviors.md's "direct filters MAY be quoted" does NOT extend to the
  regex operator. Same for nested ints: `info.4dv.source_size="8942"` → 0 vs
  `=8942` → 2. Exact match against `""` also returns 0 even when a file has it.
- Unescaped `,` in a pattern is the ONE loud failure: 400 "Cannot parse ... as a
  filter expression" or 500. `\,` works. `re.escape()` output (`\ `, `\-`, `\.`,
  `\,`) is fully accepted by the server engine — always `re.escape()` interpolated
  prefixes.
- `Finder.find()` semantics (finder.py:154-168): NO `limit` kwarg → delegates to
  `iter_find` and pages the WHOLE set; an explicit `limit=` → exactly one page,
  silently truncated. Verified directly on a 289-file project: `find(filt)`=289/289,
  `find(filt, limit=250)`=250. So "does find() truncate past 250" depends entirely
  on whether the caller passed a limit — check the call, not just the version.
- `page` is 1-BASED: `page=0` and `page=1` serve the same first page. A 0-based
  ground-truth paging loop double-counts page 1 (got 200 rows / 150 unique).
- Reusable trick for "is char X allowed in the pattern": build the probe so the
  special char is OPTIONAL (`X?`) or one arm of an alternation, so a correct parse
  still returns the known baseline count and a broken parse returns 0. Testing a
  special char with a pattern that should match nothing is useless — 0 is also
  what a parse failure gives.
- Use the TARGET REPO's venv interpreter, not `uv run --with`, when the claim is
  about the version the repo actually pins.

## 2026-08-13 (fwv-0813-0634, addendum) — the /files truncation is VERSION-BOUND
- The iter_find first-page truncation below affects flywheel-sdk <= 20.1.4 only.
  Fixed in 20.3.0: finder.py gained `if "file_id" in results[-1]: after_id =
  results[-1].file_id`. Confirmed empirically: 22.3.0 with limit=40 yields 150/150
  on the same fixture. Always re-check a refuted-adjacent finding against the
  LATEST SDK before reporting it as a live bug.
- `uv run --with flywheel-sdk` can resolve a stale cached version and call it
  latest (resolved 18.5.0 when PyPI latest was 22.3.0). Check PyPI's JSON API
  (`https://pypi.org/pypi/flywheel-sdk/json`) for the true latest, or pass
  `--refresh-package flywheel-sdk`.

## 2026-08-13 (fwv-0813-0634) — /files finder behaviors, SDK 18.5.0, sse-latest-azure
- `GET /files` (`fw.files`) DOES inflate `info` on results — unlike container
  finders. Verified byte-identical to reloaded ground truth.
- `fw.files.find()`/`iter_find()` silently truncate to the FIRST page: iter_find
  cursors with `results[-1].id`, but `FileOutput.id` is a UUID while the endpoint's
  `after_id` wants the Mongo `file_id` — the bad cursor returns an empty page and
  iteration stops. Add /files to the "prove termination AND coverage before
  trusting iter_find" list next to /gears. Coverage check: compare against
  `PageFileOutput_.total` via `get_all_files(_ignore_simplified_return_value=True)`.
  Page-based paging (`page=1..n`) works correctly.
- A finder run that returns a complete set on a small fixture proves nothing about
  pagination — force `limit=` below the known ground-truth count to test it.
- /files filter fields: `parents.project=` works (unquoted); `name=` works;
  `_id`/`id`/`file_id` all silently return 0 in every quoting form.

(Reset 2026-08-06 after integrating all prior entries into SKILL.md, the mode
references, and script docstrings.)
