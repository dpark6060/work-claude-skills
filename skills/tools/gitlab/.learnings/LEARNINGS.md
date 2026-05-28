# GitLab Skill — Learnings

Entry format:
```
## [YYYY-MM-DD] | Priority: HIGH/MED/LOW | Status: RESOLVED/OPEN
**Area:** <which part of the skill>
**Summary:** <one line>
**Details:** <what worked, why it matters>
**Suggested action:** <if any change was made to the skill>
```

---

## [2026-04-13] | Priority: MED | Status: RESOLVED
**Area:** MR API calls
**Summary:** Always use `iid` (not `id`) for MR numbers in API calls
**Details:** `iid` is the MR number shown in the GitLab UI. The global `id` is a different internal identifier. Using `id` by accident causes 404s or operates on the wrong MR.
**Suggested action:** Documented in SKILL.md MR section.

## [2026-04-13] | Priority: MED | Status: RESOLVED
**Area:** glab api path encoding
**Summary:** `/` in GROUP/REPO must be encoded as `%2F` in `glab api` endpoints
**Details:** `glab api "projects/GROUP/REPO/..."` fails or misroutes. The correct form is `projects/GROUP%2FREPO%2F...` with all slashes encoded.
**Suggested action:** Documented in SKILL.md file-fetching and REST API sections.
