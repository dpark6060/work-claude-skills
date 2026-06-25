#!/usr/bin/env python3
"""Generate denormalized per-datatype BIDS reference markdown from the BIDS schema.

The BIDS spec ships a normalized machine-readable schema: entities, datatypes,
suffixes, and metadata are each defined once, and a `rules/` layer (with `$ref`
indirection, list-refs, and intra-rule inheritance) stitches them together. We
load and dereference it with the official `bidsschematools` package rather than
reimplementing its resolver, then render one self-contained markdown file per
datatype — so an LLM can load exactly the rules for (say) an anat scan without
reading the whole spec.

Metadata applicability in BIDS is a contextual rules engine (selectors reference
other metadata values and dataset contents), so it cannot be fully flattened.
We split it deterministically:
  - datatype files get metadata scoped to the datatype or its own suffixes
  - modality-wide metadata (shared across e.g. all MRI datatypes) goes into one
    `_common-metadata.md` per modality, referenced from each datatype file

Markdown is the shipped artifact. Rerun this whenever the vendored schema bumps.
Output is stamped with the schema version (not wall-clock time) so regenerating
produces clean diffs.

Usage:
    uv run --with bidsschematools python build_bids_reference.py \
        [--schema vendor/bids-schema] [--out references/bids] [--datatype anat]
"""

import argparse
import re
import typing as t
from collections.abc import Mapping
from pathlib import Path

from bidsschematools import schema as bst

# Datatype -> modality. BIDS does not store this mapping in the schema objects;
# it is editorial (how the spec groups datatypes into modality pages). Stable.
DATATYPE_MODALITY: t.Dict[str, str] = {
    "anat": "mri",
    "func": "mri",
    "dwi": "mri",
    "fmap": "mri",
    "perf": "mri",
    "mrs": "mrs",
    "eeg": "eeg",
    "meg": "meg",
    "ieeg": "ieeg",
    "emg": "emg",
    "pet": "pet",
    "beh": "beh",
    "micr": "micr",
    "motion": "motion",
    "nirs": "nirs",
}


def _plain(obj: t.Any) -> t.Any:
    """Recursively convert a bidsschematools Namespace into plain dicts/lists."""
    if isinstance(obj, Mapping):
        return {key: _plain(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_plain(value) for value in obj]
    return obj


class SidecarGroup(t.NamedTuple):
    """One sidecar metadata rule group with its scope and fields."""

    name: str
    selectors: t.List[str]
    fields: t.List[t.Tuple[str, str]]
    datatypes: t.Set[str]
    suffixes: t.Set[str]
    modalities: t.Set[str]


class BidsSchema:
    """Loads the dereferenced BIDS schema and exposes the joins references need."""

    def __init__(self, schema_root: Path):
        """Load and dereference the schema via bidsschematools."""
        self.s = bst.load_schema(str(schema_root))
        self.entity_order: t.List[str] = list(self.s.rules.entities)
        self.entities_defs = _plain(self.s.objects.entities)
        self.datatype_defs = _plain(self.s.objects.datatypes)
        self.raw_rules = _plain(self.s.rules.files.raw)
        self.version = f"BIDS {self.s.bids_version} / schema {self.s.schema_version}"
        self._suffix_lookup = self._build_suffix_lookup()
        self._sidecar_groups = self._load_sidecar_groups()

    def _build_suffix_lookup(self) -> t.Dict[str, dict]:
        """Map suffix string (by schema key and by value) to its definition."""
        lookup: t.Dict[str, dict] = {}
        for key, defn in _plain(self.s.objects.suffixes).items():
            if not isinstance(defn, dict):
                continue
            lookup[key] = defn
            if defn.get("value"):
                lookup[defn["value"]] = defn
        return lookup

    def get_suffix_meaning(self, suffix: str) -> str:
        """Return a one-line meaning for a suffix, or empty string."""
        return self._suffix_lookup.get(suffix, {}).get("display_name", "").strip()

    def order_entities(self, entities: dict) -> t.List[t.Tuple[str, str]]:
        """Order a (already-dereferenced) entities dict per rules/entities.yaml."""
        ordered = [
            (name, self._coerce_level(entities[name]))
            for name in self.entity_order
            if name in entities
        ]
        ordered += [
            (name, self._coerce_level(level))
            for name, level in entities.items()
            if name not in self.entity_order
        ]
        return ordered

    @staticmethod
    def _coerce_level(value: t.Any) -> str:
        """Normalize a requirement value (string or dict) to a level string."""
        if isinstance(value, dict):
            return value.get("level") or value.get("requirement") or "optional"
        return str(value)

    def entity_key(self, long_name: str) -> str:
        """Return the short filename key for an entity (e.g. acquisition -> acq)."""
        return self.entities_defs.get(long_name, {}).get("name", long_name)

    def entity_display(self, long_name: str) -> str:
        """Return the human display name for an entity."""
        return self.entities_defs.get(long_name, {}).get("display_name", long_name)

    def _load_sidecar_groups(self) -> t.List[SidecarGroup]:
        """Flatten every dereferenced rules/sidecars group with its scope."""
        groups: t.List[SidecarGroup] = []
        for file_groups in _plain(self.s.rules.sidecars).values():
            if not isinstance(file_groups, dict):
                continue
            for name, group in file_groups.items():
                if not isinstance(group, dict) or "fields" not in group:
                    continue
                selectors = group.get("selectors", []) or []
                fields = _parse_fields(group["fields"])
                if not fields:
                    continue
                groups.append(
                    SidecarGroup(
                        name=name,
                        selectors=selectors,
                        fields=fields,
                        datatypes=_own_tokens(selectors, "datatype"),
                        suffixes=_own_tokens(selectors, "suffix"),
                        modalities=_own_tokens(selectors, "modality"),
                    )
                )
        return groups

    def datatype_metadata(self, datatype: str, suffix_set: t.Set[str]) -> t.List[SidecarGroup]:
        """Sidecar groups scoped to this datatype or one of its own suffixes."""
        return [
            g
            for g in self._sidecar_groups
            if datatype in g.datatypes or (g.suffixes & suffix_set)
        ]

    def modality_metadata(self, modality: str) -> t.List[SidecarGroup]:
        """Sidecar groups scoped to a whole modality, not narrowed to datatype/suffix."""
        return [
            g
            for g in self._sidecar_groups
            if modality in g.modalities and not g.datatypes and not g.suffixes
        ]


def _parse_fields(fields: dict) -> t.List[t.Tuple[str, str]]:
    """Normalize a sidecar group's fields into (name, level) pairs.

    Collapses whitespace in the level string so multi-line `level_addendum`
    text from the schema doesn't break the markdown table.
    """
    parsed: t.List[t.Tuple[str, str]] = []
    for name, spec in fields.items():
        if isinstance(spec, dict):
            level = spec.get("level", "optional")
            if spec.get("level_addendum"):
                level = f"{level} ({spec['level_addendum']})"
        else:
            level = str(spec)
        parsed.append((name, " ".join(level.split())))
    return parsed


def _own_tokens(selectors: t.List[str], keyword: str) -> t.Set[str]:
    """Quoted values constrained against the file's OWN keyword in a selector.

    Matches `datatype`/`suffix`/`modality` as a bare token (so it ignores
    `dataset.datatypes`, `dataset.modalities`, `sidecar.*`, `entities.*`), then
    collects the quoted string literals in that selector. Selectors are single
    conditions, so the quoted tokens belong to that keyword's comparison.
    """
    pattern = re.compile(rf"(?<![.\w]){keyword}\b")
    quoted = re.compile(r"""["']([^"']+)["']""")
    found: t.Set[str] = set()
    for sel in selectors:
        if pattern.search(sel):
            found.update(quoted.findall(sel))
    return found


def render_datatype(schema: BidsSchema, datatype: str, raw_rules: dict) -> str:
    """Render one datatype's reference markdown."""
    modality = DATATYPE_MODALITY.get(datatype, datatype)
    dt_def = schema.datatype_defs.get(datatype, {})
    display = dt_def.get("display_name", datatype)
    description = (dt_def.get("description", "") or "").strip()
    suffix_set = _suffix_set(raw_rules)

    lines: t.List[str] = []
    lines += _render_frontmatter(schema, datatype, modality, display)
    lines.append(f"# `{datatype}` — {display}")
    lines.append("")
    if description:
        lines.append(description)
        lines.append("")
    lines.append(f"> Modality: **{modality}** · Source: {schema.version}")
    lines.append("")
    lines += _render_suffix_groups(schema, raw_rules)
    lines += _render_metadata(
        "Datatype-specific sidecar metadata (JSON)",
        schema.datatype_metadata(datatype, suffix_set),
    )
    lines.append("")
    lines.append(
        f"For metadata shared across all `{modality}` datatypes "
        f"(scanner hardware, sequence, timing), see [`_common-metadata.md`](./_common-metadata.md)."
    )
    return "\n".join(lines).rstrip() + "\n"


def render_modality_common(schema: BidsSchema, modality: str) -> str:
    """Render the shared modality-wide metadata page."""
    lines = [
        "---",
        "type: bids-modality-metadata",
        f"modality: {modality}",
        f"tags: [bids, {modality}, metadata]",
        f"source: {schema.version}",
        "generator: scripts/build_bids_reference.py",
        "---",
        "",
        f"# `{modality}` — shared sidecar metadata",
        "",
        f"Metadata fields that apply across all `{modality}` datatypes. Datatype "
        "pages link here instead of duplicating these tables. Selector conditions "
        "are shown verbatim — they are not evaluated.",
        "",
    ]
    lines += _render_metadata("Fields", schema.modality_metadata(modality), with_heading=False)
    return "\n".join(lines).rstrip() + "\n"


def render_entities_glossary(schema: BidsSchema) -> str:
    """Render the global entity glossary in canonical filename order."""
    lines = [
        "---",
        "type: bids-entity-glossary",
        "tags: [bids, entities, glossary]",
        f"source: {schema.version}",
        "generator: scripts/build_bids_reference.py",
        "---",
        "",
        "# BIDS entities (canonical order)",
        "",
        "Every BIDS entity, in the order it must appear in a filename. Per-datatype pages "
        "say which of these are required/optional/forbidden for that datatype.",
        "",
        "| # | Entity | Key | Format | Meaning |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, long_name in enumerate(schema.entity_order, start=1):
        defn = schema.entities_defs.get(long_name, {})
        key = defn.get("name", long_name)
        fmt = defn.get("format", "")
        desc = " ".join((defn.get("description", "") or "").split())
        desc = desc.split(". ")[0].rstrip(".") if desc else ""
        lines.append(f"| {i} | {defn.get('display_name', long_name)} | `{key}-` | {fmt} | {desc}. |")
    return "\n".join(lines).rstrip() + "\n"


def _suffix_set(raw_rules: dict) -> t.Set[str]:
    """Collect every suffix across a datatype's raw rule groups."""
    suffixes: t.Set[str] = set()
    for group in raw_rules.values():
        if isinstance(group, dict):
            suffixes.update(group.get("suffixes", []) or [])
    return suffixes


def _render_frontmatter(schema: BidsSchema, datatype: str, modality: str, display: str) -> t.List[str]:
    """Build the YAML frontmatter block for a datatype page."""
    tags = sorted({"bids", datatype, modality})
    return [
        "---",
        "type: bids-datatype-reference",
        f"datatype: {datatype}",
        f"modality: {modality}",
        f"display_name: {display}",
        f"tags: [{', '.join(tags)}]",
        f"source: {schema.version}",
        "generator: scripts/build_bids_reference.py",
        "---",
        "",
    ]


def _render_suffix_groups(schema: BidsSchema, raw_rules: dict) -> t.List[str]:
    """Render every suffix group for a datatype (suffixes, extensions, entities)."""
    lines = ["## Suffix groups", ""]
    for group_name, group in raw_rules.items():
        if not isinstance(group, dict) or "suffixes" not in group:
            continue
        lines.append(f"### {group_name}")
        lines.append("")
        lines += _render_suffix_table(schema, group.get("suffixes", []))
        extensions = group.get("extensions", [])
        if extensions:
            lines.append(f"**Extensions:** {', '.join(f'`{e}`' for e in extensions)}")
            lines.append("")
        lines += _render_entity_table(schema, group.get("entities", {}))
    return lines


def _render_suffix_table(schema: BidsSchema, suffixes: t.List[str]) -> t.List[str]:
    """Render the suffix → meaning table for a group."""
    lines = ["| Suffix | Meaning |", "| --- | --- |"]
    for suffix in suffixes:
        lines.append(f"| `{suffix}` | {schema.get_suffix_meaning(suffix)} |")
    lines.append("")
    return lines


def _render_entity_table(schema: BidsSchema, entities: dict) -> t.List[str]:
    """Render the ordered entity → key → requirement table for a group."""
    if not entities:
        return []
    lines = [
        "**Entities** (in filename order):",
        "",
        "| Entity | Key | Requirement |",
        "| --- | --- | --- |",
    ]
    for long_name, level in schema.order_entities(entities):
        lines.append(f"| {schema.entity_display(long_name)} | `{schema.entity_key(long_name)}-` | {level} |")
    lines.append("")
    return lines


def _render_metadata(heading: str, groups: t.List[SidecarGroup], with_heading: bool = True) -> t.List[str]:
    """Render a list of sidecar metadata groups."""
    if not groups:
        return [f"## {heading}", "", "_None defined for this datatype._"] if with_heading else []
    lines = [f"## {heading}", ""] if with_heading else []
    for group in groups:
        lines.append(f"### {group.name}")
        if group.selectors:
            lines.append("")
            lines.append("Applies when:")
            for sel in group.selectors:
                lines.append(f"- `{' '.join(sel.split())}`")
        lines.append("")
        lines.append("| Field | Level |")
        lines.append("| --- | --- |")
        for field, level in group.fields:
            lines.append(f"| `{field}` | {level} |")
        lines.append("")
    return lines


def get_datatypes(schema: BidsSchema) -> t.List[str]:
    """Return datatype names present in the schema that have a modality mapping."""
    return [dt for dt in schema.raw_rules if dt in DATATYPE_MODALITY]


def main() -> None:
    """Parse args and generate datatype + modality-common reference markdown."""
    skill_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema", type=Path, default=skill_root / "vendor" / "bids-schema",
        help="BIDS schema dir (default: vendored snapshot under vendor/bids-schema)",
    )
    parser.add_argument(
        "--out", type=Path, default=skill_root / "references" / "bids",
        help="output dir for markdown (default: references/bids)",
    )
    parser.add_argument("--datatype", help="generate only this datatype (preview)")
    args = parser.parse_args()

    schema = BidsSchema(args.schema)
    datatypes = [args.datatype] if args.datatype else get_datatypes(schema)
    modalities_seen: t.Set[str] = set()
    for datatype in datatypes:
        raw_rules = schema.raw_rules.get(datatype)
        if not raw_rules:
            print(f"skip {datatype}: no raw rules")
            continue
        modality = DATATYPE_MODALITY.get(datatype, datatype)
        modalities_seen.add(modality)
        out_dir = args.out / modality
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{datatype}.md").write_text(render_datatype(schema, datatype, raw_rules))
        print(f"wrote {out_dir / f'{datatype}.md'}")

    for modality in sorted(modalities_seen):
        out_path = args.out / modality / "_common-metadata.md"
        out_path.write_text(render_modality_common(schema, modality))
        print(f"wrote {out_path}")

    if not args.datatype:
        args.out.mkdir(parents=True, exist_ok=True)
        glossary_path = args.out / "_entities.md"
        glossary_path.write_text(render_entities_glossary(schema))
        print(f"wrote {glossary_path}")


if __name__ == "__main__":
    main()
