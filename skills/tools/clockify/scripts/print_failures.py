#!/usr/bin/env python3
"""Map batch_submit.py failure output back to the intent entries that failed.

Usage:
    python3 print_failures.py INTENT_JSON [FAILURE_LOG]

FAILURE_LOG is the captured output of a batch_submit.py run (stdout or
stderr, full log is fine). When omitted, the log is read from stdin, so
you can pipe a run directly:

    python3 batch_submit.py intent.json --yes 2>&1 | python3 print_failures.py intent.json
"""
import json
import re
import sys
import typing as t
from pathlib import Path

FAILURE_RE = re.compile(r"-\s+entry\s+(\d+)\s+\((\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})\):\s*(.*)")
RESPONSE_PREFIX = "Response:"


def get_failures(log_text: str) -> t.List[dict]:
    """Extract failure records from batch_submit output.

    Args:
        log_text (str): Full text of a batch_submit.py run.

    Returns:
        List[dict]: One dict per failure with index, date, start, error,
            and the server response line (when present).
    """
    failures = []
    pending = None
    for line in log_text.splitlines():
        match = FAILURE_RE.search(line)
        if match:
            pending = {
                "index": int(match.group(1)),
                "date": match.group(2),
                "start": match.group(3),
                "error": match.group(4).strip(),
                "response": "",
            }
            failures.append(pending)
            continue
        if pending and line.strip().startswith(RESPONSE_PREFIX):
            pending["response"] = line.strip()[len(RESPONSE_PREFIX):].strip()
            pending = None
    return failures


def build_failure_report(intent: dict, failures: t.List[dict]) -> str:
    """Build a human-readable report joining failures to intent entries.

    Args:
        intent (dict): Parsed intent JSON (with an "entries" list).
        failures (List[dict]): Failure records from get_failures().

    Returns:
        str: Multi-line report, one block per failed entry.
    """
    entries = intent["entries"]
    blocks = []
    for failure in failures:
        idx = failure["index"]
        if idx >= len(entries):
            blocks.append(f"entry {idx}: not found in intent file (only {len(entries)} entries)")
            continue
        entry = entries[idx]
        path = " > ".join(
            entry.get(key, "?") for key in ("client", "project", "task") if key in entry
        )
        blocks.append(
            f"entry {idx}: {entry['date']} {entry['start']}-{entry['end']}\n"
            f"  where: {path}\n"
            f"  desc:  {entry['description']}\n"
            f"  error: {failure['error']}\n"
            f"  server: {failure['response'] or '(no response line)'}"
        )
    return "\n\n".join(blocks)


def main() -> int:
    """Entry point: load inputs, print the failure report."""
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    intent = json.loads(Path(sys.argv[1]).read_text())
    log_text = Path(sys.argv[2]).read_text() if len(sys.argv) > 2 else sys.stdin.read()

    failures = get_failures(log_text)
    if not failures:
        print("no failures found in log")
        return 0
    print(f"{len(failures)} failed entries:\n")
    print(build_failure_report(intent, failures))
    return 1


if __name__ == "__main__":
    sys.exit(main())
