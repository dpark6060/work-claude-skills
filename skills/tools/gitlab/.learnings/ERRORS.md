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
