---
type: Data Layout Reference
title: SSE Capacity Workbook Layout
description: How the quarterly SSECapacityPlan tab encodes per-person allocation, and why the M365 connector cannot read it.
tags: [capacity, excel, sharepoint, openpyxl]
timestamp: 2026-09-17T00:00:00Z
resource: https://flywheelio.sharepoint.com/sites/solutions/Shared%20Documents/Scientific%20Solutions/Clockify/SSE-2026-CapacityPlanning.xlsx
---

# SSE Capacity Workbook Layout

> **Load when:** `read_capacity_sheet.py` exits non-zero, the workbook has been restructured, or
> you need to understand where a number in the snapshot came from.

Decoded from `Q3-2026-SSECapacityPlan` on 2026-09-17. 31 sheets total; the quarterly tabs follow
`Q<n>-<year>-SSECapacityPlan` and are roughly sheet 17-23.

**The layout is not stable across quarters.** Whoever maintains the workbook rebuilds the tab each
quarter, so anchors move. Verified against the 2026 tabs:

| Tab | State |
|---|---|
| `Q3-2026` | Current layout. Everything below applies. |
| `Q2-2026` | Same initiative table, **no "working days" capacity block** — the capacity section uses `Target`/`Available`/`Client Work(PS)` labels around column L instead. |
| `Q1-2026` | Structurally different. Headers in row 2, no "projected consumption" column at all. |

The script therefore degrades in three steps rather than assuming stability: allocations need only
the header row and the type/name/hours columns, so they survive most reshuffling; the capacity block
is optional and its absence lands in `discrepancies`; a missing hours column is fatal because
nothing meaningful can be computed without it. **When the next quarter's tab lands, run the script
first and read the discrepancies before trusting any number.**

# Access

**The Microsoft 365 connector cannot read this workbook.** Tested, not assumed:

- `read_resource` on an `.xlsx` renders *every* sheet as tab-separated text starting at sheet 1,
  and stops at a fixed budget after ~11 sheets. `Q3-2026-SSECapacityPlan` is sheet 23.
- There is no sheet or range selector. `startPage`/`endPage` apply only to formats Graph converts
  via PDF (pdf, docx, pptx); passing `startPage=12` on this workbook returns byte-identical output
  beginning at sheet 1 again.
- `sharepoint_search` returns only a truncated content preview of the first sheet.

The Graph Excel REST API (`/workbook/worksheets('<tab>')/range(address='...')`) would solve this
cleanly, but needs a Graph token the connector doesn't expose. Until that exists, David downloads
the file and the script reads a local copy from `cache/`.

# Schema

## Initiative table — rows 2 through the summary anchor

| Column | Holds |
|---|---|
| `H` | Type: `SOW`, `Internal`, or `Gear RM` |
| `I` | Customer / initiative name — **the authoritative name** for client mapping |
| `J` | Remaining contract term, months |
| `K` | Remaining contract hours |
| `Q` | **Q3 projected consumption — the initiative's hours for this quarter** |
| `R`..`AE` | One column per team member, header in row 1 |

A person-column cell holds a **fraction of that initiative assigned to that person**, not hours and
not a share of the person's time. Fractions across one person's rows routinely sum above 1.0
(David's Q3: 1.0 + 0.5 + 0.85 + 0.35 + 0.25 = 2.95).

**Hours for a person on an initiative = `Q<row> × <person-col><row>`.** Column `K` divided by column
`J` is *not* the quarterly figure — it's contract burn-down, and using it produces numbers roughly
30% low.

## Summary block — anchored on the person's name appearing a second time

The person's name appears twice in their column: row 1 (initiative table header) and again at the
summary block header. Offsets below that second occurrence:

| Offset | Value | Formula |
|---|---|---|
| +1 | Customer SOW hours | `SUMPRODUCT($Q$2:$Q$32, <col>2:<col>32)` |
| +2 | Internal hours | `SUMPRODUCT($Q$33:$Q$41, ...)` |
| +3 | Gear roadmap hours | `SUMPRODUCT($Q$42:$Q$49, ...)` |
| +4 | Total allocated | `SUM` of the three above |
| +5 | Monthly average | total ÷ 3 |
| +6 | Customer count | `COUNT` over the SOW rows |

The SUMPRODUCT row ranges are **hardcoded in the workbook**, so inserting an initiative row without
extending them silently drops it from the totals. The script sidesteps this by recomputing from
column `H` types rather than trusting the ranges — which is exactly how such a break would show up
as a `discrepancies` entry.

## Capacity block — anchored on the "Q3 working days" label

Found by scanning columns A-T for a cell containing both "working" and "day".

| Row | Column K | Person column |
|---|---|---|
| anchor | Working days (63) | Raw available = `(days − holidays) × 8` (480) |
| anchor+1 | Holidays (3) | **Haircut — hand-typed, per person** (0.3) |
| anchor+2 | — | Effective = `raw × (1 − haircut)` (336) |
| anchor+3 | — | Allocated, mirrors the summary total (334) |
| anchor+4 | — | Slack = effective − allocated (2) |
| anchor+5 | — | Slack ÷ raw available |

**The haircut is the whole ballgame.** It is a bare constant with no formula and no derivation —
0.3 for David, 0.3 for Mehul, 0.1 for Daniel Lopez. Because the person's column has no PTO row, no
admin row and no meeting row, that one number absorbs **all** of it. Measured against Q3-2026
actuals it should have been ~0.41. See [forecast-model.md](forecast-model.md).

## Known defect: the working-day count

`K59` reads 63 working days for Q3-2026. **Jul 1 – Sep 30 2026 contains 66 weekdays.** Only two
readings are possible and they differ by 24 hours per person:

- 63 is simply wrong, and `(63 − 3) × 8 = 480` understates raw capacity.
- 63 already has the 3 holidays removed, in which case the formula subtracts them a second time
  and raw capacity should be `63 × 8 = 504`.

Under the second reading David's effective capacity is 353h rather than 336h, turning 2 hours of
quarterly slack into about 19. This is systematic across all 14 people in the tab, so it is worth
raising with whoever owns the workbook rather than silently patching. **Report it; don't pick a
reading.**

# Examples

David, Q3-2026 (column `Z`), verified against the workbook's own totals with zero discrepancies:

| Initiative | Type | Q3 hours | Fraction | His hours |
|---|---|---|---|---|
| University of Washington | SOW | 180 | 0.85 | 153 |
| GE Healthcare | SOW | 200 | 0.50 | 100 |
| Emory University | SOW | 50 | 1.00 | 50 |
| SSE Skills - Gear building | Internal | 60 | 0.35 | 21 |
| US Classification for DICOM | Gear RM | 40 | 0.25 | 10 |

Totals: 303 SOW + 21 internal + 10 gear RM = **334 allocated** against **336 effective**. Two hours
of slack for the entire quarter, 99.4% utilization.

Initiative names carry stray zero-width spaces (`​`) and trailing whitespace — strip before
matching. See [client-map.md](client-map.md).
