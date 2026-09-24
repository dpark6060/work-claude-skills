# LEARNINGS

Patterns that worked, non-obvious behaviors, workflow adjustments. Append-only; newest first.

## 2026-09-22 (fwv-0922-6a21) — running a gear over a fixed case set, alatest

- **Resetting a gear's own metadata is three deletes, and the third has a trap.** Verdict
  tags come off with `fw.delete_file_tags(id, body=[tag])`; a top-level info key with
  `fw.get_file(id).delete_info(key)`. A *nested* QC namespace has no delete path — the API
  deletes fields, not paths. Read `info["qc"]`, drop the namespace, and
  `update_info({"qc": remaining})`: the set-info endpoint replaces each top-level key it is
  given, so writing a rebuilt `qc` removes the namespace while leaving other top-level info
  alone. When `qc` ends up empty, `delete_info("qc")` instead — do not write `{"qc": {}}`.
- Back up `tags` + full `info` per file to JSON before any reset. It costs one extra
  `get_file` per file and makes the whole operation undoable.
- `fw.gears.iter_find()` yields the SAME gear document ~140 times on this site (the /gears
  pagination cursor bug). Deduplicate on `gear.id` before counting versions, or you will
  report a gear as having 140 versions.
- **A gear that resolves its file's parents must guard every level for None.** A trigger file
  on a session/subject/project has `parents.acquisition is None`, and
  `client.get_acquisition(None)` raises `ValueError: Missing the required parameter
  acquisition_id` *client-side*, before any HTTP call — so it does not look like an API
  error in the log. Found live in 4dv-archive-validator 1.0.0-rc5: the crash happens in the
  first line of the write phase, so the job dies with no tag and no QC result written at all.
  When a gear declares project/subject/session/acquisition levels, test at least one non-
  acquisition parent.
- Old test data encodes old gear behavior. A file sitting in a `quarantine` container is a
  *fixture of the previous build*, not a neutral starting state — it is exactly the input
  shape the new build never anticipated. Check where each case file actually lives before
  assuming the case set is uniform.

## 2026-09-22 (fwv-0922-022b) — tag and nested-QC filters on `/files`, SDK 22.0.0, alatest
- `fw.files.find("tags=<value>")` is a real exact match against one element of the tag
  array. Value may be quoted or not; hyphens need no escaping; case-sensitive. Works
  site-wide with no parent scope. `tags=~<pattern>` matches a tag family — but quoting
  a `=~` value still silently returns 0.
- **A deeply nested `info` path with hyphens AND a leading digit filters fine written
  bare**: `info.qc.4dv-archive-validator.4dv-validation.outcome=PHI_HIT` returned exactly
  the one matching file. Every attempt to protect the segments — double quotes, single
  quotes, `[brackets]`, `\-` escapes, quoting the whole path — silently returned 0. The
  rule is: quote the VALUE if you like, never the KEY PATH.
- A filter on an intermediate path that resolves to an OBJECT returns 0
  (`info.qc=~.` -> 0) while the scalar leaf under it returns the full set
  (`....outcome=~.` -> 6). Key-exists probes only work on scalar leaves — do not read a
  zero on an object path as "the key is absent".
- `fw.acquisitions.find("parents.project=<pid>,files.tags=<tag>")` parses and returns a
  plausible-looking non-zero count that is WRONG (2 acquisitions for 3 matching files).
  `file.tags=` on the same finder returns 0. Filter files with `fw.files`, not with a
  child-file join off a container finder.
- `tags.0=<value>` returned the correct set even for files whose matching tag is not
  first — it is not really positional. Don't build on it.
- Ground-truth-first pays off: the fixture project carried 15 unrelated tags from other
  gears, so a filter that silently matched everything would have been visible in the
  counts rather than passing as CONFIRMED.

## 2026-09-22 (fwv-0922-d487) — smart copy endpoints, gear-rule keys, alatest
- Smart copy and "copy by reference" are the same thing: `POST
  /{projects|subjects|sessions|acquisitions}/{id}/copy`. Container copies return the
  new container synchronously; project copy returns `{task_id, snapshot_id,
  project_id}` and takes `group_id`+`project_label`. Copied files carry a `copy_of`
  block (source file_id/version/parents).
- **`filter` is a REQUIRED body field on all four copy endpoints.** Omit it and you
  get a bare `422 invalid_request` (`loc=["body","filter"]`) raised before any
  permission check — a probe that reports that as a permission failure is wrong. An
  operator-key control call is the cheapest way to pin a call's body shape before
  reading a 4xx as a verdict.
- The generated SDK exceptions expose the useful detail only in `exc.body`;
  `exc.reason` is `None` on FastAPI validation errors. Log `body` in probe failure
  details or you learn nothing from a 422.
- Gear-rule key and copy: in-project copy PASSes at rule role admin and rw, 403 at
  ro; copy to ANY other project is 403 `containers_create_hierarchy` (checked on the
  DESTINATION) at every role; project copy is 403 "User does not have admin access to
  group" at every role, since a gear-rule key has no group access.
- The `copy_by_reference` RBAC action is carried only by the built-in admin role, but
  rw passed the copy without it — it does NOT gate these endpoints on this version.
  Do not infer capability from an action name matching an endpoint's summary.
- `fw.lookup("gears/<name>")` resolves to the newest version, which may not be the
  version a pinned (`auto_update=False`) rule spawns. A job finder keyed on the
  looked-up `gear_id` then never finds the rule's job. Read `rule.gear_id` and use
  that for both the finder and any baseline `gear.run`.

## 2026-09-14 (fwv-0914-5421) — gear-rule job keys, file-curator 1.0.6, alatest
- A gear-RULE job's `api-key` input is a project-scoped key: `/auth/status` returns
  `origin.type=gear_rule`, `origin.id=<rule id>`, `user_id=None`, `roles=["user"]`.
  It sees only the rule's project (`fw.projects()` → 1 entry, `fw.groups()` → 403),
  regardless of the rule's `role_id` (admin/rw/ro all identical on scope). The role
  governs ACTIONS inside that project only (ro → 403 `containers_modify_metadata`,
  `files_move`). Cross-project `move_file` is 403 `files_move` even when the role has
  the action — the check is on the destination container. Only site-wide read that
  passed: `fw.get_all_users()`.
- A user-launched job (`gear.run` with a user key) runs AS THAT USER inside the
  gear: `origin.type=user`, full site perms. That is the elevation direction to worry
  about, not rules.
- `PUT /files/{id}` with a `parents` body is 422 `extra_forbidden` for everyone;
  `POST /files/{id}/move` is the only re-parent path. Cross-GROUP move is 422
  "Destination container must be in the same group" for a site admin too.
- The job document's `origin` for a rule-spawned job is `{"type":"system","id":None}`;
  the finer `gear_rule` origin only shows up via `/auth/status` from inside the job.
- Gear rules: `GearRuleInput(role_id=..., triggering_input="file-input",
  fixed_inputs=[{"type":"project","id":pid,"name":fname,"input":"curator"}], tags=["static"])`
  via `fw.add_project_rule(pid, body)`; swap role with `fw.modify_project_rule(pid,
  rule_id, GearRuleModifyInput(role_id=...))`. Rule fires on upload when the type is set
  in upload `metadata={"type": "pfile"}` — no separate type-set step needed. Pickup on
  static engine ~15-25 s per run.
- `fw.jobs.find("destination.id=<acq>")` returns nothing; filter `gear_id=` with
  `sort="created:desc"` and match `job.destination.id` in Python.
- file-curator 1.0.6 image has NO `requests` and NO `urllib3`; raw HTTP from a curator
  must go through `fw.api_client.call_api(path, "PUT", path_params=..., body=...,
  auth_settings=["ApiKey"])`. In-image SDK was 22.3.0 (no `flywheel.__version__`; use
  `importlib.metadata.version("flywheel-sdk")`).
- Audit trail ON on alatest: `delete_file` without `delete_reason=` is 400. Re-upload a
  changed curator under a NEW filename and repoint the rule's `fixed_inputs` (the stored
  entry pins `version: 1`).

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

## 2026-09-14 (fwv-0914-1d55) — `project.permissions` is RBAC (`RolePermission`), not `AccessPermission`, on SDK 22.0.0 / alatest
- `project.permissions` entries came back as `RolePermission(id, role_ids: list[str])`
  — **no `.access` field**. `AccessPermission(id, access: AccessLevel)` (the
  `ro`/`rw`/`admin` string shape) exists as an SDK model but is NOT what this
  instance returns. Resolve `role_ids` through `fw.get_role(role_id)` to a
  `RoleOutput` carrying `actions: list[Action]` (58 granular enum values, e.g.
  `Action.FILES_MOVE`) and, only on the 3 built-in default roles,
  `default_flywheel_role` (`admin`/`ro`/`rw`). Custom roles (this instance had
  4) have no `default_flywheel_role` — a writability check that only reads
  that field misjudges every custom-role permission. Check a specific `Action`
  in `role.actions` instead.
- `client.lookup(path)` on a miss RAISES `ApiException(404)`, never returns
  `None` — confirmed live and by source (`flywheel.py:4776` `lookup_path()` has
  no except/fallback). The `reason` string distinguishes "group exists,
  project doesn't" from "group doesn't exist" (`'No match for project with
  label X'` vs `'Could not find resource group:X'`).
- `move_file(file_id, FileMoveInput(container_reference=ContainerReference(type="project", id=...)))`
  is the only file-move endpoint (`POST /files/{file_id}/move`). Confirmed:
  `tags` and `info` survive byte-identical, `file_id` is unchanged (re-parents
  the same doc), return type genuinely matches the declared `ModifiedResult`
  (`{jobs_spawned, modified}` — not otherwise useful to a caller).
- `delete_file_tags(file_id, body=[tag])` on a tag the file does not carry is
  a confirmed no-op (returns `None`, raises nothing) — safe to call
  unconditionally with no `try/except`.
- **A root/site-admin key cannot be used to test "absent from
  `project.permissions`".** Scanned every one of 48 projects reachable on
  alatest and the root key's id was present in every one's `permissions`,
  including projects it never created. Testing that branch needs a
  deliberately unprivileged second key — record REFUTED-untestable rather
  than trusting a root key's view as representative of a scoped key.
- `fw.add_group`/`fw.delete_group` work fine for a fully scratch group (not
  just projects within a shared config-driven group) — useful when a task
  explicitly asks for a disposable group rather than reusing config's
  namespace group. Cleanup must delete group after both its projects, and
  `fw.get_group(id)` after delete confirms 404 rather than trusting the
  delete call's lack of an exception.
- `source.update_file_info(filename, dict)` (the container-scoped
  `_invoke_file_api("set_{}_file_info", ...)` convenience method) works;
  the raw `fw.modify_file_info(file_id, body=dict)` wrapper is BROKEN on
  22.0.0 — raises `AttributeError: module 'flywheel.models' has no attribute
  'object'` before ever making the HTTP call, because the swagger codegen
  mistranslated an untyped `object` body type into a bogus model lookup. Use
  the container convenience method instead of the raw client method for info.

(Reset 2026-08-06 after integrating all prior entries into SKILL.md, the mode
references, and script docstrings.)
