"""Find free time slots on a given day that could fit a minimum duration.

Usage:
    python3 find_gaps.py [--date YYYY-MM-DD] [--min-duration-min N] [--tz-offset N]

Output: JSON array of free slots sorted by start time.
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

from ClockifySdk import clockify_utils

# Import sibling script as a module
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])
from get_day_entries import get_day_entries

# Working day boundaries in local time (used to bound gap search)
WORKDAY_START_HOUR = 8
WORKDAY_END_HOUR = 20


def find_gaps(target_date: date, min_duration_min: int, tz_offset: int) -> list[dict]:
    """Find free time slots on a calendar day that fit a minimum duration.

    Args:
        target_date (date): The local calendar date to check.
        min_duration_min (int): Minimum gap size in minutes to include.
        tz_offset (int): Hours offset from UTC (e.g. -5 for CDT).

    Returns:
        list[dict]: Free slots as dicts with start_utc, end_utc, duration_min.
    """
    entries = get_day_entries(target_date, tz_offset)

    # Compute workday boundaries in UTC
    workday_start_local = datetime(target_date.year, target_date.month, target_date.day, WORKDAY_START_HOUR, 0, 0)
    workday_end_local = datetime(target_date.year, target_date.month, target_date.day, WORKDAY_END_HOUR, 0, 0)
    workday_start_utc = workday_start_local - timedelta(hours=tz_offset)
    workday_end_utc = workday_end_local - timedelta(hours=tz_offset)

    # Build sorted list of (start_utc, end_utc) intervals from existing entries
    occupied = []
    for e in entries:
        s = clockify_utils.decode_clockify_datestr(e["start_utc"])
        t = clockify_utils.decode_clockify_datestr(e["end_utc"])
        occupied.append((s, t))

    occupied.sort(key=lambda x: x[0])

    # Walk the day, collecting gaps
    gaps = []
    cursor = workday_start_utc

    for entry_start, entry_end in occupied:
        if entry_start > cursor:
            gap_duration = int((entry_start - cursor).total_seconds() / 60)
            if gap_duration >= min_duration_min:
                gaps.append({
                    "start_utc": clockify_utils.encode_clockify_datestr(cursor),
                    "end_utc": clockify_utils.encode_clockify_datestr(entry_start),
                    "duration_min": gap_duration,
                })
        cursor = max(cursor, entry_end)

    # Gap after last entry until workday end
    if workday_end_utc > cursor:
        gap_duration = int((workday_end_utc - cursor).total_seconds() / 60)
        if gap_duration >= min_duration_min:
            gaps.append({
                "start_utc": clockify_utils.encode_clockify_datestr(cursor),
                "end_utc": clockify_utils.encode_clockify_datestr(workday_end_utc),
                "duration_min": gap_duration,
            })

    return gaps


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Find free time slots on a given day.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date to check (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--min-duration-min", type=int, default=60, help="Minimum slot size in minutes. Defaults to 60.")
    parser.add_argument("--tz-offset", type=int, default=-5, help="Hours offset from UTC. Defaults to -5 (CDT).")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    target_date = date.fromisoformat(args.date)
    gaps = find_gaps(target_date, args.min_duration_min, args.tz_offset)
    print(json.dumps(gaps, indent=2))
