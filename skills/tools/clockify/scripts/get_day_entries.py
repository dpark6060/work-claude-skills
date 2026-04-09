"""Get all Clockify time entries for a given calendar day, sorted by start time.

Usage:
    python3 get_day_entries.py [--date YYYY-MM-DD] [--tz-offset N]

Output: JSON array of entries to stdout.
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

from ClockifySdk import clockify_utils
from ClockifySdk.clockify_sdk import Clockify


def get_day_entries(target_date: date, tz_offset: int) -> list[dict]:
    """Fetch all entries for a calendar day, sorted by start time.

    Args:
        target_date (date): The local calendar date to query.
        tz_offset (int): Hours offset from UTC (e.g. -5 for CDT).

    Returns:
        list[dict]: Sorted list of entry dicts with id, description, timestamps,
            duration_min, project_id, task_id, and billable.
    """
    cl = Clockify(api_key=os.environ["CLOCKIFY_API"])
    cl.get_flywheel_workspace()

    day_start_local = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    day_end_local = day_start_local + timedelta(days=1)

    day_start_utc = day_start_local - timedelta(hours=tz_offset)
    day_end_utc = day_end_local - timedelta(hours=tz_offset)

    entries = cl.get_workspace_time_entries(
        start=clockify_utils.encode_clockify_datestr(day_start_utc),
        end=clockify_utils.encode_clockify_datestr(day_end_utc),
    )

    entries.sort(key=lambda e: e.start_timestamp)

    results = []
    for e in entries:
        start_dt = e.start_timestamp
        end_dt = e.end_timestamp
        duration_min = int((end_dt - start_dt).total_seconds() / 60)
        results.append({
            "id": e.id,
            "description": e.description,
            "start_utc": clockify_utils.encode_clockify_datestr(start_dt),
            "end_utc": clockify_utils.encode_clockify_datestr(end_dt),
            "duration_min": duration_min,
            "project_id": e.projectId,
            "task_id": e.taskId,
            "billable": e.billable,
        })
    return results


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Get Clockify entries for a calendar day.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Date to query (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--tz-offset",
        type=int,
        default=-5,
        help="Hours offset from UTC for local timezone (e.g. -5 for CDT). Defaults to -5.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    target_date = date.fromisoformat(args.date)
    entries = get_day_entries(target_date, args.tz_offset)
    print(json.dumps(entries, indent=2))
