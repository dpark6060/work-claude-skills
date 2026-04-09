"""Convert a human-friendly time description to a UTC ISO datetime string.

Usage:
    python3 parse_time_spec.py --spec "DESCRIPTION" [--tz-offset N]

Handles:
    "now"                     → current UTC moment
    "today" / "yesterday"     → that date at noon local
    "morning"                 → 9am local today
    "afternoon"               → 2pm local today
    "evening"                 → 6pm local today
    "yesterday morning"       → 9am local yesterday
    "yesterday afternoon"     → 2pm local yesterday
    "2pm" / "9:15am"          → today at that local time
    "14:30"                   → today at 14:30 local
    "2pm CDT" / "3pm EST"     → that time in the named timezone
    "2 hours ago"             → 2 hours before now (UTC)
    "45 minutes ago"          → 45 minutes before now (UTC)

Output: JSON with utc_iso, local_str, and interpreted_as.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

# Named timezone offsets (hours from UTC, standard time conventions used loosely)
NAMED_TZ_OFFSETS: dict[str, int] = {
    "utc": 0,
    "gmt": 0,
    "est": -5,
    "edt": -4,
    "cst": -6,
    "cdt": -5,
    "mst": -7,
    "mdt": -6,
    "pst": -8,
    "pdt": -7,
}

# Canonical label for display when converting offset back to a name
_OFFSET_TO_LABEL: dict[int, str] = {0: "UTC", -4: "EDT", -5: "CDT", -6: "CST", -7: "MDT", -8: "PDT"}

# Time-of-day labels → local hour
TIME_OF_DAY: dict[str, int] = {
    "morning": 9,
    "afternoon": 14,
    "evening": 18,
    "noon": 12,
    "midnight": 0,
}


def _now_utc() -> datetime:
    """Return current time as a naive UTC datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _local_to_utc(local_dt: datetime, tz_offset: int) -> datetime:
    """Convert a naive local datetime to naive UTC using a fixed offset.

    Args:
        local_dt (datetime): Naive local datetime.
        tz_offset (int): Hours offset from UTC (e.g. -5 for CDT).

    Returns:
        datetime: Naive UTC datetime.
    """
    return local_dt - timedelta(hours=tz_offset)


def _utc_to_local_str(utc_dt: datetime, tz_offset: int) -> str:
    """Format a naive UTC datetime as a local time string.

    Args:
        utc_dt (datetime): Naive UTC datetime.
        tz_offset (int): Hours offset from UTC.

    Returns:
        str: Human-readable local time string.
    """
    local_dt = utc_dt + timedelta(hours=tz_offset)
    tz_label = _OFFSET_TO_LABEL.get(tz_offset, f"UTC{tz_offset:+d}")
    return local_dt.strftime(f"%Y-%m-%d %-I:%M %p {tz_label}")


def _parse_clock_time(time_str: str, tz_offset: int) -> int | None:
    """Parse a clock time string to an hour offset from midnight (local).

    Supports: "2pm", "9:15am", "14:30", "2:30pm".

    Args:
        time_str (str): The clock time string to parse.
        tz_offset (int): Not used here, kept for interface consistency.

    Returns:
        int | None: Minutes since midnight (local), or None if unrecognized.
    """
    time_str = time_str.strip().lower()

    # "14:30" or "9:15"
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", time_str)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))

    # "2pm" or "9am"
    m = re.fullmatch(r"(\d{1,2})(am|pm)", time_str)
    if m:
        h = int(m.group(1))
        if m.group(2) == "pm" and h != 12:
            h += 12
        if m.group(2) == "am" and h == 12:
            h = 0
        return h * 60

    # "2:30pm"
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(am|pm)", time_str)
    if m:
        h = int(m.group(1))
        mins = int(m.group(2))
        if m.group(3) == "pm" and h != 12:
            h += 12
        if m.group(3) == "am" and h == 12:
            h = 0
        return h * 60 + mins

    return None


def parse_time_spec(spec: str, tz_offset: int) -> dict:
    """Parse a human-friendly time spec into a UTC ISO datetime.

    Args:
        spec (str): Human description of a time (e.g. "yesterday afternoon").
        tz_offset (int): Default local timezone offset from UTC.

    Returns:
        dict: With keys utc_iso (str), local_str (str), interpreted_as (str).

    Raises:
        ValueError: If the spec cannot be interpreted.
    """
    s = spec.strip().lower()
    now_utc = _now_utc()

    # "now"
    if s == "now":
        return {
            "utc_iso": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(now_utc, tz_offset),
            "interpreted_as": "now",
        }

    # "X hours ago" / "X minutes ago"
    m = re.fullmatch(r"(\d+)\s+hours?\s+ago", s)
    if m:
        result_utc = now_utc - timedelta(hours=int(m.group(1)))
        return {
            "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(result_utc, tz_offset),
            "interpreted_as": spec,
        }

    m = re.fullmatch(r"(\d+)\s+minutes?\s+ago", s)
    if m:
        result_utc = now_utc - timedelta(minutes=int(m.group(1)))
        return {
            "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(result_utc, tz_offset),
            "interpreted_as": spec,
        }

    # Determine the base date: "yesterday ...", "today ...", or today by default
    base_date_offset = 0  # days back from today
    remaining = s

    if remaining.startswith("yesterday"):
        base_date_offset = 1
        remaining = remaining[len("yesterday"):].strip()
    elif remaining.startswith("today"):
        remaining = remaining[len("today"):].strip()

    today_local = (now_utc + timedelta(hours=tz_offset)).date()
    base_date = today_local - timedelta(days=base_date_offset)

    # Try timezone-qualified clock time: "2pm CDT", "14:30 UTC"
    for tz_name, tz_off in NAMED_TZ_OFFSETS.items():
        pattern = rf"^(.+?)\s+{re.escape(tz_name)}$"
        m = re.fullmatch(pattern, remaining)
        if m:
            minutes_since_midnight = _parse_clock_time(m.group(1).strip(), tz_off)
            if minutes_since_midnight is not None:
                local_dt = datetime(base_date.year, base_date.month, base_date.day) + timedelta(minutes=minutes_since_midnight)
                result_utc = _local_to_utc(local_dt, tz_off)
                return {
                    "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "local_str": _utc_to_local_str(result_utc, tz_off),
                    "interpreted_as": spec,
                }

    # Time-of-day label: "morning", "afternoon", "evening"
    if remaining in TIME_OF_DAY:
        hour = TIME_OF_DAY[remaining]
        local_dt = datetime(base_date.year, base_date.month, base_date.day, hour, 0, 0)
        result_utc = _local_to_utc(local_dt, tz_offset)
        return {
            "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(result_utc, tz_offset),
            "interpreted_as": spec,
        }

    # Plain clock time: "2pm", "14:30", "9:15am"
    minutes_since_midnight = _parse_clock_time(remaining, tz_offset)
    if minutes_since_midnight is not None:
        local_dt = datetime(base_date.year, base_date.month, base_date.day) + timedelta(minutes=minutes_since_midnight)
        result_utc = _local_to_utc(local_dt, tz_offset)
        return {
            "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(result_utc, tz_offset),
            "interpreted_as": spec,
        }

    # "today" / "yesterday" with no time → noon local
    if not remaining:
        local_dt = datetime(base_date.year, base_date.month, base_date.day, 12, 0, 0)
        result_utc = _local_to_utc(local_dt, tz_offset)
        return {
            "utc_iso": result_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "local_str": _utc_to_local_str(result_utc, tz_offset),
            "interpreted_as": f"{'yesterday' if base_date_offset else 'today'} at noon",
        }

    raise ValueError(f"Could not interpret time spec: {spec!r}")


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Parse a human time description to UTC ISO datetime.")
    parser.add_argument("--spec", required=True, help='Time description, e.g. "yesterday afternoon" or "2pm CDT"')
    parser.add_argument("--tz-offset", type=int, default=-5, help="Default local timezone offset from UTC. Defaults to -5 (CDT).")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    try:
        result = parse_time_spec(args.spec, args.tz_offset)
        print(json.dumps(result, indent=2))
    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
