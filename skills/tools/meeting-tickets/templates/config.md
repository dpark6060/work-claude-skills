# meeting-tickets — local config: paths + reporting

<!-- TEMPLATE. Your live copy lives at local/config.md — run `/meeting-tickets setup`
     to create it, or copy this file there and edit. Replace every <PLACEHOLDER>. -->

## Paths

- **Draft dir:** `<PATH-TO-DRAFT-DIR>` (e.g. `~/claude-work/meeting-tickets/`)
  - Create if missing. Must be OUTSIDE any git repo — it holds real meeting content.
    Never point it into `~/.claude` or a skills repo.
  - The **state file** is always `<draft-dir>/.state.json` (not separately
    configurable): `{ "last_run": "<iso8601>", "processed_transcript_ids": [...] }`.
    Ids are namespaced `<source>:<id>` per `local/sources.md`.

## Scheduled-run reporting

- **Slack report channel:** `<SLACK-CHANNEL-ID>` — or `none` to disable Slack reporting.
- **Reporter skill:** `report-to-slack` (posts no matter what — success, empty, or
  failure). If you don't have that skill, set the channel to `none`; the sweep still
  prints its human summary and `SWEEP_RESULT` line to stdout.
- Interactive runs never post to the channel — reporting is scheduled-run behavior only.
