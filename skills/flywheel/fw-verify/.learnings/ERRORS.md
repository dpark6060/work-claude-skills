# ERRORS

Failures, wrong assumptions, and how they were fixed. Append-only; newest first.

## 2026-09-14 (fwv-0914-5421)
- Curator `import requests` → `ModuleNotFoundError` in file-curator 1.0.6; then
  `import urllib3` → same. Fixed by using `fw.api_client.call_api` for the raw call.
  Cost two full job round-trips; check the image's module set before importing
  anything beyond the README's preinstalled list.
- `project.delete_file(name)` to replace a curator → `400 Need to have delete reason
  while audit-trail is enabled`, and the driver silently ran the OLD script. Fixed by
  revisioned filenames (`-r{N}.py`) and skipping delete entirely.
- `fw.jobs.find(f"gear_id=...", f"destination.id=...")` timed out finding the spawned
  job that plainly existed. `destination.id` is not a usable jobs filter.

## 2026-09-14 (fwv-0914-1d55)
- Called `fw.modify_file_info(file_id, body=info_dict)` expecting it to PATCH
  file info. It raised `AttributeError: module 'flywheel.models' has no
  attribute 'object'` from inside the generated client before any HTTP request
  — the swagger codegen's untyped `object` body type resolves to a model
  lookup that does not exist. Fixed by using the container-scoped convenience
  method instead: `project.update_file_info(filename, info_dict)`.
- Tried `fw.projects.find_first(f"group._id!={GROUP_ID}")` to find a project
  outside a scratch group. Finder query operators are `=` and `=~` only (per
  `FinderBehaviors.md`) — never assume `!=`/`<`/`>` are supported without
  checking; filter in Python over `iter_find()` instead.

(Reset 2026-08-06 after integrating all prior entries into SKILL.md, the mode
references, and script docstrings.)
