#!/usr/bin/env python3
"""Extract one person's quarterly allocation from the SSE capacity planning workbook.

Run it, don't read it:

    uv run --with openpyxl python ${CLAUDE_SKILL_DIR}/scripts/read_capacity_sheet.py \
        --workbook <path.xlsx> --person Parker [--quarter Q3-2026] [--out <path.json>]

Writes JSON to --out (default: stdout). Exit 0 on success, 1 on any structural
surprise (person column missing, anchor row missing, sheet reshaped).

The workbook's own totals are read back and compared against a recomputation from
the per-initiative rows. Mismatches land in `discrepancies` rather than being
silently smoothed over -- a mismatch usually means someone hand-edited a total.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import openpyxl

TAB_RE = re.compile(r"^Q(?P<q>[1-4])-(?P<year>20\d{2})-SSECapacityPlan$")
HOURS_HEADER = "projected consumption"
WORKDAYS_LABEL = ("working", "day")
HOURS_PER_DAY = 8

# Offsets below the summary header row (the second row carrying the person's name).
SUMMARY_OFFSETS = {
    "sow_hours": 1,
    "internal_hours": 2,
    "gear_rm_hours": 3,
    "allocated_hours": 4,
    "monthly_average": 5,
    "customer_count": 6,
}


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def current_quarter(today: dt.date) -> str:
    return f"Q{(today.month - 1) // 3 + 1}-{today.year}"


def pick_tab(sheetnames: list[str], quarter: str | None) -> str:
    tabs = {}
    for name in sheetnames:
        m = TAB_RE.match(name)
        if m:
            tabs[f"Q{m['q']}-{m['year']}"] = name
    if not tabs:
        fail("no sheet matching 'Q<n>-<year>-SSECapacityPlan' found")
    if quarter:
        if quarter not in tabs:
            fail(f"no tab for {quarter}; available: {', '.join(sorted(tabs))}")
        return tabs[quarter]
    wanted = current_quarter(dt.date.today())
    if wanted in tabs:
        return tabs[wanted]
    latest = sorted(tabs, key=lambda q: (q.split("-")[1], q.split("-")[0]))[-1]
    print(f"warning: no tab for {wanted}, falling back to {latest}", file=sys.stderr)
    return tabs[latest]


def find_person_columns(ws, person: str) -> list[int]:
    """Rows where this person's name appears as a header.

    Returns every such row, so the caller can tell the initiative table (first)
    from the summary block (second, when the tab has one).
    """
    hits = []
    target = person.strip().lower()
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.strip().lower() == target:
                hits.append((cell.row, cell.column))
    if not hits:
        fail(f"'{person}' appears in no header cell on this tab")
    cols = {c for _, c in hits}
    if len(cols) > 1:
        fail(f"'{person}' appears in multiple columns {sorted(cols)}; ambiguous")
    return sorted(r for r, _ in hits)


def find_hours_column(ws) -> tuple[int, int]:
    """(header_row, column) of the per-initiative quarterly hours column.

    Scans the first few rows rather than assuming row 1 -- the header row has
    moved between quarterly tabs.
    """
    for row in ws.iter_rows(min_row=1, max_row=6):
        for cell in row:
            if isinstance(cell.value, str) and HOURS_HEADER in cell.value.lower():
                return cell.row, cell.column
    fail(
        f"no header containing '{HOURS_HEADER}' in the first 6 rows. This tab does not use "
        "the current layout -- see references/spreadsheet-layout.md; earlier quarters differ "
        "structurally and are not supported."
    )


def find_workdays_row(ws) -> int | None:
    """Anchor row of the capacity block, or None when this tab has no such block."""
    for row in ws.iter_rows(min_col=1, max_col=20):
        for cell in row:
            if isinstance(cell.value, str):
                low = cell.value.lower()
                if all(tok in low for tok in WORKDAYS_LABEL):
                    return cell.row
    return None


def num(value) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True, type=Path)
    ap.add_argument("--person", required=True)
    ap.add_argument("--quarter", help="e.g. Q3-2026; defaults to the calendar quarter")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    if not args.workbook.exists():
        fail(f"workbook not found: {args.workbook}")

    wb = openpyxl.load_workbook(args.workbook, data_only=True)
    tab = pick_tab(wb.sheetnames, args.quarter)
    ws = wb[tab]

    name_rows = find_person_columns(ws, args.person)
    col = next(
        c.column
        for c in ws[name_rows[0]]
        if isinstance(c.value, str) and c.value.strip().lower() == args.person.strip().lower()
    )
    header_row, hours_col = find_hours_column(ws)
    workdays_row = find_workdays_row(ws)
    summary_row = name_rows[-1] if len(name_rows) > 1 else None
    last_initiative_row = workdays_row or summary_row or ws.max_row + 1

    # Per-initiative allocations: every row carrying a fraction in the person's column.
    allocations = []
    for row in range(header_row + 1, last_initiative_row):
        frac = num(ws.cell(row=row, column=col).value)
        if not frac:
            continue
        initiative = ws.cell(row=row, column=9).value  # column I
        if not isinstance(initiative, str) or not initiative.strip():
            continue
        quarter_hours = num(ws.cell(row=row, column=hours_col).value) or 0.0
        allocations.append(
            {
                "row": row,
                "type": (ws.cell(row=row, column=8).value or "").strip(),  # column H
                "initiative": initiative.strip(),
                "quarter_hours": round(quarter_hours, 2),
                "fraction": frac,
                "my_hours": round(quarter_hours * frac, 2),
            }
        )
    if not allocations:
        fail(f"'{args.person}' has a column but no allocations on {tab}")

    by_type: dict[str, float] = {}
    for a in allocations:
        by_type[a["type"]] = round(by_type.get(a["type"], 0.0) + a["my_hours"], 2)
    allocated = round(sum(a["my_hours"] for a in allocations), 2)

    discrepancies = []
    sheet_values = {}

    # Capacity block. Absent on older tabs -- degrade rather than fail, since the
    # allocations above are independently useful.
    working_days = holidays = haircut = raw_available = effective = None
    if workdays_row:
        working_days = num(ws.cell(row=workdays_row, column=11).value)  # column K
        holidays = num(ws.cell(row=workdays_row + 1, column=11).value) or 0.0
        haircut = num(ws.cell(row=workdays_row + 1, column=col).value)
    if working_days is None or haircut is None:
        discrepancies.append(
            "capacity block not found or unreadable on this tab -- allocations are complete "
            "but effective capacity, slack, and utilization are unavailable. The capacity "
            "block moves between quarters; see references/spreadsheet-layout.md."
        )
    else:
        raw_available = round((working_days - holidays) * HOURS_PER_DAY, 2)
        effective = round(raw_available * (1 - haircut), 2)

    # Cross-check against the workbook's own totals.
    if summary_row:
        for key, offset in SUMMARY_OFFSETS.items():
            sheet_values[key] = num(ws.cell(row=summary_row + offset, column=col).value)
        stated = sheet_values.get("allocated_hours")
        if stated is not None and abs(stated - allocated) > 0.5:
            discrepancies.append(
                f"workbook total {stated} != recomputed {allocated} "
                f"(diff {round(stated - allocated, 2)}h) -- a total may be hand-edited"
            )
    if workdays_row:
        sheet_values["raw_available"] = num(ws.cell(row=workdays_row, column=col).value)
        if sheet_values["raw_available"] not in (None, raw_available):
            discrepancies.append(
                f"workbook raw available {sheet_values['raw_available']} != "
                f"recomputed {raw_available}; hours-per-day may not be {HOURS_PER_DAY}"
            )

    m = TAB_RE.match(tab)
    result = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "source": {
            "workbook": str(args.workbook),
            "tab": tab,
            "person": args.person,
            "column": ws.cell(row=1, column=col).column_letter,
        },
        "quarter": {
            "label": f"Q{m['q']}-{m['year']}",
            "working_days": working_days,
            "holidays": holidays,
        },
        "capacity": {
            "raw_available": raw_available,
            "haircut": haircut,
            "haircut_hours": round(raw_available * haircut, 2) if raw_available else None,
            "effective": effective,
            "allocated": allocated,
            "slack": round(effective - allocated, 2) if effective else None,
            "utilization": round(allocated / effective, 4) if effective else None,
        },
        "by_type": by_type,
        "allocations": sorted(allocations, key=lambda a: -a["my_hours"]),
        "sheet_values": sheet_values,
        "discrepancies": discrepancies,
    }

    payload = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n")
        print(f"wrote {args.out}")
    else:
        print(payload)

    for d in discrepancies:
        print(f"warning: {d}", file=sys.stderr)


if __name__ == "__main__":
    main()
