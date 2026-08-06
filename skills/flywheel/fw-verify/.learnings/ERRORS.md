# ERRORS

Failures, wrong assumptions, and how they were fixed. Append-only; newest first.

## 2026-08-06 — live smoke ran on alatest; `latest` is still unreachable

`latest.sse.flywheel.io` still times out on 443 (curl exit 28). `sse-latest-azure.dev.
flywheel.io` (env `ALATEST_API`, release 22.3.9) answers and authenticates as
davidparker@flywheel.io, so `default_site` in `cache/config.json` points there and
`latest` is demoted to a named site. If a probe suddenly cannot reach the site, check
which of the two you are pointed at before debugging anything else.

## 2026-08-06 — file-classifier silently erases the classification the build just wrote

The first live build looked like a success and was not. On `fwv-0806-0002-example`:
`type == "dicom"` ✓, `modality == "MR"` ✓, `info.SeriesDescription == "T1w"` ✓, and
`classification == {}` ✗.

Mechanism: uploading `image.dcm` makes the site queue file-metadata-importer and
file-classifier. file-classifier owns classification and *replaces* it when it finishes
— it does not merge. Our placeholder DICOM has no readable header, so what it derives is
nothing, and it writes that nothing over the `Intent` we set seconds earlier. The file's
own `info.qc.file-classifier` records the run (`classification_not_set: true`,
`is_mr: true`), which is how the overwrite was traced.

**Root cause: the new project's own gear rules.** A project inherits the site's default
rules at creation, and those rules are what queue the gears. `build_project.py` now calls
`delete_project_rules` immediately after project creation, before any upload, and the
problem disappears at the source: a fresh stripped project spawns **zero** gear jobs, the
classification survives on the first attempt, and `image.dcm`'s `info` carries only the
`SeriesDescription` the spec asked for instead of the gears' `header` and `qc` keys. See
LEARNINGS.md for the before/after measurements.

The retry loop that was supposed to prevent this did not, because it read the value back
*immediately* after writing — before the gear had run — and returned on the first
confirm. **A read-back straight after a write proves nothing on a container that has
ingest gears pending.** Fixed first with `is_classification_durable`: sleep, read, sleep,
read again, and accept only when both delayed reads agree; up to 4 write attempts. A fresh
build (`fwv-0806-0003`) then took ~32s and `classification.Intent == ["Structural"]`
survived, re-verified after the fact. That treats the symptom — the rule strip above
removes the cause — and it stays in place as a safety net for a site whose rules fire
independently of the project's, or a key that cannot remove them.

## 2026-08-06 — `fw.gears.iter_find` never terminates; `delete_gears` hung forever

The Task 6 warning was right. `cleanup.py --dry-run` produced no output for five minutes
and had to be killed. The generic `Finder` pages with `after_id = results[-1].id` and
`/gears` ignores it, so the endpoint keeps re-serving the same page: a bounded probe
pulled 3000 gears of which **250 were unique** and showed no sign of stopping. In a real
(non-dry) run this would have re-deleted the same gears in a loop.

`fw.get_all_gears(all_versions=True)` returns the whole list in one request — 1081 gear
versions on the test site, 130 without `all_versions`. `delete_gears` now uses that, and
a dry run finished in 7 seconds. There is a test asserting the Finder is never called,
because reaching for `fw.gears.iter_find` here is the bug and not a style preference.

Generalize: **do not assume a Finder works for an endpoint just because the SDK exposes
one.** `fw.projects.iter_find` is fine; `fw.gears.iter_find` is a hang. Prove termination
on a new container type before trusting it in a delete path.

## 2026-08-06 — finder results omit `info` and `classification`; you must `.reload()`

`fw.subjects.find_first(...)` came back with `info == {}` and the acquisition's file with
`info == None`, which reads exactly like "the metadata never got written". It was written.
List endpoints return a projection without `info`/`classification`; `.reload()` (or
`fw.get_subject(id)`) fetches the full container. Cost an entire wrong diagnosis — verify
metadata only on a reloaded container.

## 2026-08-06 — group 404, audit-trail delete reason, modality-before-classification

Three live-run failures fixed in `5bdc16c`:

- **Missing namespace group.** A site that has never run fw-verify has no `fw-verify`
  group, so `fw.get_group` 404s as a raw `ApiException`. `get_or_add_group` now creates it
  on 404 via `fw.add_group(flywheel.GroupInput(id=..., label=...))` and re-fetches, since
  `add_group` returns an id and not the container. Any other status re-raises — a 403
  means the key cannot read groups, which a create attempt would only obscure.
- **Deletes need a reason.** With audit-trail enabled the site answers 400 "Need to have
  delete reason while audit-trail is enabled". `cleanup.py` always sends
  `delete_reason=flywheel.ContainerDeleteReason.TEST_DATA`; sites without audit-trail
  ignore it.
- **Classification is validated against modality.** Sending `Intent` to a file whose
  modality is unset gets 422 "Unknown modalities can only use the custom attribute", and
  changing modality clears classification. Order is load-bearing: type/modality first,
  then classification, then info.

## 2026-08-06 — first live smoke attempt blocked at the auth check

TCP 443 to `latest.sse.flywheel.io` times out from the workstation (`nc` and `curl`
both hang; DNS resolves to 35.202.85.112; the general internet is fine). `flyw` fails
the same way — `httpx2.ConnectTimeout: GET https://latest.sse.flywheel.io/xfer/version`.
`flyw auth status` still prints the site and user because that comes from cached local
config, not a live call — do not read it as proof of reachability.

Two consequences for the skill:

- The auth check in SKILL.md does its job: it fails in ~3 minutes at step 3 instead of
  halfway through a probe. Keep it. But it fails as a bare `httpx2.ConnectTimeout`
  traceback, which reads like a code bug rather than "you are not on the VPN".
- No live smoke ran, so every SDK-call assumption below is source-verified only.

## 2026-08-06 — SDK-call audit against flywheel-sdk 22.3.0 source (no live run)

All calls the scripts make match the installed SDK. Recorded so the next live run knows
what was already checked statically and what is still unproven:

| Call | Source finding |
|---|---|
| `flywheel.FileSpec(name, BytesIO, size=n)` | `__init__(self, name, contents=None, content_type=None, size=None)` — matches |
| `container.update_file(name, {"type": ...})` | `util.params_to_dict` accepts one positional dict; body becomes `FileModifyInput{type, modality}` — `type` is a real field |
| `container.update_file_info(name, d)` | wrapper wraps as `{"set": d}` — pass the raw dict, do NOT pre-wrap |
| `container.update_file_classification(name, d)` | wrapper wraps as `{"add": d}` — same, raw dict |
| `fw.gears.iter_find(all_versions=True)` | `fw.gears = Finder(self, 'get_all_gears')`; `get_all_gears` accepts `all_versions`, `limit`, `after_id` |
| `gear.gear.name` / `gear.id` | `GearDocument.gear` is a `GearManifest` (has `name`); `.id` exists |
| `fw.delete_project(id)` / `fw.delete_gear(id)` | both exist on the client |

Still unproven, and the two most likely first-live-run failures:

- **`get_or_add_project` on a site with no `fw-verify` group.** `fw.projects.find_first`
  returns None silently, then `fw.get_group(group_id)` 404s as a raw `ApiException` —
  not in `SETUP_ERRORS`, so the user gets a traceback instead of `Setup error: ...`.
- **`gears.iter_find` pagination.** The generic finder pages with
  `after_id = results[-1].id`. If `/gears` ignores `after_id`, `delete_gears` loops
  forever instead of terminating. Watch the first real cleanup that has gears to delete.
