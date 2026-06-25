#!/usr/bin/env python3
"""Diagnose a curate-bids run from its `*_niftis.csv` report.

The duplicate-path *log* only prints bare paths and is nearly useless. The
`*_niftis.csv` report (curate-bids analysis → Results) is the real diagnostic.
This script summarizes it: how many images curated vs came back `unrecognized`,
which paths collide and why (`/` = JSON sidecars, `sourcedata/...` = DICOMs),
which rules fired, the distinct acquisition-label families, and a plain verdict.

Pure stdlib — no pandas, no SDK. Run on a downloaded report:

    python3 analyze_curation_report.py <path-to>_niftis.csv
"""

import argparse
import csv
import re
import sys
import typing as t
from collections import Counter

EMPTY_PATHS = {"", "/", "unrecognized"}


def find_col(fieldnames: t.List[str], *needles: str) -> str:
    """Return the first column whose name contains all needles (case-insensitive)."""
    for name in fieldnames:
        low = name.lower()
        if all(n in low for n in needles):
            return name
    return ""


def label_family(label: str) -> str:
    """Reduce an acquisition label to a coarse family (drop series no. + suffixes)."""
    core = re.sub(r"^\s*\d+\s*-\s*", "", label)
    core = re.sub(r"-?NOT FOR DIAGNOSTIC USE", "", core, flags=re.I).strip()
    return re.split(r"\s*[(\-]", core)[0].strip() or "(blank)"


def load_rows(path: str) -> t.Tuple[t.List[dict], t.List[str]]:
    """Load the CSV into dict rows + fieldnames."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def _counter_block(title: str, counter: Counter, top: int = 12) -> None:
    """Print a titled count block."""
    print(f"\n=== {title} ===")
    for key, n in counter.most_common(top):
        print(f"  {n:6d}  {key or '(blank)'}")


def analyze(path: str) -> None:
    """Run the full diagnosis on one niftis.csv."""
    rows, fields = load_rows(path)
    if not rows:
        print("Empty report — no rows.")
        return

    c_path = find_col(fields, "curated", "path") or find_col(fields, "path")
    c_rule = find_col(fields, "rule")
    c_type = find_col(fields, "file", "type") or find_col(fields, "type")
    c_uniq = find_col(fields, "unique")
    c_label = find_col(fields, "acquisition", "label") or find_col(fields, "label")
    print(f"report: {path}")
    print(f"rows: {len(rows)}   columns: {fields}")

    _counter_block("file type", Counter(r.get(c_type, "") for r in rows))
    _counter_block("rule ID", Counter(r.get(c_rule, "") for r in rows))

    paths = [r.get(c_path, "").strip() for r in rows]
    empty = sum(1 for p in paths if p in EMPTY_PATHS)
    real = len(paths) - empty
    print(f"\n=== curated path ===\n  real BIDS path: {real}   empty/'/'/unrecognized: {empty}")

    _counter_block("most common curated paths", Counter(paths), top=10)

    if c_uniq:
        uniq = Counter((r.get(c_uniq, "").split() or ["(blank)"])[0] for r in rows)
        _counter_block("Unique? flag", uniq)

    # NIfTI-specific verdict (the images are what matter for downstream apps)
    niftis = [r for r in rows if "nif" in r.get(c_type, "").lower()]
    nifti_unrec = sum(1 for r in niftis if r.get(c_path, "").strip() in EMPTY_PATHS)
    print(f"\n=== NIfTI images ===\n  total: {len(niftis)}   unrecognized/empty: {nifti_unrec}   curated: {len(niftis) - nifti_unrec}")

    if c_label:
        fams = Counter(label_family(r.get(c_label, "")) for r in rows)
        distinct = len({r.get(c_label, "") for r in rows})
        print(f"\n=== acquisition labels ===\n  distinct labels: {distinct}")
        _counter_block("label families (distinct count not shown; row count)", fams, top=12)

    _print_verdict(rows, paths, niftis, nifti_unrec, c_path, c_rule)


def _print_verdict(rows, paths, niftis, nifti_unrec, c_path, c_rule) -> None:
    """Interpret the numbers into an actionable verdict."""
    print("\n" + "=" * 60 + "\nVERDICT")
    dup_root = sum(1 for p in paths if p == "/")
    dup_sourcedata = sum(1 for p in paths if p.startswith("sourcedata/"))

    if niftis and nifti_unrec / max(len(niftis), 1) > 0.8:
        print("  - Most NIfTI images are UNRECOGNIZED — the acquisition labels are not")
        print("    matching the curation template (classic raw-SeriesDescription vs ReproIn).")
        print("    Fix: precurate (relabel-container) the labels, then re-curate.")
    if dup_root:
        print(f"  - {dup_root} files collapsed to '/' (root) — typically JSON sidecars matching a")
        print("    catch-all rule with no entities assigned. These are the blank '/' log lines.")
    if dup_sourcedata:
        print(f"  - {dup_sourcedata} files under 'sourcedata/...' — DICOMs (expected location), but")
        print("    identical series names across subjects/sessions collide -> duplicate paths.")
    real_bids = [p for p in paths if p not in EMPTY_PATHS and not p.startswith("sourcedata/")]
    if real_bids:
        dup_real = len(real_bids) - len(set(real_bids))
        if dup_real:
            print(f"  - {dup_real} collisions among REAL BIDS paths — same suffix within a session")
            print("    without a distinguishing entity. Add acq-/run- to disambiguate.")
    if not real_bids:
        print("  - Zero images reached a real BIDS path. Curation produced no usable dataset;")
        print("    any downstream BIDS-app gear (bids-mriqc etc.) will see an empty /work/bids.")


def main() -> None:
    """CLI entry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="path to a curate-bids *_niftis.csv")
    args = parser.parse_args()
    try:
        analyze(args.report)
    except FileNotFoundError:
        sys.exit(f"not found: {args.report}")


if __name__ == "__main__":
    main()
