"""Add independent random jitter to the start and end of a proposed time entry.

Jitter magnitude scales with entry duration so short entries don't get
disproportionate offsets. Start and end are jittered independently.

Usage:
    python3 add_jitter.py --start ISO_DATETIME --end ISO_DATETIME

Output: JSON with jittered start/end and metadata.
"""
import argparse
import json
import random
import sys
from datetime import datetime, timedelta

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

from ClockifySdk import clockify_utils


def compute_jitter_max(duration_minutes: int) -> int:
    """Compute maximum jitter in minutes, scaled proportionally to duration.

    Args:
        duration_minutes (int): The entry duration in minutes.

    Returns:
        int: Maximum jitter in minutes (capped at 15, minimum 1).
    """
    return max(1, min(15, int(duration_minutes * 0.12)))


def apply_jitter(start_dt: datetime, end_dt: datetime) -> tuple[datetime, datetime, int]:
    """Apply independent random jitter to start and end datetimes.

    Retries up to 10 times if jitter would cause end <= start (only possible
    for very short entries at max jitter).

    Args:
        start_dt (datetime): Proposed start as naive UTC datetime.
        end_dt (datetime): Proposed end as naive UTC datetime.

    Returns:
        tuple[datetime, datetime, int]: Jittered (start, end) and jitter_max used.
    """
    duration_min = int((end_dt - start_dt).total_seconds() / 60)
    jitter_max = compute_jitter_max(duration_min)

    for _ in range(10):
        start_offset = random.randint(-jitter_max, jitter_max)
        end_offset = random.randint(-jitter_max, jitter_max)
        new_start = start_dt + timedelta(minutes=start_offset)
        new_end = end_dt + timedelta(minutes=end_offset)
        if new_end > new_start:
            return new_start, new_end, jitter_max

    # Fallback: keep start fixed, only jitter end positively
    end_offset = random.randint(0, jitter_max)
    return start_dt, end_dt + timedelta(minutes=end_offset), jitter_max


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Add scaled jitter to a time entry.")
    parser.add_argument("--start", required=True, help="UTC start datetime (ISO 8601, e.g. 2026-04-09T18:00:00Z)")
    parser.add_argument("--end", required=True, help="UTC end datetime (ISO 8601, e.g. 2026-04-09T19:00:00Z)")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    start_dt = clockify_utils.decode_clockify_datestr(args.start)
    end_dt = clockify_utils.decode_clockify_datestr(args.end)
    original_duration = int((end_dt - start_dt).total_seconds() / 60)

    new_start, new_end, jitter_max = apply_jitter(start_dt, end_dt)
    jittered_duration = int((new_end - new_start).total_seconds() / 60)

    print(json.dumps({
        "start": clockify_utils.encode_clockify_datestr(new_start),
        "end": clockify_utils.encode_clockify_datestr(new_end),
        "original_duration_min": original_duration,
        "jittered_duration_min": jittered_duration,
        "jitter_max_applied": jitter_max,
    }, indent=2))
