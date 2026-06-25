#!/usr/bin/env python3
"""Pull a project's unique acquisition labels and emit a relabel-container CSV
skeleton with *suggested* ReproIn targets.

Read-only (it never renames anything — it generates an artifact you review and
then feed to the relabel-container gear). Mirrors relabel-container's own
approach: one Data View over `acquisition.label` (efficient, no per-acquisition
iteration / timeouts).

The output CSV has the columns relabel-container expects — `acquisition.label`
and `new acquisition.label` — plus a `confidence`/`note` column for your review.
`new acquisition.label` is PRE-FILLED only for high-confidence anatomicals
(T1/T2/FLAIR); localizers and specialty sequences are left blank. **Review every
row before running the gear.**

Two label sources (prefer the report when one exists — it's free and offline):
    # from an existing curate-bids report (no SDK, no auth):
    python3 pull_relabel_skeleton.py --report <niftis.csv> [--out acquisitions.csv]
    # from a live project (SDK Data View) when no prior run exists:
    uv run --with flywheel-sdk --with pandas python pull_relabel_skeleton.py \
        --project PRISMA-AKU --api-key-env BMGF_API [--out acquisitions.csv]
    # --project accepts a label or a 24-char id
"""

import argparse
import csv
import os
import re
import sys
import typing as t

PLANES = [("axial", "ax"), ("sagittal", "sag"), ("coronal", "cor"),
          ("axi", "ax"), ("sag", "sag"), ("cor", "cor")]


def _plane(s: str) -> str:
    """Extract an acquisition-plane tag from a label, or ''."""
    for needle, tag in PLANES:
        if needle in s:
            return tag
    return ""


def suggest_reproin(label: str) -> t.Tuple[str, str, str]:
    """Heuristic raw-label → (suggested ReproIn label, confidence, note).

    Pre-fills only confident anatomicals. Everything uncertain returns '' so the
    reviewer must decide. ReproIn label form: `<folder>-<suffix>[_acq-<x>]`.
    """
    s = label.lower()
    plane = _plane(s)

    def acq(*extra: str) -> str:
        joined = "".join(re.sub(r"[^a-z0-9]", "", x) for x in (plane, *extra) if x)
        return f"_acq-{joined}" if joined else ""

    if "localizer" in s or "scout" in s:
        return ("", "ignore", "localizer/scout — exclude from BIDS (leave blank)")
    if "flair" in s:
        return (f"anat-FLAIR{acq()}", "high", "")
    if "t2" in s and "map" in s:
        return (f"anat-T2map{acq()}", "low", "quantitative T2 map — verify suffix")
    if re.search(r"\bt1\b", s) or "t1w" in s or "mprage" in s:
        desc = "graywhite" if any(k in s for k in ("gray", "white", "contrast")) else \
               "standard" if "standard" in s else "mprage" if "mprage" in s else ""
        return (f"anat-T1w{acq(desc)}", "high", "")
    if re.search(r"\bt2\b", s) or "t2w" in s:
        desc = "fast" if "fast" in s else ""
        return (f"anat-T2w{acq(desc)}", "high", "")
    if "diff" in s or re.search(r"\bdwi\b", s) or re.search(r"\bdti\b", s):
        return ("dwi-dwi", "review", "diffusion — confirm dir-/run- as needed")
    if any(k in s for k in ("bold", "fmri", "rest", "task")):
        return ("func-bold_task-REPLACE", "review", "functional — set the task label")
    return ("", "review", "specialty/non-standard — verify a suffix or exclude")


def unique_labels_from_report(report_path: str) -> t.List[str]:
    """Read distinct acquisition labels from a curate-bids *_niftis.csv (offline)."""
    with open(report_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        col = next((c for c in (reader.fieldnames or []) if "acquisition" in c.lower() and "label" in c.lower()), "")
        if not col:
            col = next((c for c in (reader.fieldnames or []) if "label" in c.lower()), "")
        labels = {row.get(col, "").strip() for row in reader}
    return sorted(l for l in labels if l)


def get_project(fw: t.Any, ident: str):
    """Resolve a project by 24-char id or by label."""
    if re.fullmatch(r"[0-9a-fA-F]{24}", ident):
        return fw.get_project(ident)
    proj = fw.projects.find_first(f"label={ident}")
    if not proj:
        sys.exit(f"no project with label {ident!r}")
    return proj


def unique_acq_labels(fw: t.Any, project_id: str) -> t.List[str]:
    """Pull distinct acquisition.label values via a single Data View."""
    import flywheel
    builder = flywheel.ViewBuilder(
        label="bids-expert-relabel-skeleton",
        columns=["acquisition.label"],
        container="acquisition",
        match="all",
        process_files=False,
        include_ids=False,
        sort=False,
    )
    view = builder.build()
    view.parent = project_id
    df = fw.read_view_dataframe(view, project_id)
    if df.empty or "acquisition.label" not in df:
        return []
    return sorted(x for x in df["acquisition.label"].dropna().unique() if x)


def write_csv(labels: t.List[str], out_path: str) -> t.Dict[str, int]:
    """Write the relabel skeleton CSV; return a confidence tally."""
    tally: t.Dict[str, int] = {}
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["acquisition.label", "new acquisition.label", "confidence", "note"])
        for label in labels:
            new_label, conf, note = suggest_reproin(label)
            tally[conf] = tally.get(conf, 0) + 1
            writer.writerow([label, new_label, conf, note])
    return tally


def main() -> None:
    """CLI: get labels (from a report or live project), write the skeleton."""
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--report", help="a curate-bids *_niftis.csv to read labels from (offline)")
    src.add_argument("--project", help="project label or 24-char id (live SDK Data View)")
    parser.add_argument("--api-key-env", default="FW_API_KEY", help="env var holding the API key")
    parser.add_argument("--out", default="acquisitions.csv", help="output CSV path")
    args = parser.parse_args()

    if args.report:
        labels = unique_labels_from_report(args.report)
        print(f"report {args.report}: {len(labels)} distinct acquisition labels")
    else:
        key = os.environ.get(args.api_key_env)
        if not key:
            sys.exit(f"env var {args.api_key_env} not set")
        import flywheel
        fw = flywheel.Client(key)
        proj = get_project(fw, args.project)
        labels = unique_acq_labels(fw, proj.id)
        print(f"project {proj.label} ({proj.id}): {len(labels)} distinct acquisition labels")
    if not labels:
        sys.exit("no labels found")

    tally = write_csv(labels, args.out)
    print(f"wrote {args.out}")
    print("confidence:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print("REVIEW every row before running relabel-container — pre-filled labels are heuristic.")


if __name__ == "__main__":
    main()
