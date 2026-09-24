---
name: write-for-human
description: Writes prose that a distracted human will actually read — Confluence/Jira/technical docs, email, or Slack. Enforces a lead executive summary, hard length caps per medium, and a mandatory no-slop → STE → deletion-pass pipeline before delivery. Use for any text a person other than the user will read. MANDATORY TRIGGERS - write for human, write this up, draft an email, draft a slack message, post this to slack, write the confluence page, write the jira description, write the ticket description, summarize this for the team, send this to the client, make this readable, write the MR description, write the status update.
---

You are writing for a human with a short attention span. That is the whole job. Assume the
reader is skimming on a phone between meetings and will stop at the first paragraph that looks
like work.

## Golden Rules (all modes)

1. **Lead with an executive summary.** 1-5 sentences. The answer, the ask, or the bottom line —
   first, before any context. Never build up to it.
2. **Bullets are fragments.** A single word is fine. One short sentence is the ceiling. Two
   sentences in a bullet is a defect.
3. **No long sentences anywhere.** If it needs a comma splice or a semicolon to hold together,
   split it.
4. **Bugs and bad news first.** Happy path last. Name problems plainly: "this is broken",
   "silently returns 0". Never soften a defect into "a potential consideration".
5. **Offer depth, don't deliver it unasked.** "Want the detail on X?" beats three paragraphs on X.
6. **Summarize, link, stop.** A post is an index into evidence, not the evidence. Link the
   source and quote at most one line of it:
   - commits → short SHA + subject; MRs and tickets → `!9`, `GEAR-22888`
   - Slack → permalink; Confluence → page title + link; meetings → link + who said it
   - code → `path/file.py:74`; your own findings file → its path, once, at the end
7. **Every claim carries evidence.** A number, identifier, date, or named source. Name the
   exact thing (`customfield_10108`, `f28ada67`), not "the field" or "a recent commit". No
   intensifiers: "significantly slower" is a missing number. No hedging on something you
   tested. Contractions are fine.
8. **Don't post nothing.** If the reader learns nothing they don't already have on screen,
   don't write it. A gate saying you *may* post is not a reason to post.

## Step 1 — Pick the Mode

| Reader is on... | Mode |
|---|---|
| Confluence, Jira ticket/description, MR description, technical doc | **Docs** |
| Email — client, internal, external | **Email** |
| Slack, Teams, any chat | **Chat** |

A calling skill names its default mode. **A mode the user names in their prompt beats the
skill's default.** Otherwise unclear? Ask one short question. Don't write two versions.

READMEs, developer guides, and module docs that live in a code repo go to the `doc-writer` skill
instead. It owns their structure and runs Step 3's pipeline itself.

## Step 2 — Pick the Channel

If the text is posted to one of these, load its file. **The channel file wins over the mode on
shape, length, and sign-off.** Mode still governs tone and the pipeline.

| Channel | Default mode | File |
|---|---|---|
| Jira comment | Email | [references/jira-comments.md](references/jira-comments.md) |
| Jira ticket description | Docs | [references/jira-description.md](references/jira-description.md) |
| MR description | Docs | [references/mr-description.md](references/mr-description.md) |
| Slack run report or nudge | Chat | [references/slack-posts.md](references/slack-posts.md) |

None of these? The mode rules alone apply.

## Mode 1 — Docs

- Executive summary at the top, 1-5 sentences.
- Break the body into **bite-sized sections**. If a section can't be skimmed in ~15 seconds, split it.
- Every section opens with its own **1-3 sentence summary**, then the detail. The reader must be
  able to read only the section openers and understand the whole document.
- Write simply. Plain words over precise-sounding ones.
- **Diagrams earn their place.** A mermaid flowchart, sequence diagram, state diagram, or gantt
  beats three paragraphs describing the same flow. Reach for one whenever you're describing
  order of operations, who-calls-what, a state machine, or a timeline. Confluence and GitLab
  both render mermaid; Jira descriptions generally do not — there, use a plain ASCII diagram or
  link out.
- **Validate every mermaid block before delivering.** Write it to a temp file and run
  `mmdc -i diagram.mmd -o diagram.svg`. A block that fails to render is worse than no diagram.
  For whether a diagram earns its place and what it should show, the `artifact-diagramming`
  skill has the judgment content — load it when the choice isn't obvious. Charts and graphs go
  to `dataviz` instead.
- Tables beat prose for anything with more than two parallel items.

## Mode 2 — Email

Tighter than docs. The reader decides whether to keep reading at the subject line.

- Subject line states the ask or the outcome, not the topic.
- Open with the 1-3 sentence summary. If there's an ask, it goes in the first two sentences.
- **One concept per point.** Each concept gets one or two sentences. That's it.
- No background section, no "as discussed", no recap of what they already know.
- When a point genuinely needs more: state it in one sentence and **offer the detail**. "Happy to
  walk through the migration steps if useful." Never write the walkthrough unprompted.
- Close with the ask or the next action, one line. No sign-off padding.

## Mode 3 — Chat (Slack/Teams)

The hardest cap. Attention span is near zero.

- **3-4 sentences maximum per message.** Not a guideline.
- More to say? **Split into multiple messages, one topic each.** Each still caps at 3-4 sentences.
  Never one long message with headers.
- A few bullets appended to those sentences is fine — fragments only.
- No greeting, no preamble, no "just wanted to flag". Lead with the thing.
- Code, logs, error strings: in a code block, trimmed to the relevant lines.
- Long output (a report, a plan, a list of 10 items) doesn't belong in chat. Say what it is in
  two sentences and link or thread it.

## Step 3 — The Pipeline (mandatory, every writing request)

After drafting and before delivering, run all three in order. Do not skip one because the draft
"already looks clean."

1. **`no-ai-slop-writing-rules:no-ai-slop`** — strip the AI tells. Em-dashes, "Here's...",
   bold-label bullets, rule-of-three padding, wrap-up paragraphs.
2. **`ste-writing`** — simplified-technical-English pass. One idea per sentence, plain
   vocabulary, active voice. Use STE-flavored mode for general prose; strict mode only for
   procedures and safety steps. Never ban a word that is the correct technical term.
3. **`deletion-pass`** — cut every concept and sentence the request doesn't require.

## Step 4 — Check Before You Send

- Does sentence one carry the whole point?
- Any bullet longer than one short sentence?
- Is every number attached to where it came from?
- Chat mode: did any message exceed 4 sentences?
- Email mode: did you explain something you should have offered instead?
- Docs mode: would a diagram replace a paragraph you just wrote?
- Channel: is it under that channel's ceiling?
- Anything left that the reader already knows?

Fix, then deliver.
