---
type: Reference
title: Outbound Writing Core
description: The shared rules for anything a skill posts where a human will read it — Jira comments, Slack reports, MR descriptions. Summarize and link; never dump.
tags: [writing, style, jira, slack, outbound]
timestamp: 2026-08-17T00:00:00Z
---

# Outbound Writing Core

Rules for text a skill **posts** — Jira comments, Slack run reports, MR descriptions.
Channel specifics: [jira-comments.md](jira-comments.md), [slack-posts.md](slack-posts.md).

Not for: the local findings file (that one is allowed to be long and complete — it's
the thing these posts point *at*), code, or docstrings.

## The one rule

**Summarize, link, stop.** Every post is an index into evidence, not the evidence.
Data goes in the source; the post says what the data means and where to find it.

The reader is a busy engineer skimming a notification. If they have to scroll, you
wrote a document where a note belonged.

## Length ceilings

| Channel | Ceiling |
|---|---|
| Jira comment | ~200 words / one screen. Over that, the findings file gets it. |
| Slack run report | ~150 words + a short ranked list |
| MR description | ~150 words |

Under the ceiling is not a target to fill. A three-line comment that says the thing
is better than a 200-word one that says it twice.

## Link, don't paste

Every claim points at something checkable. Link the source; quote at most one line
from it.

- Commits → short SHA + subject. Not the diff.
- MRs / tickets → `!9`, `GEAR-22888`. Not a recap of their contents.
- Slack → permalink. Not a transcript.
- Confluence / docs → page title + link. Not the section.
- Code → `path/file.py:74`. Not the function.
- Meeting notes → link + who said it. Not the notes.
- Your own findings file → its path, once, at the end.

If a number is the point, give the number and where it came from: "7,822 bytes,
`unzip -l` on the blob at `<branch>`". That's the whole citation.

## Voice: which guide governs what

`ste-writing` and `no-ai-slop-writing-rules:rossmann-voice` **conflict** — STE wants
short uniform sentences, Rossmann wants deliberate 4-word-next-to-36-word variance.
Do not "apply both." Split them by role:

**Evidence discipline — from `rossmann-voice`:**
- Every claim carries a testable number, identifier, date, or named source.
- Claim first, then proof. No topic sentences, no run-up.
- No intensifiers. "Significantly slower" is a missing number; write the number.
- Name the exact thing: `Batch-Url`, `customfield_10108`, `f28ada67` — not "a manifest
  key", "the customer field", "a recent commit".
- Contractions are fine and preferred.

**Sentence construction — from `ste-writing`:**
- One idea per sentence. Short over clever.
- Active voice, present tense where it fits.
- Plain words. No jargon that isn't the actual name of the thing.

**Explicitly do NOT carry over from `rossmann-voice`:**
- `&` for `and` — a personal tic, wrong in an engineering ticket.
- "Prose over lists" — these posts are skimmed; tight bullets win.
- Contempt-through-precision framing. Keep the precision, drop the edge. Some of
  these tickets are customer-adjacent.

**And do NOT go full strict STE.** No controlled-vocabulary enforcement, no banning
a word that is the correct technical term.

## Slop that shows up in posted comments

Beyond the general `no-ai-slop` rules, these are the ones that actually appear here:

- No em-dashes.
- No preamble. Not "I investigated and found that…" — just the finding.
- No bold-label-colon bullets (`**Impact:** …`). Write the sentence.
- No closing wrap-up ("Overall, this is a solid…"). End on the last fact.
- No rule-of-three padding.
- No hedging on something you tested. You ran it; say what happened.
- Don't restate the ticket back at the reader. They have it open.

## Say what's wrong first

Lead with the broken, surprising, or blocking thing. Happy path last, or not at all.

Name problems plainly: "this is broken", "still can't run headless", "silently
returns 0". Do not soften a real defect into "a potential consideration".

## Don't post nothing

If the only change since the last post is something the reader did themselves, skip
the comment. "You un-drafted your MR" is noise in a record someone reads in six
months. A gate deciding you *may* post is not the same as the post earning its place.
