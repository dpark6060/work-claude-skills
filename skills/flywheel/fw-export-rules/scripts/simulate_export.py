"""Simulate a Flywheel export rule set against a hierarchy fixture, offline.

Mirrors the connector's scan loop (connector/exports/operation.py `items`/`get_rule`):
zero-byte skip, rule match gated on the file's parent container type, analysis
routing, duplicate-label `_N` suffixes, and destination-collision `_N` suffixes.
Rule matching and path formatting are fw-meta's own `ExportRule.match`/`format`.

Usage:
    uv run --with fw-meta==4.13.0 --with pyyaml python simulate_export.py RULES FIXTURE

RULES is a bare rule list or a full export spec. FIXTURE is YAML:

    project: {label: P, info: {}}
    files: [...]                          # project attachments
    analyses: [...]                       # project analyses
    subjects:
      - label: S01
        info: {cohort: A}
        files: [...]
        analyses: [...]
        sessions:
          - label: baseline
            timestamp: "2024-03-05T10:00:00+00:00"
            files: [...]
            acquisitions:
              - label: 1 - T1w
                files:
                  - {name: T1.dicom.zip, type: dicom, size: 1000, info: {}, tags: []}

An analysis entry is `{label: ..., files: [{name: ..., file_group: inputs|outputs}]}`.
File `size` defaults to 1 (zero-byte files are skipped, as on the server).
"""

import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from fw_meta.exports import ExportRule
from fw_meta.utils import sanitize_label

LEVELS = ["project", "subject", "session", "acquisition"]
CHILDREN = {"project": "subjects", "subject": "sessions", "session": "acquisitions"}


def load_rules(path: Path) -> list[ExportRule]:
    """Load and validate rules from a bare list or a full export spec."""
    spec = yaml.safe_load(path.read_text())
    rules = spec["rules"] if isinstance(spec, dict) else spec
    return [ExportRule.model_validate(rule) for rule in rules]


def suffix_label(label: str, seen: Counter) -> str:
    """Return label with the connector's `_N` suffix when a sibling already used it."""
    seen[label] += 1
    return label if seen[label] == 1 else f"{label}_{seen[label] - 1}"


def walk(node: dict, level: str, parents: dict, src_dir: list[str]):
    """Yield (item, parent_level, src_path) for every file under node."""
    file_names: Counter = Counter()
    for file in node.get("files", []):
        file = {"size": 1, **file}
        name = file["name"]
        src_name = name if not file_names[name] else f"{name}_{file_names[name]}"
        file_names[name] += 1
        yield {**parents, "file": file}, level, "/".join([*src_dir, src_name])

    analysis_labels: Counter = Counter()
    for analysis in node.get("analyses", []):
        analysis = {**analysis, "label": suffix_label(analysis["label"], analysis_labels)}
        for file in analysis.get("files", []):
            file = {"size": 1, **file}
            item = {**parents, "analysis": analysis, "file": file}
            yield item, level, "/".join([*src_dir, analysis["label"], file["name"]])

    if child_key := CHILDREN.get(level):
        child_level = LEVELS[LEVELS.index(level) + 1]
        labels: Counter = Counter()
        for child in node.get(child_key, []):
            child = {**child, "label": suffix_label(child["label"], labels)}
            scalars = {k: v for k, v in child.items() if k not in ("files", "analyses", CHILDREN.get(child_level))}
            yield from walk(child, child_level, {**parents, child_level: scalars}, [*src_dir, child["label"]])


def get_rule(item: dict, parent_level: str, rules: list[ExportRule]) -> int | None:
    """Return the index of the first matching rule, mirroring connector get_rule."""
    for index, rule in enumerate(rules):
        if "analysis" in item:
            if rule.analyses and parent_level == rule.level and rule.match(item):
                return index
        elif parent_level == rule.level and rule.match(item):
            return index
    return None


def main(rules_path: str, fixture_path: str) -> None:
    """Print one line per file and a per-rule coverage summary."""
    rules = load_rules(Path(rules_path))
    fixture = yaml.safe_load(Path(fixture_path).read_text())
    project = fixture.get("project", {})

    dst_counts: Counter = Counter()
    per_rule: dict = defaultdict(int)
    skipped, collisions = [], []
    for item, parent_level, src_path in walk(fixture, "project", {"project": project}, [project.get("label", "")]):
        if not item["file"].get("size"):
            skipped.append((src_path, "zero-byte file"))
            continue
        index = get_rule(item, parent_level, rules)
        if index is None:
            skipped.append((src_path, "no matching rule found"))
            continue
        dst_path = rules[index].format(item)
        if analysis := item.get("analysis"):
            base, _, name = dst_path.rpartition("/")
            group = "INPUTS" if item["file"].get("file_group") == "inputs" else "OUTPUTS"
            dst_path = "/".join(filter(None, [base, "ANALYSES", sanitize_label(analysis["label"]), group, name]))
        dst_counts[dst_path] += 1
        if (count := dst_counts[dst_path]) > 1:
            original = dst_path
            stem, dot, ext = Path(dst_path).name.partition(".")
            dst_path = str(Path(dst_path).with_name(f"{stem}_{count - 1}{dot}{ext}"))
            collisions.append((src_path, original, dst_path))
        per_rule[index] += 1
        extras = []
        if rules[index].unzip and src_path.lower().endswith(".zip"):
            extras.append(f"UNZIP -> {dst_path}/<members, unzip_path={rules[index].unzip_path.value}>")
        if rules[index].metadata:
            extras.append(f"+ {dst_path}.metadata.json")
        print(f"{src_path}  ->  rule {index} (level={rules[index].level.value})  {dst_path}  {' '.join(extras)}")

    for src_path, reason in skipped:
        print(f"{src_path}  ->  SKIPPED ({reason})")
    print("\n--- coverage ---")
    for index, rule in enumerate(rules):
        print(f"rule {index} (level={rule.level.value}): {per_rule[index]} files")
    print(f"skipped: {len(skipped)}")
    for src_path, original, renamed in collisions:
        print(f"COLLISION: {src_path} wanted {original}, renamed to {renamed}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
