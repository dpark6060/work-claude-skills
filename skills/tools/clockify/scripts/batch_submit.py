"""Submit a batch of Clockify time entries from a JSON intent file.

The intent file describes entries with human-readable hints
(client / project / task as substrings), which are resolved against the
local workspace cache (built by refresh_cache.py). Defaults to dry-run —
pass --yes to actually post.

Usage:
    python3 batch_submit.py PATH_TO_INTENT_JSON [--yes] [--tz-offset N]
                            [--allow-conflicts]

Intent file schema (top level):
    timezone_offset_hours : int   (optional; --tz-offset overrides)
    default_billable      : bool  (optional; per-entry billable overrides)
    entries               : list  (see _validate_entry for required fields)
"""
import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

SCRIPTS_PATH = str(Path(__file__).parent)
sys.path.insert(0, SCRIPTS_PATH)

from ClockifySdk.clockify_sdk import Clockify
from ClockifySdk.Models.time_entry import TimeEntryInput

from get_day_entries import get_day_entries
from lookup import LookupError as ResolveError
from lookup import load_workspace, resolve


class IntentError(Exception):
    """Raised when the intent JSON is malformed."""


# ---------------------------------------------------------------------------
# Parsing & resolution
# ---------------------------------------------------------------------------


def _validate_entry(entry: dict, index: int) -> None:
    """Check that an intent entry has all required fields.

    Args:
        entry (dict): One element of `entries` in the intent file.
        index (int): Position in the entries list (for error messages).

    Raises:
        IntentError: If any required field is missing or the entry mixes
            resolved IDs with name hints.
    """
    required = ("date", "start", "end", "description")
    missing = [k for k in required if k not in entry]
    if missing:
        raise IntentError(f"entry {index}: missing fields {missing}")

    has_ids = "project_id" in entry and "task_id" in entry
    has_hints = "client" in entry
    if not (has_ids or has_hints):
        raise IntentError(
            f"entry {index}: must specify either 'client' (with optional 'project'/'task') "
            "or both 'project_id' and 'task_id'"
        )
    if has_ids and has_hints:
        raise IntentError(
            f"entry {index}: cannot mix 'project_id'/'task_id' with 'client'/'project'/'task'"
        )


def _build_naive_utc(date_str: str, time_str: str, tz_offset_hours: int) -> datetime:
    """Convert a local date+time to a naive UTC datetime.

    Args:
        date_str (str): ISO date, e.g. "2026-05-04".
        time_str (str): Local time in HH:MM (24h).
        tz_offset_hours (int): Hours offset from UTC for the local time.

    Returns:
        datetime: Naive UTC datetime suitable for `TimeEntryInput`.
    """
    local = datetime.fromisoformat(f"{date_str}T{time_str}:00")
    return local - timedelta(hours=tz_offset_hours)


def resolve_entry(entry: dict, cache: dict) -> dict:
    """Resolve client/project/task hints in an intent entry to IDs.

    Args:
        entry (dict): One intent entry.
        cache (dict): Workspace cache from `load_workspace()`.

    Returns:
        dict: `{"project_id", "task_id", "client_name", "project_name",
            "task_name"}` for display and submission.

    Raises:
        ResolveError: If any hint is ambiguous or unmatched.
    """
    if "project_id" in entry:
        return {
            "project_id": entry["project_id"],
            "task_id": entry["task_id"],
            "client_name": "(by id)",
            "project_name": entry["project_id"],
            "task_name": entry["task_id"],
        }

    resolved = resolve(
        client_hint=entry["client"],
        project_hint=entry.get("project"),
        task_hint=entry.get("task"),
        cache=cache,
    )
    project = resolved["project"]
    task = resolved["task"]
    return {
        "project_id": project["id"] if project else "",
        "task_id": task["id"] if task else "",
        "client_name": resolved["client"]["name"],
        "project_name": project["name"] if project else "",
        "task_name": task["name"] if task else "",
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_batch_overlaps(rows: list[dict]) -> list[str]:
    """Detect overlaps between entries within the batch itself.

    Args:
        rows (list[dict]): Prepared rows (each has `start_utc`, `end_utc`).

    Returns:
        list[str]: Error messages — one per overlapping pair.
    """
    errors = []
    by_date: dict[str, list[tuple[int, datetime, datetime]]] = {}
    for i, row in enumerate(rows):
        by_date.setdefault(row["date"], []).append((i, row["start_utc"], row["end_utc"]))

    for date_str, items in by_date.items():
        items.sort(key=lambda x: x[1])
        for j in range(1, len(items)):
            prev_i, _, prev_end = items[j - 1]
            cur_i, cur_start, _ = items[j]
            if cur_start < prev_end:
                errors.append(
                    f"in-batch overlap on {date_str}: entry {prev_i} and entry {cur_i}"
                )
    return errors


def validate_external_overlaps(rows: list[dict], tz_offset: int) -> list[str]:
    """Detect overlaps between batch rows and entries already in Clockify.

    Args:
        rows (list[dict]): Prepared rows (each has `date`, `start_utc`, `end_utc`).
        tz_offset (int): Hours offset from UTC for the local timezone.

    Returns:
        list[str]: Error messages — one per conflicting existing entry.
    """
    errors = []
    by_date: dict[str, list[tuple[int, datetime, datetime]]] = {}
    for i, row in enumerate(rows):
        by_date.setdefault(row["date"], []).append((i, row["start_utc"], row["end_utc"]))

    for date_str, items in by_date.items():
        target_date = date.fromisoformat(date_str)
        existing = get_day_entries(target_date, tz_offset)
        for i, start, end in items:
            for e in existing:
                e_start = datetime.strptime(e["start_utc"], "%Y-%m-%dT%H:%M:%SZ")
                e_end = datetime.strptime(e["end_utc"], "%Y-%m-%dT%H:%M:%SZ")
                if start < e_end and end > e_start:
                    errors.append(
                        f"entry {i} on {date_str} ({start.time()}-{end.time()} UTC) "
                        f"conflicts with existing '{e['description'][:50]}' "
                        f"({e['start_utc']} - {e['end_utc']})"
                    )
    return errors


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def build_rows(intent: dict, tz_offset: int, cache: dict) -> list[dict]:
    """Validate, resolve, and convert each intent entry into a submission row.

    Args:
        intent (dict): Parsed intent JSON.
        tz_offset (int): Hours offset from UTC.
        cache (dict): Workspace cache.

    Returns:
        list[dict]: Rows with all fields needed for preview and posting.

    Raises:
        IntentError: On malformed entries.
        ResolveError: On unresolvable hints.
    """
    entries = intent.get("entries", [])
    if not entries:
        raise IntentError("intent file has no 'entries'")

    default_billable = intent.get("default_billable")

    rows = []
    for i, entry in enumerate(entries):
        _validate_entry(entry, i)
        ids = resolve_entry(entry, cache)

        start_utc = _build_naive_utc(entry["date"], entry["start"], tz_offset)
        end_utc = _build_naive_utc(entry["date"], entry["end"], tz_offset)
        if end_utc <= start_utc:
            raise IntentError(f"entry {i}: end ({entry['end']}) must be after start ({entry['start']})")

        billable = entry.get("billable", default_billable)
        if billable is None:
            raise IntentError(
                f"entry {i}: 'billable' not set and no 'default_billable' in intent"
            )

        rows.append({
            "index": i,
            "date": entry["date"],
            "start_local": entry["start"],
            "end_local": entry["end"],
            "start_utc": start_utc,
            "end_utc": end_utc,
            "description": entry["description"],
            "billable": billable,
            **ids,
        })
    return rows


def render_preview(rows: list[dict]) -> str:
    """Format the batch as per-day markdown tables.

    Args:
        rows (list[dict]): Prepared rows from `build_rows`.

    Returns:
        str: Multi-line preview text.
    """
    by_date: dict[str, list[dict]] = {}
    for row in rows:
        by_date.setdefault(row["date"], []).append(row)

    out = []
    for date_str in sorted(by_date.keys()):
        out.append(f"\n### {date_str}")
        out.append("| # | Start | End  | Hrs | Client | Project | Task | Bill | Description |")
        out.append("|---|-------|------|-----|--------|---------|------|------|-------------|")
        for row in sorted(by_date[date_str], key=lambda r: r["start_local"]):
            hrs = (row["end_utc"] - row["start_utc"]).total_seconds() / 3600
            out.append(
                f"| {row['index']} "
                f"| {row['start_local']} "
                f"| {row['end_local']} "
                f"| {hrs:.2f} "
                f"| {row['client_name'][:25]} "
                f"| {row['project_name'][:25]} "
                f"| {row['task_name'][:40]} "
                f"| {'Y' if row['billable'] else 'N'} "
                f"| {row['description'][:50]} |"
            )
    total_hrs = sum((r["end_utc"] - r["start_utc"]).total_seconds() / 3600 for r in rows)
    out.append(f"\nTotal: {len(rows)} entries, {total_hrs:.2f} hours.")
    return "\n".join(out)


def post_rows(cl: Clockify, rows: list[dict]) -> tuple[int, list[str]]:
    """Post each row to Clockify.

    Args:
        cl (Clockify): Initialized SDK instance with workspace set.
        rows (list[dict]): Prepared rows.

    Returns:
        tuple[int, list[str]]: (success_count, failure_messages).
    """
    success = 0
    failures: list[str] = []
    for row in rows:
        try:
            entry = TimeEntryInput({
                "description": row["description"],
                "projectId": row["project_id"],
                "taskId": row["task_id"],
                "start": row["start_utc"],
                "end": row["end_utc"],
                "billable": row["billable"],
            })
            cl.add_time_entry(entry)
            success += 1
        except Exception as exc:
            failures.append(f"entry {row['index']} ({row['date']} {row['start_local']}): {exc}")
    return success, failures


def run_batch(intent_path: Path, dry_run: bool, tz_offset: int, allow_conflicts: bool) -> int:
    """Top-level orchestration for the batch submit workflow.

    Args:
        intent_path (Path): Path to the intent JSON.
        dry_run (bool): When True, skip the API post step.
        tz_offset (int): Hours offset from UTC for local times.
        allow_conflicts (bool): When True, post despite external overlaps.

    Returns:
        int: Process exit code.
    """
    intent = json.loads(intent_path.read_text())

    effective_tz = tz_offset
    if "timezone_offset_hours" in intent and tz_offset is None:
        effective_tz = intent["timezone_offset_hours"]
    if effective_tz is None:
        effective_tz = -5

    cache = load_workspace()

    try:
        rows = build_rows(intent, effective_tz, cache)
    except (IntentError, ResolveError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    in_batch = validate_batch_overlaps(rows)
    if in_batch:
        print("In-batch overlaps detected:", file=sys.stderr)
        for msg in in_batch:
            print(f"  - {msg}", file=sys.stderr)
        return 3

    print(render_preview(rows))

    external = validate_external_overlaps(rows, effective_tz)
    if external:
        print("\nConflicts with existing Clockify entries:", file=sys.stderr)
        for msg in external:
            print(f"  - {msg}", file=sys.stderr)
        if not allow_conflicts:
            print("re-run with --allow-conflicts to post anyway.", file=sys.stderr)
            return 4

    if dry_run:
        print(f"\ndry-run: would post {len(rows)} entries. pass --yes to submit.")
        return 0

    cl = Clockify(api_key=os.environ["CLOCKIFY_API"])
    cl.get_flywheel_workspace()
    success, failures = post_rows(cl, rows)
    print(f"\nposted {success}/{len(rows)}")
    if failures:
        print("failures:", file=sys.stderr)
        for msg in failures:
            print(f"  - {msg}", file=sys.stderr)
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", help="Path to the intent JSON file.")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually post entries. Without this flag the script runs as a dry-run.",
    )
    parser.add_argument(
        "--tz-offset",
        type=int,
        default=None,
        help="Hours offset from UTC. Overrides timezone_offset_hours in the intent file. "
             "Defaults to -5 if neither is set.",
    )
    parser.add_argument(
        "--allow-conflicts",
        action="store_true",
        help="Post entries even when they overlap existing Clockify entries.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    sys.exit(run_batch(Path(args.intent), not args.yes, args.tz_offset, args.allow_conflicts))
