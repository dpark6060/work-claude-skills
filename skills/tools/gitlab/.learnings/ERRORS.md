# GitLab Skill — Errors & Fixes

Entry format:
```
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: RESOLVED/OPEN
**Area:** <which part of the skill>
**Summary:** <one line>
**Details:** <what happened>
**Fix:** <what resolved it>
```

---

## [2026-08-20] | Priority: HIGH | Status: RESOLVED
**Area:** Triggering pipelines with variables
**Summary:** `glab api -X POST .../pipeline -f "variables[0][key]=..."` silently drops the variable, returns 201, and runs the branch's default pipeline instead — which on a customer deployment repo was `apply:terraform`
**Details:** Tried to run a support bundle on `flywheel-io/customers/nacc/nacc-sandbox` with `-f "variables[0][key]=SUPPORT_BUNDLE" -f "variables[0][value]=true"`. `-f` sends `application/x-www-form-urlencoded`; the pipeline endpoint expects `variables` as a JSON array and does not parse PHP-style bracket notation. GitLab ignored it and returned `201 Created` with a valid pipeline object, so it looked like success. The gating rule `- if: '$SUPPORT_BUNDLE' when: never` (which correctly suppresses apply) never matched, so `op:support-bundle` did not run and `apply:terraform` did. Cancelled ~39s in, during `get_sources` — no terraform ran. Proof:
```
pipeline 2777709582  variables: []                                     -> apply:terraform
pipeline 2777751100  variables: [{key: SUPPORT_BUNDLE, value: "true"}] -> op:support-bundle
```
**Fix:** Use `glab ci run -b master --variables KEY:value -R GROUP/REPO`, or send a real JSON body via `glab api ... --input -`. Then **always** confirm with `glab api "projects/<ID>/pipelines/<PID>/variables"` before letting jobs proceed — a 201 proves a pipeline exists, not that your variable was accepted. Cancel with `POST /pipelines/<PID>/cancel` if it comes back `[]`.

**Two meta-lessons:** (1) don't treat a 2xx as confirmation of intent — verify the effect; (2) don't infer job behavior from a comment above a YAML anchor, confirm the job actually `extends` it.

## [2026-04-13] | Priority: HIGH | Status: RESOLVED
**Area:** glab API write operations
**Summary:** Moved/renamed projects reject PUT/POST with `405 Non GET methods are not allowed for moved projects`
**Details:** When a GitLab project has been moved or renamed, the old path redirects for GET but rejects all write operations. The git remote may still point to the old path, so it cannot be trusted.
**Fix:** Resolve the numeric project ID first (works even on old path via redirect), then use the ID for all write calls:
```bash
glab api "projects/OLD%2FPATH%2FREPO" | jq '.id'
glab api -X PUT "projects/<NUMERIC_ID>/merge_requests/<IID>" -f title="..." -f description="..."
```

## [2026-04-13] | Priority: MED | Status: RESOLVED
**Area:** MCP code search
**Summary:** `mcp__GitLab__search` returns `Invalid JSON response` for some project paths
**Details:** Certain project paths or query strings cause the MCP search tool to fail with an invalid JSON response error.
**Fix:** Fall back to `glab` CLI:
```bash
glab mr list -s opened -R GROUP/REPO
glab mr list --source-branch my-branch
```

## [2026-04-13] | Priority: HIGH | Status: RESOLVED
**Area:** glab authentication
**Summary:** `glab` returns 401 despite `glab auth status` reporting logged in
**Details:** The `token:` field in `~/Library/Application Support/glab-cli/config.yml` can become corrupted with a `!!null` YAML tag. `glab auth status` checks that the field exists (not that it's non-null), so the 401 on actual API calls is the only symptom.
**Fix:** Open the config file, find the `token:` line under `hosts.gitlab.com`, and remove the `!!null ` prefix. No restart needed.
