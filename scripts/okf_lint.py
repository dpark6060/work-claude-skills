#!/usr/bin/env python3
"""Lint skill reference files for OKF conformance.

Checks, per the vendored spec (skills/shared/okf-spec.md):
1. Every concept .md under a skills/*/*/references/ tree (and skills/shared/)
   has YAML frontmatter with a non-empty `type` field.
2. Every directory whose "uncovered" concept count reaches 4 has an index.md.
   Uncovered = the directory's own concept files, plus (recursively) the
   uncovered count of every subdirectory that lacks its own index.md. An
   indexed subdirectory covers its subtree and contributes zero; an unindexed
   one passes its files up to the parent's count.
3. index.md files carry no frontmatter (a bundle root may carry a lone
   `okf_version` block).

Exit 0 when clean, 1 with one finding per line otherwise.
"""

import re
import sys
import typing as t
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESERVED_NAMES = {"index.md", "log.md"}
SKIP_DIR_NAMES = {"scripts", "server", "cache", "sources", ".learnings", "tools"}
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.DOTALL)
TYPE_RE = re.compile(r"^type:\s*\S", re.MULTILINE)


def get_bundle_roots() -> t.List[Path]:
    """Collect every directory treated as an OKF bundle root."""
    roots = [p for p in REPO_ROOT.glob("skills/*/*/references") if p.is_dir()]
    shared = REPO_ROOT / "skills" / "shared"
    if shared.is_dir():
        roots.append(shared)
    return sorted(roots)


def get_frontmatter(path: Path) -> t.Optional[str]:
    """Return the raw frontmatter block of a markdown file, or None."""
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8", errors="replace"))
    return match.group(1) if match else None


def validate_concept_file(path: Path) -> t.List[str]:
    """Rule 1: concept files carry frontmatter with a non-empty type."""
    frontmatter = get_frontmatter(path)
    if frontmatter is None:
        return [f"{path}: missing YAML frontmatter (OKF requires `type`)"]
    if not TYPE_RE.search(frontmatter):
        return [f"{path}: frontmatter has no non-empty `type` field"]
    return []


INDEX_THRESHOLD = 4


def validate_index_presence(directory: Path, uncovered_count: int) -> t.List[str]:
    """Rule 2: directories with INDEX_THRESHOLD+ uncovered concepts carry an index.md."""
    if uncovered_count < INDEX_THRESHOLD:
        return []
    if (directory / "index.md").exists():
        return []
    return [
        f"{directory}: has {uncovered_count} uncovered concept files "
        f"(threshold {INDEX_THRESHOLD}) but no index.md"
    ]


def validate_index_file(path: Path, is_bundle_root: bool) -> t.List[str]:
    """Rule 3: index.md has no frontmatter (root may carry okf_version only)."""
    frontmatter = get_frontmatter(path)
    if frontmatter is None:
        return []
    keys = {line.split(":")[0].strip() for line in frontmatter.splitlines() if ":" in line}
    if is_bundle_root and keys <= {"okf_version"}:
        return []
    return [f"{path}: index.md must not carry frontmatter (found keys: {sorted(keys)})"]


def validate_directory(directory: Path, root: Path, errors: t.List[str]) -> int:
    """Run all checks for one directory inside a bundle.

    Returns the directory's contribution to its parent's uncovered count:
    0 if this directory has an index.md, else its own uncovered count.
    """
    concepts = [p for p in directory.glob("*.md") if p.name not in RESERVED_NAMES]
    subdirs_with_md = [
        d for d in directory.iterdir()
        if d.is_dir() and d.name not in SKIP_DIR_NAMES and any(d.rglob("*.md"))
    ]

    for concept in concepts:
        errors.extend(validate_concept_file(concept))

    uncovered = len(concepts)
    for subdir in subdirs_with_md:
        uncovered += validate_directory(subdir, root, errors)

    errors.extend(validate_index_presence(directory, uncovered))

    index_file = directory / "index.md"
    if index_file.exists():
        errors.extend(validate_index_file(index_file, is_bundle_root=directory == root))
        return 0
    return uncovered


def run_lint() -> int:
    """Lint every bundle root; print findings and return an exit code."""
    errors: t.List[str] = []
    for root in get_bundle_roots():
        validate_directory(root, root, errors)
    for error in errors:
        print(error)
    if errors:
        print(f"\n{len(errors)} OKF conformance error(s). Spec: skills/shared/okf-spec.md")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(run_lint())
