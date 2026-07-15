# Draft file format

Both modes share this. `sweep` writes it, `review` reads it and writes ticket keys back.

## Location

- Draft dir: `<draft-dir>/` — the draft dir comes from `local/config.md` (outside any
  git repo — contains real meeting content).
- One file per day: `<draft-dir>/YYYY-MM-DD.md` (date of the sweep run, local time).
- A run **appends** to that day's file; it never clobbers existing entries.

## File skeleton

```markdown
# Meeting ticket drafts — 2026-06-24

_Swept 2026-06-24 17:00 local. Window: 2026-06-23 17:00 → 2026-06-24 17:00._

---

## DRAFT 1 — Create platform tickets for Acme Corp storage buckets
- **status:** pending          <!-- pending | approved | rejected | created -->
- **ticket:** —                <!-- filled with <KEY-####> once created, e.g. PROJ-1234 -->
- **owner_confidence:** high   <!-- high | low; low = ownership was ambiguous -->
- **source_meeting:** Acme Corp Internal Pod Sync
- **meeting_date:** 2026-06-23
- **transcript_id:** ktVizInG...TranscriptV2
- **transcript_source:** teams  <!-- the configured source's `name` from local/sources.md, e.g. teams, zoom -->
- **suggested_type:** Task
- **suggested_priority:** Medium
- **suggested_labels:** Acme-Corp
- **suggested_customer:** Acme Corp
- **due:** —

**What I'm on the hook for:**
Create the platform tickets to provision the three Acme Corp storage buckets (East US,
Israel, Norway). Jordan confirmed this is mine.

**Context / quotes:**
> Sam: "...for Alex to create the platform ticket."
> Jordan: "The expectation would be yes for Alex to create the platform tickets."
> Jordan: "3 buckets, right? One in the East US where the prod instance is deployed, and
> two more, one in Israel and one in Norway."

**Related:** PLT (platform tickets); follows the V7 integration work. Israel bucket
already done via an earlier platform ticket.

---

## DRAFT 2 — ...
```

## Field rules

- **status** drives everything. `review` only offers `pending` drafts; on creation it
  flips to `created` and fills **ticket**. Rejected items stay in the file as `rejected`
  (a record of what was considered and dropped).
- **transcript_id** is the dedupe key, namespaced by source — e.g. `teams:<id>`, or
  `<source-name>:<stable-key>` for whatever other sources are configured in
  `local/sources.md`. `sweep` skips any id already in `.state.json`, so a
  given meeting is only ever drafted once.
- **transcript_source** is the configured source's `name` from `local/sources.md` (e.g.
  `teams`, `zoom`). Sources with `speaker_attribution: no` (e.g. a local
  fallback transcript with no speaker labels) mean lower-confidence drafts — treat them
  as such (see S5).
- Keep **What I'm on the hook for** to 1–3 sentences — it becomes the ticket description
  lead. **Context / quotes** are verbatim transcript lines so the ticket carries enough
  to act on without re-listening.
- Summary line (the `## DRAFT n — <summary>`) becomes the Jira `summary`. Keep it
  imperative and specific.
- **suggested_labels** must be topical only (customer / feature — e.g. a customer or
  system name). Never suggest an automation-derived label — see `local/tracker.md`'s
  no-automation-fingerprint rule.
