#!/usr/bin/env python3
"""Offline dry-run for a curation template — predict what it will do BEFORE a gear run.

Applies a curation template's rules to a curate-bids `*_niftis.csv` (which carries the
real Subject / Session / acquisition.label / file.type per file) and reports: how many
files match each rule, the suffix/acq distribution, what stays `unrecognized`, and —
crucially — **whether the resulting BIDS paths are unique** (i.e. would the duplicate-path
failure be fixed).

This is a PRE-FLIGHT PREDICTOR, not the gear. Known limitations (it will say so at runtime):
  - Only evaluates `where`/`initialize` conditions on fields present in the CSV
    (`container_type`, `parent_container_type`, `file.type`, `acquisition.label`, `file.name`).
    Conditions on `file.classification.*` or other unavailable fields make a rule
    indeterminate → it's treated as NON-matching and reported (this is why base ReproIn
    rules that key on classification show up as skipped — correct for raw-label data).
  - `auto_update` path/filename construction is simplified to a canonical
    `sub-X[/ses-Y]/<folder>/sub-X[_ses-Y][_acq-..][_run-..]_<suffix>` form — enough to
    detect collisions, not byte-identical to the gear.
  - Supports `$value`, `$regex` (named `value` group), `$switch` ($eq/$regex/$default),
    `$take`, `$run_counter`. Resolvers and exotic ops are ignored.

Usage:
    python3 simulate_template.py <template.json> <niftis.csv>
    # resolves `extends` against ../references/flywheel/templates/<base>.json
"""

import argparse
import csv
import json
import re
import sys
import typing as t
from collections import Counter, defaultdict
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "references" / "flywheel" / "templates"

# field name in a definition's properties -> BIDS entity key, in canonical filename order
ENTITY_ORDER = [("Acq", "acq"), ("Ce", "ce"), ("Rec", "rec"), ("Dir", "dir"),
                ("Mod", "mod"), ("Run", "run"), ("Echo", "echo"), ("Inv", "inv"),
                ("Part", "part")]


def load_template(path: Path) -> t.Tuple[t.List[dict], t.Dict[str, dict]]:
    """Load a template, resolving `extends` — return (rules in match order, definitions)."""
    data = json.loads(path.read_text())
    rules: t.List[dict] = []
    defs: t.Dict[str, dict] = {}
    base = data.get("extends")
    if base:
        base_path = TEMPLATES_DIR / f"{base}.json"
        if base_path.exists():
            base_rules, base_defs = load_template(base_path)
            rules.extend(base_rules)          # parent rules first (first match wins)
            defs.update(base_defs)
        else:
            print(f"  (warn: base template '{base}' not found at {base_path}; inherited rules not simulated)")
    rules.extend(data.get("rules", []) or [])
    defs.update(data.get("definitions", {}) or {})
    return rules, defs


def get_field(ctx: dict, path: str) -> t.Optional[str]:
    """Return a context field by dot-path, or None if unavailable."""
    return ctx.get(path)


def cond_matches(spec: t.Any, actual: t.Optional[str]) -> t.Optional[bool]:
    """Evaluate one where-condition. None = indeterminate (field unavailable)."""
    if isinstance(spec, dict):
        if "$in" in spec:
            return None if actual is None else actual in spec["$in"]
        if "$regex" in spec:
            pats = spec["$regex"]
            pats = pats if isinstance(pats, list) else [pats]
            return None if actual is None else any(re.search(p, actual) for p in pats)
        if "$not" in spec:
            inner = cond_matches(spec["$not"], actual)
            return None if inner is None else not inner
    return None if actual is None else actual == spec


def where_matches(where: dict, ctx: dict) -> t.Optional[bool]:
    """All conditions must hold. None if any is indeterminate."""
    indeterminate = False
    for field, spec in where.items():
        if field in ("$and", "$or"):
            continue  # nested logic not simulated; ignore
        result = cond_matches(spec, get_field(ctx, field))
        if result is None:
            indeterminate = True
        elif result is False:
            return False
    return None if indeterminate else True


def eval_switch(switch: dict, ctx: dict, fields: dict) -> t.Optional[str]:
    """Evaluate a $switch over a context field; return the matched $value."""
    on_val = get_field(ctx, switch.get("$on", "")) or ""
    for case in switch.get("$cases", []):
        if "$default" in case:
            return case.get("$value")
        if "$eq" in case and on_val in case["$eq"]:
            return case.get("$value")
        if "$regex" in case and re.search(case["$regex"], on_val):
            return case.get("$value")
    return None


def eval_init_field(spec: dict, ctx: dict, fields: dict) -> t.Optional[str]:
    """Evaluate one initialize entry (excluding run_counter, handled later)."""
    if "$value" in spec:
        return spec["$value"]
    if "$switch" in spec:
        return eval_switch(spec["$switch"], ctx, fields)
    # form {"<field.path>": {"$regex": ...} | {"$take": true}}
    for key, op in spec.items():
        if key.startswith("$"):
            continue
        src = get_field(ctx, key)
        if src is None:
            return None
        if isinstance(op, dict) and "$regex" in op:
            m = re.search(op["$regex"], src)
            if m:
                return m.groupdict().get("value") or (m.group(1) if m.groups() else m.group(0))
        if isinstance(op, dict) and op.get("$take"):
            return src
    return None


def interp(key: str, fields: dict) -> str:
    """Interpolate {file.info.BIDS.<Field>} tokens in a run_counter key."""
    return re.sub(r"\{file\.info\.BIDS\.(\w+)\}", lambda m: str(fields.get(m.group(1), "")), key)


def folder_for(rule: dict, defs: dict) -> str:
    """Determine the datatype folder for a rule's definition."""
    tmpl = rule.get("template", "")
    props = (defs.get(tmpl, {}).get("properties", {}) or {})
    folder = (props.get("Folder", {}) or {}).get("default")
    if folder:
        return folder
    return tmpl[:-5] if tmpl.endswith("_file") else tmpl


def build_path(sub: str, ses: str, folder: str, fields: dict, suffix: str) -> str:
    """Canonical sub/ses/folder/filename (simplified) for collision detection."""
    name = f"sub-{sub}" + (f"_ses-{ses}" if ses else "")
    for field, ent in ENTITY_ORDER:
        if fields.get(field):
            name += f"_{ent}-{fields[field]}"
    name += f"_{suffix}"
    path = f"sub-{sub}" + (f"/ses-{ses}" if ses else "") + f"/{folder}/{name}"
    return path


def find_col(fieldnames: t.List[str], *needles: str) -> str:
    """First column whose name contains all needles (case-insensitive)."""
    for name in fieldnames:
        if all(n in name.lower() for n in needles):
            return name
    return ""


def simulate(template_path: Path, report_path: Path) -> None:
    """Run the dry-run and print the prediction."""
    rules, defs = load_template(template_path)
    print(f"template: {template_path.name}  ({len(rules)} rules incl. inherited)")

    with open(report_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        cols = reader.fieldnames or []
    c_sub, c_ses = find_col(cols, "subject"), find_col(cols, "session")
    c_label = find_col(cols, "acquisition", "label") or find_col(cols, "label")
    c_type = find_col(cols, "file", "type") or find_col(cols, "type")
    c_name = find_col(cols, "file", "name") or find_col(cols, "name")

    niftis = [r for r in rows if "nif" in (r.get(c_type, "")).lower()]
    print(f"NIfTI files in report: {len(niftis)}")

    counters: t.Dict[t.Tuple, int] = defaultdict(int)
    rule_hits: Counter = Counter()
    suffix_dist: Counter = Counter()
    skipped_rules: set = set()
    paths: t.List[str] = []
    unrecognized = 0

    for r in niftis:
        ctx = {
            "container_type": "file",
            "parent_container_type": "acquisition",
            "file.type": r.get(c_type, ""),
            "acquisition.label": r.get(c_label, ""),
            "file.name": r.get(c_name, ""),
        }
        matched = _apply_rules(rules, ctx, defs, counters, r.get(c_sub, ""), r.get(c_ses, ""),
                               rule_hits, skipped_rules)
        if matched is None:
            unrecognized += 1
        else:
            suffix_dist[matched[1]] += 1
            paths.append(matched[0])

    _report(rules, niftis, unrecognized, suffix_dist, paths, rule_hits, skipped_rules)


def _apply_rules(rules, ctx, defs, counters, sub, ses, rule_hits, skipped_rules):
    """Try rules in order; return (path, suffix) for the first match, else None."""
    for rule in rules:
        verdict = where_matches(rule.get("where", {}), ctx)
        if verdict is None:
            skipped_rules.add(rule.get("id", rule.get("template", "?")))
            continue
        if verdict is False:
            continue
        fields, suffix = _run_initialize(rule, ctx, defs, counters, sub, ses)
        rule_hits[rule.get("id", rule.get("template", "?"))] += 1
        folder = folder_for(rule, defs)
        return build_path(sub, ses, folder, fields, suffix or "MISSING"), (suffix or "MISSING")
    return None


def _run_initialize(rule, ctx, defs, counters, sub, ses):
    """Compute the BIDS fields for a matched rule (incl. run_counter)."""
    fields: dict = {}
    init = rule.get("initialize", {}) or {}
    for target, spec in init.items():
        if isinstance(spec, dict) and "$run_counter" not in spec:
            val = eval_init_field(spec, ctx, fields)
            if val:
                fields[target] = val
    # run_counter pass (needs other fields for key interpolation)
    for target, spec in init.items():
        if isinstance(spec, dict) and "$run_counter" in spec and not fields.get(target):
            key = interp(spec["$run_counter"].get("key", target), fields)
            ckey = (sub, ses, key)
            counters[ckey] += 1
            fields[target] = str(counters[ckey])
    return fields, fields.get("Suffix")


def _report(rules, niftis, unrecognized, suffix_dist, paths, rule_hits, skipped_rules) -> None:
    """Print the prediction + verdict."""
    print(f"\nmatched (curated): {len(paths)}   unrecognized (excluded): {unrecognized}")
    print("suffix distribution:", dict(suffix_dist))
    print("\nrule hits:")
    for rid, n in rule_hits.most_common():
        print(f"  {n:6d}  {rid}")
    if skipped_rules:
        print(f"\nrules skipped (need fields not in the report, e.g. classification): {sorted(skipped_rules)}")
    dupes = len(paths) - len(set(paths))
    print("\n" + "=" * 60 + "\nPREDICTION")
    print(f"  predicted duplicate BIDS paths: {dupes}")
    if dupes == 0 and paths:
        print("  -> no collisions; this template should pass the duplicate-path check.")
    elif dupes:
        worst = Counter(paths).most_common(5)
        print("  -> collisions remain; add acq-/run- disambiguation. Worst:")
        for p, n in worst:
            if n > 1:
                print(f"       {n}x  {p}")
    if "MISSING" in suffix_dist:
        print(f"  WARNING: {suffix_dist['MISSING']} files matched a rule but got no Suffix — check initialize.")
    print("\n(Pre-flight predictor — confirm with a real dry-run on one subject.)")


def main() -> None:
    """CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path, help="curation template JSON")
    parser.add_argument("report", type=Path, help="a curate-bids *_niftis.csv")
    args = parser.parse_args()
    if not args.template.exists():
        sys.exit(f"not found: {args.template}")
    if not args.report.exists():
        sys.exit(f"not found: {args.report}")
    simulate(args.template, args.report)


if __name__ == "__main__":
    main()
