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

## [2026-05-07] | Priority: HIGH | Status: RESOLVED
**Area:** Accessing the Destination Container (gear-basics.md)
**Error:** Code used `context.destination.id` to access the gear's destination container ID. This raises `AttributeError` at runtime — `GearContext` has no `destination` attribute, and the destination is a dict, not an object.
**Root cause:** Confusion with the older `flywheel-gear-toolkit` API and/or assuming the destination is an SDK container object. `destination` lives on `context.config` and is the raw dict from `config.json`.
**Fix:** Use `context.config.destination["id"]` (or `.get("id")`). For the SDK container object, use `context.config.get_destination_container()` (requires api-key input). NEVER write `context.destination` — it does not exist.
