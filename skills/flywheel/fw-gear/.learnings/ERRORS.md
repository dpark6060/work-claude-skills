## Errors — fw-gear skill

Format:
```
## [YYYY-MM-DD] | Priority: HIGH/MEDIUM/LOW | Status: OPEN/RESOLVED
**Area:** <section of fw-gear>
**Error:** <what went wrong>
**Root cause:** <why it happened>
**Fix:** <what the correct pattern is>
```

---

<!-- Append new entries below this line -->

## [2026-06-10] | Priority: HIGH | Status: RESOLVED
**Area:** Skeleton template rename
**Error:** After renaming `fw_gear_skeleton/` to the new package name, the in-Docker editable install failed: hatchling "no directory that matches the name of your project", and gearcheck CRIT'd on .dockerignore.
**Root cause:** The skeleton's `.dockerignore` excludes everything (`**`) and allowlists `!fw_gear_skeleton` by name — the renamed package dir never reaches the Docker build context.
**Fix:** Update `.dockerignore` to `!<new_package_dir>` (and `!tests` if the CI pytest hook builds the dev stage). Also note: the skeleton pins `pytest<7`, which breaks at import time (`_pytest.scope`) once fw-client/httpx pulls in anyio's pytest plugin — bump to `pytest>=8`.

## [2026-05-07] | Priority: HIGH | Status: RESOLVED
**Area:** Accessing the Destination Container (gear-basics.md)
**Error:** Code used `context.destination.id` to access the gear's destination container ID. This raises `AttributeError` at runtime — `GearContext` has no `destination` attribute, and the destination is a dict, not an object.
**Root cause:** Confusion with the older `flywheel-gear-toolkit` API and/or assuming the destination is an SDK container object. `destination` lives on `context.config` and is the raw dict from `config.json`.
**Fix:** Use `context.config.destination["id"]` (or `.get("id")`). For the SDK container object, use `context.config.get_destination_container()` (requires api-key input). NEVER write `context.destination` — it does not exist.
