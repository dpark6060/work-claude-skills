# Owner profile (for action-item extraction)

This file tells the sweep who "me" is, so it can decide which action items are mine —
either assigned explicitly or falling to me by role. Keep it current; extraction quality
depends on it.

<!-- TEMPLATE. Your live copy lives at local/profile.md — run `/meeting-tickets setup`
     to create it. Replace every <PLACEHOLDER>; rewrite "mine by role" for YOUR role;
     start the meetings list thin and grow it over time. -->

## Identity

- **Name:** <FULL-NAME>
- **Spoken/transcript name variants:** <NAMES-PEOPLE-ACTUALLY-CALL-YOU-IN-MEETINGS>
  - List what coworkers actually say, not your formal name — often a surname or a
    nickname (a "Jordan Smith" may be "Smith" in every transcript). The sweep matches
    assignments on these strings ("<name> to ..."), so a missing variant means missed
    action items.
- **Email:** <YOUR-EMAIL>
- **Jira accountId:** `<YOUR-JIRA-ACCOUNT-ID>` (the `atlassianUserInfo` tool returns it)
- **Role:** <YOUR-JOB-TITLE>
- **Department:** <YOUR-TEAM-OR-DEPARTMENT>

## What counts as "mine by role"

Describe the work that falls to you even when nobody says your name — the sweep uses
this to claim unnamed items, so be concrete. Example shape (rewrite for your role):

- Building, scoping, or debugging <THE-SYSTEMS-YOU-OWN>.
- Spinning up infrastructure for an engagement where you're the engineer in the room.
- Following up on a technical integration you're driving.
- Writing or scoping technical proposals/SOPs tied to your projects.

Do **not** claim items that clearly belong to someone else (sales follow-ups owned by an
AE, scheduling owned by the organizer, another engineer's named task, decisions reserved
for a manager). When ownership is genuinely ambiguous, keep the item but mark
`owner_confidence: low` and say why in the context.

## Teams / pods / recurring meetings I'm in

Used to recognize context and tag customers. Start thin; fill in / correct over time.

- **<MEETING-OR-POD-NAME>** — <what it's about>. Customer tag: `<CUSTOMER>` (if any).
  People: <REGULAR-ATTENDEES>.
- **<MEETING-OR-POD-NAME>** — <...>

## Common collaborators (name → email)

Helps the sweep resolve who "he/she/they" is and who owns what.

- <COLLABORATOR-NAME> — <COLLABORATOR-EMAIL>
- <COLLABORATOR-NAME> — <COLLABORATOR-EMAIL>
