## Learnings — fw-gear skill

Format:
```
## [YYYY-MM-DD] | Priority: HIGH/MEDIUM/LOW | Status: OPEN/RESOLVED
**Area:** <section of fw-gear>
**Summary:** <one line>
**Details:** <what was observed>
**Suggested action:** <what to do differently next time>
```

---

<!-- Append new entries below this line -->

## [2026-06-10] | Priority: HIGH | Status: OPEN
**Area:** SDK client vs /xfer endpoints
**Summary:** `context.client` (flywheel SDK) cannot reach /xfer — build an FWClient from the api-key input instead.
**Details:** The SDK client is rooted at `/api`, so `/xfer/storages/...` style endpoints are unreachable through it, and it has no generic `.get(path)`. fw-client's `FWClient.get(path)` returns parsed JSON on success and raises an httpx-style `HTTPStatusError` (`err.response.status_code`) on non-2xx.
**Suggested action:** For gears calling non-/api services (/xfer, /snapshot), add `fw-client` as a dep and build `FWClient(api_key=...)` from the same api-key input (loop `context.config.inputs`, match `base == "api-key"`).

## [2026-06-10] | Priority: MEDIUM | Status: OPEN
**Area:** Job origin detection
**Summary:** `context.config.job` (populated when manifest has `custom.flywheel.show-job: true`) carries `origin.type` for user-vs-trigger detection.
**Details:** `job["origin"]["type"]` is `"user"` for manual launches and `"system"` for gear-rule launches (`"job"` for job-spawned). Best-effort: treat missing/None as unknown.
**Suggested action:** Keep `show-job: true` in the manifest when a gear needs to know how it was launched.

## [2026-06-10] | Priority: MEDIUM | Status: OPEN
**Area:** Connection URL parsing
**Summary:** Don't use `urllib.parse.parse_qs` on storage connection URLs — it decodes `+` as space, corrupting base64 credentials.
**Details:** S3 secret keys and GCP private keys routinely contain `+`. Split the query on `&`/`=` manually and use `unquote()` (which leaves `+` intact).
**Suggested action:** Reuse the `_get_url_params` pattern from storage-auth-test's main.py.

## [2026-07-09] | Priority: MEDIUM | Status: RESOLVED
**Area:** api-key input (gear-manifest.md)
**Summary:** `"read-only": true` on an api-key input is deprecated — always use the plain `{"base": "api-key"}` form.
**Details:** Confirmed by David. The gear-manifest.md reference used to present a read-only variant as "preferred when the gear doesn't write"; that guidance is stale. Updated the reference to say don't use read-only.
**Suggested action:** Never emit `read-only` on an api-key input, regardless of whether the gear writes back.
