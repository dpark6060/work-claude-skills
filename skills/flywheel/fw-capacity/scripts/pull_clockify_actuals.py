#!/usr/bin/env python3
"""Pull logged hours for a date range and aggregate by project and task.

Run it, don't read it. Needs CLOCKIFY_API in the environment and the clockify
skill's vendored SDK:

    /Users/davidparker/.claude/skills/clockify/.venv/bin/python \
        ${CLAUDE_SKILL_DIR}/scripts/pull_clockify_actuals.py \
        --start 2026-07-01 --end 2026-09-18 [--out <path.json>]

`--end` is exclusive. Prints a summary table and optionally writes JSON.

Aggregates are checked against a sum invariant before anything is reported --
past runs of this skill family have twice shipped double-counting bugs in ad-hoc
aggregation snippets, so the totals verify themselves here instead.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "/Users/davidparker/.claude/skills/clockify/scripts")

from ClockifySdk.clockify_sdk import Clockify  # noqa: E402

PAGE_SIZE = 200


def iso_z(d: dt.date) -> str:
    return f"{d.isoformat()}T00:00:00Z"


def fetch_entries(cl: Clockify, start: dt.date, end: dt.date) -> list[dict]:
    entries, page = [], 1
    endpoint = f"/workspaces/{cl.workspaceId}/user/{cl.userId}/time-entries"
    while True:
        batch = cl.client.make_call(
            "get",
            endpoint,
            {
                "start": iso_z(start),
                "end": iso_z(end),
                "hydrated": "true",
                "page": page,
                "page-size": PAGE_SIZE,
            },
        )
        if isinstance(batch, dict):
            batch = batch.get("timeEntries", [])
        if not batch:
            break
        entries.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        page += 1
        if page > 100:
            print("warning: stopped at 100 pages", file=sys.stderr)
            break
    return entries


def minutes_of(entry: dict) -> float:
    interval = entry.get("timeInterval") or {}
    start, end = interval.get("start"), interval.get("end")
    if not start or not end:
        return 0.0
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    delta = dt.datetime.strptime(end, fmt) - dt.datetime.strptime(start, fmt)
    return delta.total_seconds() / 60.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, type=dt.date.fromisoformat)
    ap.add_argument("--end", required=True, type=dt.date.fromisoformat, help="exclusive")
    ap.add_argument("--out", type=Path)
    ap.add_argument(
        "--entries",
        action="store_true",
        help="also emit per-entry records (date, project, task, description, hours)",
    )
    args = ap.parse_args()

    key = os.environ.get("CLOCKIFY_API")
    if not key:
        print("error: CLOCKIFY_API not set", file=sys.stderr)
        raise SystemExit(1)

    cl = Clockify(api_key=key)
    entries = fetch_entries(cl, args.start, args.end)
    if not entries:
        print("no entries in range")
        raise SystemExit(0)

    by_project: dict[str, float] = defaultdict(float)
    by_task: dict[tuple[str, str], float] = defaultdict(float)
    by_week: dict[str, float] = defaultdict(float)
    billable = nonbillable = 0.0
    undated = 0
    records = []

    for e in entries:
        mins = minutes_of(e)
        if not mins:
            undated += 1
            continue
        project = ((e.get("project") or {}).get("name")) or "(no project)"
        task = ((e.get("task") or {}).get("name")) or "(no task)"
        by_project[project] += mins
        by_task[(project, task)] += mins
        start = (e.get("timeInterval") or {}).get("start", "")
        if start:
            day = dt.date.fromisoformat(start[:10])
            by_week[(day - dt.timedelta(days=day.weekday())).isoformat()] += mins
        if e.get("billable"):
            billable += mins
        else:
            nonbillable += mins
        if args.entries:
            records.append(
                {
                    "date": start[:10],
                    "project": project,
                    "task": task,
                    "description": (e.get("description") or "").strip(),
                    "billable": bool(e.get("billable")),
                    "hours": round(mins / 60, 3),
                }
            )

    total = sum(by_project.values())

    # Sanity invariant: every split must sum back to the same total.
    for label, split in (
        ("task", sum(by_task.values())),
        ("week", sum(by_week.values())),
        ("billable", billable + nonbillable),
    ):
        if abs(split - total) > 0.01:
            print(
                f"error: {label} split sums to {split / 60:.2f}h but project split "
                f"sums to {total / 60:.2f}h -- aggregation is wrong, not reporting",
                file=sys.stderr,
            )
            raise SystemExit(1)

    h = lambda m: round(m / 60, 2)  # noqa: E731
    result = {
        "range": {"start": args.start.isoformat(), "end": args.end.isoformat()},
        "entry_count": len(entries),
        "entries_without_end": undated,
        "total_hours": h(total),
        "billable_hours": h(billable),
        "nonbillable_hours": h(nonbillable),
        "by_project": {k: h(v) for k, v in sorted(by_project.items(), key=lambda kv: -kv[1])},
        "by_task": [
            {"project": p, "task": t, "hours": h(v)}
            for (p, t), v in sorted(by_task.items(), key=lambda kv: -kv[1])
        ],
        "by_week": {k: h(v) for k, v in sorted(by_week.items())},
    }
    if args.entries:
        if abs(sum(r["hours"] for r in records) - total / 60) > 0.05:
            print("error: per-entry records do not sum to the total", file=sys.stderr)
            raise SystemExit(1)
        result["entries"] = sorted(records, key=lambda r: (r["date"], r["project"]))

    print(f"{args.start} .. {args.end} (exclusive) | {len(entries)} entries | {h(total)}h")
    if undated:
        print(f"  ({undated} entries had no end time and were skipped)")
    print(f"  billable {h(billable)}h / non-billable {h(nonbillable)}h\n")
    print(f"{'project':<42} {'hours':>8}")
    for name, mins in sorted(by_project.items(), key=lambda kv: -kv[1]):
        print(f"{name[:42]:<42} {h(mins):>8}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
