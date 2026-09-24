# Capacity — {{QUARTER}}

*Snapshot {{SNAPSHOT_DATE}} ({{SNAPSHOT_AGE}}). {{WEEKS_REMAINING}} working weeks left in the quarter.*

## The call

{{ONE_PARAGRAPH_VERDICT}}

<!-- Lead with what's broken. Which dates miss, by how much, and the single biggest cause.
     If everything lands, say that in one line and move on. No preamble. -->

## Overdue now

| Epic | Summary | Due | Days over | Blocker |
|---|---|---|---|---|
| {{KEY}} | {{SUMMARY}} | {{DUE}} | {{DAYS_OVER}} | {{BLOCKER}} |

<!-- Omit the section entirely if nothing is overdue. -->

## Plan vs. reality

|  | Hours | |
|---|---|---|
| Raw available ({{WORKING_DAYS}} days − {{HOLIDAYS}} holidays × 8) | {{RAW_AVAILABLE}} | |
| PTO / vacation | {{PTO_HOURS}} | |
| Admin | {{ADMIN_HOURS}} | |
| Meetings ({{MEETING_COUNT}} events) | {{MEETING_HOURS}} | |
| **Overhead the haircut must absorb** | **{{OVERHEAD_HOURS}}** | **{{OBSERVED_HAIRCUT}}** |
| Plan assumes | | {{PLANNED_HAIRCUT}} |

<!-- The haircut covers PTO AND admin AND meetings — the column has no row for any of them.
     Comparing admin alone against it understates the gap. -->

**Landing rate:** {{LANDED_HOURS}} of {{PROJECT_HOURS}} project hours reached an allocated
initiative ({{LANDING_RATE}}). The plan assumes 100%.

Applying both rates to the full quarter: **{{REALISTIC_CAPACITY}}h** lands on allocated
initiatives against **{{ALLOCATED}}h** allocated — {{PCT_OF_PLAN}} of plan.

{{HAIRCUT_COMMENTARY}}

<!-- Evidence quality: if every full week in by_week reads exactly 40.00h, Clockify was
     reconstructed by the day-fill process. Say so here — the haircut figure depends on it. -->

## Where the hours go

| Client | Allocated | Meetings | Productive | Committed (Jira) | Verdict |
|---|---|---|---|---|---|
| {{CLIENT}} | {{ALLOCATED}} | {{MEETINGS}} | {{PRODUCTIVE}} | {{COMMITTED}} | {{VERDICT}} |
| **Total** | **{{A_TOTAL}}** | **{{M_TOTAL}}** | **{{P_TOTAL}}** | **{{C_TOTAL}}** | |

## Work with no allocation

| Hours | Where | Note |
|---|---|---|
| {{HOURS}} | {{PROJECT}} > {{TASK}} | {{NOTE}} |
| **{{UNALLOC_TOTAL}}** | | **{{PCT_OF_PROJECT_TIME}} of all project time** |

<!-- By name and hours, never a single "other" line. This is the argument for renegotiating
     the plan. Note where it's structural — e.g. Support/Implementation exists as a team-level
     category but is never allocated into individual columns. -->

## Epic forecast

| Epic | Client | Remaining | Weeks to finish | Finish | Due | Verdict |
|---|---|---|---|---|---|---|
| {{KEY}} | {{CLIENT}} | {{REMAINING}}h | {{WEEKS}} | {{FINISH}} | {{DUE}} | {{VERDICT}} |

<!-- Epics sharing a client queue against the same productive hours — order by due date and
     accumulate. Mark any t-shirt-derived estimate "low confidence". -->

## Tradeoffs

### To hit {{EPIC_A}}

{{OPTION}} — recovers {{HOURS}}h, pulls {{EPIC}} in by {{DELTA}}. **Costs:** {{COST}}.

<!-- One block per missing epic. Every option names what slips. If two epics can't both land,
     say which one the numbers favour and why. Omit the section if nothing misses. -->

## Not forecast

| Epic | Why |
|---|---|
| {{KEY}} | {{unestimated / on hold / no due date / blocked}} |

## Loose ends

- {{Allocations with no matching epic, epics with no matching allocation, unresolved map entries,
   workbook discrepancies, unmatched meeting load above 25%}}

---
*Sources: {{WORKBOOK_TAB}} · Outlook {{QUARTER_RANGE}} · Jira {{EPIC_COUNT}} epics{{CLOCKIFY_NOTE}}.
Assumed: {{ADMIN_PER_WEEK}}h/week admin overhead.*
