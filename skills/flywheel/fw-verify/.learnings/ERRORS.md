# ERRORS

Failures, wrong assumptions, and how they were fixed. Append-only; newest first.

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
