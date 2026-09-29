---
type: Template
title: PM Update Low-Detail Report Template
description: The fill-in skeleton for a low-detail (default) pm-update epic status comment — verdict line, done bullets, one current-work sentence.
tags: [pm-update, template, report, budget, low-detail]
timestamp: 2026-09-29T00:00:00Z
---

# PM Update Low-Detail Report Template

Replace every `<PLACEHOLDER>` or delete its whole section. Caps and vocabulary live in
`SKILL.md`. `<PROJECTION>` is "budget runs out ~<DATE>" from the script's
`budget_exhausted_on_short`; delete it when velocity is unknown. `· <BUILT>% built` appears
only when the script carries a measured `percent_complete`. `<BLOCKED_LINE>` exists only when
a ticket is ⛔. **Copy from below the line only — the frontmatter above must never reach
Jira.**

---

**<VERDICT>** · `<BAR>` <BURN>% of budget used<BUILT_PART> · <REMAINING>h of <BUDGET>h left · <PROJECTION>

- <DONE_ITEM>

<CURRENT_WORK>

<BLOCKED_LINE>

— pm-update (auto-posted, <TODAY>)

```pm-update-snapshot
<SNAPSHOT_JSON>
```
