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

## [2026-07-23] | Priority: HIGH | Status: OPEN (needs engine verification)
**Area:** context.metadata / .metadata.json (gear-metadata.md, metadata-capability-matrix.md)
**Summary:** OPEN QUESTION — does `context.metadata` need an `api-key` input in fw-gear 0.3.x? The SOURCE says yes; the fw-gear DOCS say no. Do not assert either as fact without a live engine run. (Also confirmed: tag the destination container via `update_container(type, tags=[...])`; there is no `add_container_tags` helper.)
**Details:** All six write methods (`update_container`, `update_file_metadata`, `add_file_tags`, `add_qc_result`, `add_qc_result_to_analysis`, `update_zip_member_count`) route through `_validate_container_type`, which resolves the destination via `config.get_destination_container()` (`get_destination_parent()` for analysis). In the source that raises `RuntimeError: ... Requires authenticated API key` when `config._client` is falsy, and `get_client()` sources a client ONLY from an api-key input (grepped whole package — no env/CLI/ambient path). SO THE CODE PATH NEEDS A CLIENT. BUT fw-gear's own `docs/fw_gear/getting_started.md` presents `update_container`/`add_qc_result` under "Adding Metadata" with NO api-key input, and gates `context.client` as a separate "requires api-key" pattern — documented intent is keyless. Repo facts (fw-gear main @ 0.3.9-dev, cloned from gitlab flywheel-io/scientific-solutions/lib/fw-gear): strict validation ADDED in 0.3.0 ("Metadata class now validates container types more strictly"); legacy flywheel-gear-toolkit had none (that's why keyless always worked before); the `get_destination_container()` call is STILL present unchanged on main and every release through 0.3.7 — no fix/rollback. CORRECTION TO EARLIER THIS SESSION: I first tested with a local mock + real local GearContext and declared it "VERIFIED" that api-key is required. That was wrong — `get_destination_container()` is a live API call that can't run locally at all, so a local RuntimeError proves nothing about a real engine run. The Suzanne Witt (2026-01-15) and Sina/file-curator (2026-02-23) Slack cases were both hierarchy/destination-misclick failures (ValueError), NOT the auth path — they do not establish the api-key requirement. Two outcomes, only distinguishable on the engine: (1) engine supplies a client for destination resolution without an api-key input → keyless works; (2) it doesn't → the 0.3.0 validation broke keyless writes. Context: LONI-metadata-processor MR4 Q3.5.
**Suggested action:** RESOLVE VIA ENGINE RUN — run a metadata-writing gear with NO api-key input, write a tag/QC result, read the job log for `Requires authenticated API key`. Update this entry + the two reference files with the result. Until then: safe default is to include the api-key input for metadata-writing gears, but present it as precaution, not fact. Separately (this part IS solid): tag a container with `update_container(type, tags=[...])` (no read-merge, destination-and-up only); `add_file_tags` is file-only and does union existing tags.
