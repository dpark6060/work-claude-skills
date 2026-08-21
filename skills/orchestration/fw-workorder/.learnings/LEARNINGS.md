# fw-workorder Learnings

Append confirmed facts discovered during runs. Promote hot ones into SKILL.md and prune.

## 2026-08-12 — initial build

- **Gear index measured at build time:** 77 manifests under the gears root resolve to 68
  unique gear names. 30 repos carry uncommitted *tracked* modifications, 12 more carry only
  untracked files, 5 have client mirror remotes.
- **Dual remotes are a NACC pattern, not universal.** `redcap-processor` and `loni-upload`
  both have `origin` → GitLab `flywheel-io/scientific-solutions/gears/nacc/*` and `nacc` →
  GitHub `naccdata/*`. Only 5 of 68 gears have any mirror remote.
- **`gh` is authenticated as `dpark6060`** with `repo` scope, so github-origin gears can get
  draft PRs. GitLab-origin gears go through the `gitlab` skill.
- **Gear name ≠ directory name, reliably.** `loni-upload` lives in
  `NACC-loni-upload-gear/nacc-loni-uploader/`. Never resolve a gear by directory name.

## 2026-08-12 — first real run (`pipeline_adcid`), confirmed facts

- **The skill's own worked example was wrong, and intake caught it.** Both the depth rubric
  and the estimate rubric use `pipeline_adcid` as their example and claim `redcap-processor`
  *and* `loni-upload` read `project.info.center.adcid`. `loni-upload` never reads a
  project-level ADCID at all — `loni_mapper.py:65` builds the LONI `Site` column from
  `redcap_data.adcid`, sourced from `session.info["series-metadata"]`, which
  `redcap-processor` writes. One gear changed, not two; one 30-min entry, not two. **Grep the
  claim before scoping a repo in, even when the request and this skill agree on it.**
- **Confirmed IDs for `UWash - NACC` time logging:** Clockify client
  `62d18685a111991d1068f6ca`, project `Solutions Hourly` = `6a4689480dd182727a826249` (note
  the sibling traps: `Solutions Hourly - 2023/2024`, `Solutions Hourly - U24`, and
  `Solutions Fixed` all live under the same client), task `[GEAR-12084]` =
  `6a75ff0d30fb6ae7561cf05d`, task `[GEAR-20969]` = `6a7b33ca003030c0bb94374e`. Both tasks
  `ACTIVE`.
- **The clockify MCP server was not registered in this session** — `ToolSearch` for
  `mcp__clockify__*` returned nothing. The SDK fallback works but needs
  `cl.get_flywheel_workspace()` before any workspace-scoped call, or every request goes to
  `workspaces/None/...` and 403s with `{"message":"Access Denied","code":501}`. Two further
  gotchas were written into the `clockify` skill's `sdk-usage.md`: `add_time_entry()` returns
  no usable id (verify with `get_day_entries.py`, never retry on an empty return), and
  `check_overlap.py` requires a literal trailing `Z` on `--start`/`--end`.
- **New Stories land in `INBOX`**, a status that does not appear in the Epic transition table.
  Transition `21` moves a Story to `IN PROGRESS`; Epic `11` does not (see `ERRORS.md`).
- **Epic children do not follow the `<EpicNickname>-<N>` summary convention** in
  `create-ticket.md`. GEAR-12084's existing stories use plain descriptive summaries
  ("Update the REDCap gears' data model for the finalized NACC REDCap EDC form"). Matched the
  epic's actual convention rather than the doc's.
- **Slack MCP returns no display name for the external/guest replies** in the NACC channel —
  the actual requester's messages came back with an empty `From`. Cite the permalink and
  timestamp and say the name is unavailable; do not guess from nearby @-mentions.

## 2026-08-12 — Jira→Clockify sync, read from source

Read from `jira_clockify_sync/sync.py` in GitLab project `38298158`. The wiki and older
notes disagree with the code in two places; the code wins.

- **Epic status is an allowlist, not "anything but New Request".**
  `EPIC_STATUS_CREATING_TASK = ["TO DO", "READY FOR DEV", "IN PROGRESS",
  "REQUIREMENTS DEVELOPMENT", "UAT", "ON HOLD"]`. `Internal Backlog List` is excluded and
  looks open while being `done`-category.
- **A closed Clockify task is a dead end — pause and flag.** The sync has **no
  ACTIVE-restore path**: `update_task()` only renames or closes; `status: "ACTIVE"` is
  written only in `create_task()`, which runs only when no matching task exists. So
  reopening the epic and running the sync leaves the task `DONE`. And the manual fix
  (`PUT .../tasks/{id}` with `status: ACTIVE`) needs Clockify manager/admin permissions —
  **David tested it 2026-08-12 and does not have access.** Detect this at intake (read-only)
  and stop at the gate; it needs an SSE Manager, not a workaround.
- **Read task status; never infer it from the epic's dates.** The 42-day grace period
  explains one way tasks close, but does not predict state. `GEAR-11687` resolved only 15
  days ago and its task is already `DONE` — something other than the grace period closed it.
  Measured 2026-08-12: 7595 DONE (76d), 11687 DONE (15d), 12084 ACTIVE, 20969 ACTIVE.
- **No sprint requirement.** The sync's JQL filters on `Customer/s` and labels only — there
  is no sprint or work-item clause. An active sprint item is not needed for a task to sync.
- **Customer must be on `config.yaml`'s allowlist** (~55 names) or the epic never syncs
  regardless of labels. `UWash - NACC` is on it.
- **Schedule confirmed live:** id `274132`, `Sync every 6h`, cron `0 */6 * * *`,
  `America/Chicago`, active. Confluence's "daily at 3am CT" is stale.
- Worked cases: `GEAR-7595 [NACC] LONI Exporter` resolved 2026-05-28 (76 days → task
  `DONE`, needs manual reactivation); `GEAR-11687 [NACC] session-splitter` resolved
  2026-07-28 (15 days → task still `ACTIVE`, nothing to do).

## 2026-08-14 — loni-upload JAR v2 run

- **Jira sprint field on create: pass a plain int.** `createJiraIssue` with
  `"customfield_10021": {"id": 3555}` 400s ("Specify a valid value for Sprint");
  `"customfield_10021": 3555` works. create-ticket.md's example shows the dict form — wrong.
- **`pm` dispatches can go idle without delivering a report.** Got two bare
  idle_notifications and no status line. Recovery that worked: verify the repo state
  directly (branch, commit, diff stat, md5, run pytest yourself) instead of ping-ponging
  messages. The commit was complete and correct; only the report was missing.
- **Sprint 26Q3 = id 3555 (`SSE - Board - 26Q3`, boardId 35), active through 2026-09-30.**
- **GEAR-20969 has no children via `parent = GEAR-20969` JQL** even though the sync treats
  it as an epic — new stories under it appear fine; don't rely on that query for convention
  matching.
- **Clockify SDK scripts need the skill's own venv**
  (`~/.claude/skills/clockify/.venv/bin/python`) — system python3 lacks `fw_http_client`.
