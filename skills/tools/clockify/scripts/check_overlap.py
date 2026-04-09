"""Check if a proposed time entry overlaps existing Clockify entries.

If overlap is detected, presents resolution options interactively and returns
the chosen outcome as JSON.

Usage:
    python3 check_overlap.py --start ISO_DATETIME --end ISO_DATETIME [--tz-offset N]

Output: JSON with status and final start/end times.

Status values:
    ok        — no overlap, original times returned
    added     — user chose to add anyway (original times returned)
    truncated — times trimmed to avoid overlap
    moved     — times shifted to a nearby free slot
    skipped   — user chose not to add
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

SCRIPTS_PATH = str(__file__).rsplit("/", 1)[0]
sys.path.insert(0, SCRIPTS_PATH)

from ClockifySdk import clockify_utils
from find_gaps import find_gaps
from get_day_entries import get_day_entries


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Check whether two time intervals overlap."""
    return a_start < b_end and a_end > b_start


def _find_conflicts(proposed_start: datetime, proposed_end: datetime, entries: list[dict]) -> list[dict]:
    """Return entries that overlap with the proposed interval.

    Args:
        proposed_start (datetime): Naive UTC start of proposed entry.
        proposed_end (datetime): Naive UTC end of proposed entry.
        entries (list[dict]): Existing day entries from get_day_entries.

    Returns:
        list[dict]: Subset of entries that conflict.
    """
    conflicts = []
    for e in entries:
        e_start = clockify_utils.decode_clockify_datestr(e["start_utc"])
        e_end = clockify_utils.decode_clockify_datestr(e["end_utc"])
        if _overlaps(proposed_start, proposed_end, e_start, e_end):
            conflicts.append(e)
    return conflicts


def _truncate_to_fit(
    proposed_start: datetime,
    proposed_end: datetime,
    entries: list[dict],
) -> tuple[datetime, datetime] | None:
    """Trim proposed interval to avoid all overlapping entries.

    Keeps start fixed and trims the end; if that leaves zero duration,
    tries trimming the start instead. Returns None if no valid window exists.

    Args:
        proposed_start (datetime): Naive UTC proposed start.
        proposed_end (datetime): Naive UTC proposed end.
        entries (list[dict]): All existing day entries.

    Returns:
        tuple[datetime, datetime] | None: Trimmed (start, end) or None if impossible.
    """
    # Collect all occupied intervals that overlap
    occupied = []
    for e in entries:
        e_start = clockify_utils.decode_clockify_datestr(e["start_utc"])
        e_end = clockify_utils.decode_clockify_datestr(e["end_utc"])
        if _overlaps(proposed_start, proposed_end, e_start, e_end):
            occupied.append((e_start, e_end))
    occupied.sort(key=lambda x: x[0])

    # Try keeping start fixed, shrink end to the earliest conflict start
    new_end = proposed_end
    for occ_start, _ in occupied:
        if occ_start > proposed_start:
            new_end = min(new_end, occ_start)

    if new_end > proposed_start:
        return proposed_start, new_end

    # Try keeping end fixed, push start to after the latest conflict end
    new_start = proposed_start
    for _, occ_end in occupied:
        if occ_end < proposed_end:
            new_start = max(new_start, occ_end)

    if proposed_end > new_start:
        return new_start, proposed_end

    return None


def _find_nearest_slot(
    proposed_start: datetime,
    proposed_end: datetime,
    target_date: date,
    tz_offset: int,
) -> tuple[datetime, datetime] | None:
    """Find the nearest free slot that fits the proposed duration.

    Args:
        proposed_start (datetime): Naive UTC proposed start.
        proposed_end (datetime): Naive UTC proposed end.
        target_date (date): The calendar date being searched.
        tz_offset (int): Hours offset from UTC.

    Returns:
        tuple[datetime, datetime] | None: (start, end) of nearest free slot or None.
    """
    duration_min = int((proposed_end - proposed_start).total_seconds() / 60)
    gaps = find_gaps(target_date, min_duration_min=duration_min, tz_offset=tz_offset)

    if not gaps:
        return None

    # Pick the gap whose start is closest to the proposed start
    def distance(gap: dict) -> int:
        gap_start = clockify_utils.decode_clockify_datestr(gap["start_utc"])
        return abs(int((gap_start - proposed_start).total_seconds()))

    nearest = min(gaps, key=distance)
    slot_start = clockify_utils.decode_clockify_datestr(nearest["start_utc"])
    slot_end = slot_start + timedelta(minutes=duration_min)
    return slot_start, slot_end


def _prompt_resolution(conflicts: list[dict]) -> str:
    """Print conflict summary and prompt user to choose a resolution.

    Args:
        conflicts (list[dict]): Conflicting entries to display.

    Returns:
        str: One of 'a', 'b', 'c', 'd'.
    """
    print("\nOverlap detected with existing entries:", file=sys.stderr)
    for c in conflicts:
        print(f"  [{c['start_utc']} – {c['end_utc']}] {c['description'][:60]}", file=sys.stderr)

    print("\nHow would you like to resolve this?", file=sys.stderr)
    print("  a) Add anyway (keep original times)", file=sys.stderr)
    print("  b) Truncate to fit (trim to largest open window)", file=sys.stderr)
    print("  c) Move to nearest free slot of same duration", file=sys.stderr)
    print("  d) Skip (don't add this entry)", file=sys.stderr)

    while True:
        choice = input("Choice [a/b/c/d]: ").strip().lower()
        if choice in ("a", "b", "c", "d"):
            return choice
        print("Please enter a, b, c, or d.", file=sys.stderr)


def check_overlap(
    proposed_start: datetime,
    proposed_end: datetime,
    tz_offset: int = -5,
) -> dict:
    """Check for overlaps and return resolution outcome.

    Args:
        proposed_start (datetime): Naive UTC proposed start.
        proposed_end (datetime): Naive UTC proposed end.
        tz_offset (int): Hours offset from UTC (default -5 for CDT).

    Returns:
        dict: Resolution result with status, start, end.
    """
    target_date = (proposed_start + timedelta(hours=tz_offset)).date()
    entries = get_day_entries(target_date, tz_offset)
    conflicts = _find_conflicts(proposed_start, proposed_end, entries)

    start_str = clockify_utils.encode_clockify_datestr(proposed_start)
    end_str = clockify_utils.encode_clockify_datestr(proposed_end)

    if not conflicts:
        return {"status": "ok", "start": start_str, "end": end_str}

    choice = _prompt_resolution(conflicts)

    if choice == "a":
        return {"status": "added", "start": start_str, "end": end_str}

    if choice == "b":
        result = _truncate_to_fit(proposed_start, proposed_end, entries)
        if result is None:
            print("No valid window found after truncation — skipping.", file=sys.stderr)
            return {"status": "skipped", "start": start_str, "end": end_str}
        new_start, new_end = result
        return {
            "status": "truncated",
            "start": clockify_utils.encode_clockify_datestr(new_start),
            "end": clockify_utils.encode_clockify_datestr(new_end),
        }

    if choice == "c":
        result = _find_nearest_slot(proposed_start, proposed_end, target_date, tz_offset)
        if result is None:
            print("No free slot found for this duration — skipping.", file=sys.stderr)
            return {"status": "skipped", "start": start_str, "end": end_str}
        new_start, new_end = result
        return {
            "status": "moved",
            "start": clockify_utils.encode_clockify_datestr(new_start),
            "end": clockify_utils.encode_clockify_datestr(new_end),
        }

    return {"status": "skipped", "start": start_str, "end": end_str}


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Check if a proposed time entry overlaps existing entries.")
    parser.add_argument("--start", required=True, help="UTC start datetime (ISO 8601)")
    parser.add_argument("--end", required=True, help="UTC end datetime (ISO 8601)")
    parser.add_argument("--tz-offset", type=int, default=-5, help="Hours offset from UTC. Defaults to -5 (CDT).")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    proposed_start = clockify_utils.decode_clockify_datestr(args.start)
    proposed_end = clockify_utils.decode_clockify_datestr(args.end)
    result = check_overlap(proposed_start, proposed_end, args.tz_offset)
    print(json.dumps(result, indent=2))
