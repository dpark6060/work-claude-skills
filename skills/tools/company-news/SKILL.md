---
name: company-news
description: >
  Crawls Flywheel's company announcement sources (Nikki's update emails, IT announcement
  emails, the All Hands transcript and slides, #general, #ask-anything,
  #real-talk-with-product, #it-crowd-sourced, #fw-it-security-postman) and the JSM ticket
  diff, keeps only what matters per a criteria file, and writes scored news items for
  the work dashboard's News tab. Normally run headless by run_news_crawl.sh. MANDATORY
  TRIGGERS: company-news, news crawl, crawl company news, what's the company news,
  backfill news.
---

# Company News

The wrapper gives you these in the prompt:
- `CONTEXT`: JSON with `window_start`, `source_windows`, `themes` and `recent_ticket_items`.
- `ITEMS_FILE`, `REPORT_FILE` and `CRITERIA_FILE` paths.
- `FW_IT_SYNC`: the ticket sync script.
- `VALIDATE`: the command that checks your items file.

Read `CRITERIA_FILE` first. It decides what counts and how to score it.

## 1. Read each source from its own window

`CONTEXT.source_windows` gives each source's start time, keyed by the bracketed names
below. A source that failed last time starts further back so nothing is lost. Use that
source's window, not the overall `window_start`.

A source that fails (tool error, connector never loads after ToolSearch) goes in
`failed_sources` under the name in brackets. Keep going with the rest.

- **[company-email]** `outlook_email_search` with `sender: "nikkicarlsoncullina@flywheel.io"`
  and `afterDateTime: <its window>`. Read each with `read_resource`. Link the item to
  the email's `webLink` (an `https://outlook.office365.com/...` URL) from the search or
  read result.
- **[it-email]** `outlook_email_search` with `query: "IT"` and `afterDateTime`. Keep only
  company-wide IT announcements (to all staff or a company list), never personal
  ticket mail. Link to the email's `webLink`.
- **[allhands]** `outlook_calendar_search` with `query: "All Hands"`,
  `organizer: "nikkicarlsoncullina@flywheel.io"` and the window. For each event, call
  `read_resource` on its `meetingTranscriptUrl` verbatim; that's the same Teams method
  the meeting-tickets skill uses. Then read the slides: `sharepoint_search` for the
  meeting's date in the "All Hands Presentations" folder (a follow-up email or #general
  post usually points there), and `read_resource` on the PDF. Link items to the event's
  `webLink`, or to the PDF when the item comes from the slides.
  David often can't read the transcript; a 403 "does not have access to lookup meeting"
  is expected. When that happens, the slides are the source. `allhands` has failed only
  if **neither** the transcript nor the slides could be read.
- **Slack**, with `slack_read_channel`. Set `oldest` to 7 days before the channel's
  window, because replies land on older parents. Treat a message as new when it was
  posted inside the window. For any message with replies, call `slack_read_thread` and
  treat replies posted inside the window as new; an answer to last week's
  #ask-anything question is news. Channels:
  - [slack-general] `CE10W8HST`
  - [slack-ask-anything] `C06TXNBE25Q`
  - [slack-real-talk-with-product] `C050VHN7HUH`
  - [slack-it-crowd-sourced] `C08F520EAF8`
  - [slack-fw-it-security-postman] `C087U6STLAX`

  Link each item to the message permalink:
  `https://flywheel-io.slack.com/archives/<channel>/p<ts with the dot removed>`. For a
  thread, use the parent message.
- **[it-tickets]** run `uv run "$FW_IT_SYNC" sync`. **Never run `commit`**; the wrapper
  does that after your items are stored. Use `new[]`, `updated[]`, `closed[]` and
  `newly_stale[]` across every desk. Ignore `open[]`, except to count.
  If `JIRA_TOKEN` is unset or the sync exits non-zero, `it-tickets` has failed.

## 2. Judge and write items

One item per real piece of news. Merge a message and its thread, or an email and its
Slack echo, into one item that links to the best source.

- `section`:
  - `company`: Nikki's email, all hands, #general, #ask-anything, #real-talk-with-product.
  - `it`: IT email, #it-crowd-sourced, #fw-it-security-postman.
  - `tickets`: JSM.
- `summary`: one sentence, the fact itself, no preamble.
- `who`: the person who posted or sent it. For tickets, the reporter.
- `source`: `email`, `slack`, `allhands` or `jsm`.
- `date`: when it was posted, as a plain date `YYYY-MM-DD`. Never include a time.
- `importance`: 3–5 per the criteria file. Don't output 1–2.
- `action` and `deadline`: only when the item requires David to act.

**Tickets** add these fields:
- `ticket_key` and `change` (`new`, `comment`, `stale` or `closed`).
- `theme`: reuse a name from `CONTEXT.themes` whenever it fits. Invent a short new theme
  only for a genuinely new problem.
- `insight`: one or two sentences in the voice of "Another MFA ticket opened by Joe.
  This is the 9th MFA ticket; the company seems to be having MFA trouble. IT is
  responding quickly." Use the theme's count (`CONTEXT.themes` plus this run's new
  tickets) and how IT has been responding (comments, time to close), from this diff and
  `recent_ticket_items`.
- `link`: `https://flywheelio.atlassian.net/servicedesk/customer/portal/<desk_id>/<KEY>`,
  using each request's `desk_id` from the sync output.

Give a theme to **every** ticket, including ones you score 1–2 and drop. These go in
`ticket_themes` (key → theme), so the lifetime counts are true counts:
- Every key in `new[]`, `updated[]`, `closed[]`, `newly_stale[]` and `open[]`, on
  every desk.
- Re-theming an open ticket each night is expected. Keep it on the same theme name it
  had before (see `CONTEXT.themes` and `recent_ticket_items`) so the counts stay stable.

Before writing the file, count the distinct keys in those lists and check that
`ticket_themes` has exactly that many. Put "themed N of N tickets" in the report.

Write `ITEMS_FILE` in exactly this shape. No extra keys, and no ticket keys on
non-ticket items:

```json
{
  "window_start": "<CONTEXT.window_start>",
  "failed_sources": ["slack-general"],
  "ticket_themes": {"FIS-1234": "MFA", "FIS-1240": "Printer"},
  "items": [
    {"section": "company", "summary": "Benefits enrollment opens Nov 1; plan options change for 2027.",
     "who": "Nikki Carlson Cullina", "source": "email", "link": "https://outlook.office365.com/owa/?ItemID=...",
     "date": "2026-10-13", "importance": 4, "action": null, "deadline": null},
    {"section": "tickets", "summary": "Another MFA ticket opened by Joe Smith (FIS-1234).",
     "who": "Joe Smith", "source": "jsm",
     "link": "https://flywheelio.atlassian.net/servicedesk/customer/portal/1/FIS-1234",
     "date": "2026-10-13", "importance": 4, "action": null, "deadline": null,
     "ticket_key": "FIS-1234", "change": "new", "theme": "MFA",
     "insight": "9th MFA ticket tracked; looks company-wide. IT is replying within hours."}
  ]
}
```

Every `link` must start with `https://`. Rules for `failed_sources`:
- Use only the bracketed names above.
- Leave it `[]` when nothing failed.

Then run `VALIDATE ITEMS_FILE`. If it prints errors, fix the file and run it again
until it prints `valid: N items`. An invalid file loses the whole night.

## 3. Report and post

Write the Slack summary to `REPORT_FILE`:
- The item count per section.
- The critical items in full.
- A line starting `ATTENTION:` for each failed source.

Then use `report-to-slack` with channel `C0BEHDHGCLD`. End your output with exactly
`NEWS_RESULT items=<N>`.

The ticket sync state (`tracked.json`) is shared with the on-demand `fw-it-summary`
skill. If someone runs that skill's `commit` between nights, the next crawl won't see
those changes.
