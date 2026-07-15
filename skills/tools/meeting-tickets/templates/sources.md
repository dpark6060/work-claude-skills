# Sources manifest — meeting index + transcript sources

<!-- TEMPLATE. Your live copy lives at local/sources.md. `setup` writes the Meeting
     index and Teams entries below VERBATIM (org default — no questions) and asks only
     "any other transcript tools?". "Adding your own source" at the bottom is the
     shape for any extra entry. -->

## Meeting index

Which tool enumerates candidate meetings for the sweep window, and what to drop cheaply
before reading details.

- **Tool:** `outlook_calendar_search` (Microsoft 365 connector) — `query: "*"`,
  `afterDateTime`/`beforeDateTime` = the window, `order: "newest"`, paging until the
  window is covered.
- **Event details:** `read_resource` on the event's `calendar:///events/...` uri.
- **Cheap drops (index-specific):**
  - Subjects starting `Canceled:`, `Cancelled:`, or `Declined:`.
  - All-day events (`isAllDay`) and self-blocks with `attendees: null` and
    organizer = me ("Focus Time", "Lunch", "Outside working hours").
  - Anything that isn't plausibly a real meeting (no other attendees).

## Transcript sources (priority order)

For each surviving meeting, try these in order; first transcript wins. Every entry
declares the same six fields — SKILL.md keys behavior off `name` (the dedupe-id
namespace) and `speaker_attribution` (drives the conservative extraction rules in S5).

### 1. Teams (org default — the gold standard)

- **speaker_attribution:** yes — WEBVTT `<v Speaker>` tags, attribution is real.
- **detect:** the calendar event has a `meetingTranscriptUrl`.
- **fetch:** `read_resource` on the `meetingTranscriptUrl` **verbatim** (it carries the
  occurrence's `start`/`end`). The response gives `transcripts[].id` and `.content`
  (WEBVTT).
- **dedupe_id:** `teams:<transcripts[].id>`.
- **caveats:** an empty transcript body counts as "no transcript here" — fall through
  to the next source.

## Adding your own source (Zoom, Granola, a local recording app, ...)

Add extra sources as `### N. <name>` entries above, in priority order — the heading's
name doubles as the dedupe-id prefix. Every entry declares the same fields:

- **speaker_attribution:** `yes` or `no`. `no` = a plain transcript with no speaker
  labels (typical for local Whisper-style recorders) — S5 then extracts on
  first-person commitment cues only and defaults items to `owner_confidence: low`,
  so expect lower-confidence drafts from such a source.
- **detect:** how to tell this source has a transcript for a given calendar event.
  An API source usually has a field on the event or a lookup by meeting id. A local
  recording app usually doesn't — match on **time**: find the recording whose
  start/end window overlaps the event's `[start, end]`, allowing a few minutes'
  slack for a late start or overrun; if several overlap, take the greatest overlap.
  Never match on meeting *names* — recorders auto-generate them.
- **fetch:** the exact tool calls or file reads that yield ONE plain transcript —
  name the endpoints or file paths, and how to join segments if the transcript is
  chunked.
- **dedupe_id:** `<name>:<stable-key>`. Pick a key that survives re-runs unchanged —
  an id the API returns, or a recording folder/file name. Never a timestamp you
  re-derive per run.
- **caveats:** fidelity notes, empty-transcript handling ("empty counts as no
  transcript — fall through to the next source"), and anything the next person
  needs to know before trusting it.
