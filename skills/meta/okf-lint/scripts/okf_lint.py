#!/usr/bin/env python3
"""OKF conformance linter.

Walks an Open Knowledge Format bundle (a directory tree of markdown files) and
checks it against the OKF v0.1 conformance rules plus the index/log coverage
conventions this config relies on. Deterministic — no LLM, stdlib only (PyYAML
used if available for stricter frontmatter parse checks).

Scope: OKF structure only — frontmatter, reserved files (index.md / log.md), and
index coverage. It does NOT check project-specific directory layouts (sources/,
notes/, outputs/, ...); that is a project convention, not OKF.

Exit codes: 0 = clean (no errors; no warnings under --strict), 1 = findings that
count as failures, 2 = tool/usage error.
"""

import argparse
import datetime
import json
import re
import sys
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

RESERVED = {"index.md", "log.md"}
# Harness-owned markdown that is never an OKF concept (spec scope note): the tool
# owns these fields, and they are intentionally not indexed. Skipped entirely.
EXEMPT = {"SKILL.md", "CLAUDE.md", "README.md", "AGENTS.md", "GEMINI.md"}
# Directory subtrees excluded from all checks. project-init's `sources/` holds
# read-only ingested evidence (never given frontmatter) and `scratch/` is
# disposable and never indexed — neither is authored OKF content.
SKIP_DIRS = {"sources", "scratch"}
INDEX_THRESHOLD = 4  # dirs with this many uncovered concept files want an index.md

# The OKF spec version this linter's rules were written against. The self-check
# below compares it to the vendored spec so drift is announced, not silent.
# When you bump this after a spec revision, review every rule below against the
# new spec and update the project-init CLAUDE.md paraphrase too.
OKF_SPEC_VERSION = "0.1"
VENDORED_SPEC_CANDIDATES = (
    Path.home() / ".claude" / "skills" / "shared" / "okf-spec.md",
)

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?)?$"
)
LOG_DATE_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass
class Finding:
    """A single OKF conformance issue."""

    path: str
    rule: str
    severity: str
    message: str


@dataclass
class FrontMatter:
    """Parsed frontmatter of a markdown file."""

    present: bool
    keys: t.Dict[str, t.Any] = field(default_factory=dict)
    parse_error: t.Optional[str] = None
    body: str = ""


def get_text(path: Path) -> str:
    """Read a file as UTF-8, tolerating undecodable bytes."""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_frontmatter(text: str) -> FrontMatter:
    """Split leading YAML frontmatter from a markdown body.

    Args:
        text (str): full file contents.

    Returns:
        FrontMatter: present flag, parsed top-level keys, parse error, and body.
    """
    stripped = text.lstrip("﻿")
    if not stripped.startswith("---"):
        return FrontMatter(present=False, body=text)

    lines = stripped.splitlines()
    if lines[0].strip() != "---":
        return FrontMatter(present=False, body=text)

    closing = _find_closing_fence(lines)
    if closing is None:
        return FrontMatter(present=True, parse_error="unterminated frontmatter block")

    block = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    return _parse_block(block, body)


def _find_closing_fence(lines: t.List[str]) -> t.Optional[int]:
    """Return the index of the closing `---` line, or None if absent."""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def _parse_block(block: str, body: str) -> FrontMatter:
    """Parse a frontmatter block with PyYAML if present, else a minimal parser."""
    if _HAS_YAML:
        try:
            parsed = yaml.safe_load(block) or {}
        except yaml.YAMLError as exc:
            return FrontMatter(present=True, parse_error=str(exc).splitlines()[0], body=body)
        if not isinstance(parsed, dict):
            return FrontMatter(present=True, parse_error="frontmatter is not a mapping", body=body)
        return FrontMatter(present=True, keys=parsed, body=body)

    return FrontMatter(present=True, keys=_parse_keys_minimal(block), body=body)


def _parse_keys_minimal(block: str) -> t.Dict[str, str]:
    """Extract top-level `key: value` pairs without a YAML library."""
    keys: t.Dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line[0] in " \t#-":
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        keys[key.strip()] = value.strip().strip("\"'")
    return keys


def is_skipped(path: Path, root: Path) -> bool:
    """Check whether a path lies in a skipped subtree (sources/, scratch/)."""
    return any(part in SKIP_DIRS for part in path.relative_to(root).parts)


def is_concept(path: Path) -> bool:
    """Check whether a path is an OKF concept document (non-reserved, non-exempt .md)."""
    return (
        path.suffix == ".md"
        and path.name not in RESERVED
        and path.name not in EXEMPT
        and not path.name.startswith(".")
    )


def get_children(dirpath: Path) -> t.Tuple[t.List[Path], t.List[Path]]:
    """Return (concept files, subdirectories) directly under a directory, hidden excluded."""
    concepts: t.List[Path] = []
    subdirs: t.List[Path] = []
    for child in sorted(dirpath.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            if child.name not in SKIP_DIRS:
                subdirs.append(child)
        elif is_concept(child):
            concepts.append(child)
    return concepts, subdirs


def check_concept(path: Path, root: Path) -> t.List[Finding]:
    """Check a concept document's frontmatter (OKF001/002/008/009/010)."""
    rel = str(path.relative_to(root))
    fm = parse_frontmatter(get_text(path))

    if not fm.present:
        return [Finding(rel, "OKF001", SEVERITY_ERROR, "missing YAML frontmatter block")]
    if fm.parse_error:
        return [Finding(rel, "OKF009", SEVERITY_ERROR, f"unparseable frontmatter: {fm.parse_error}")]

    findings: t.List[Finding] = []
    type_value = fm.keys.get("type")
    if type_value is None or str(type_value).strip() == "":
        findings.append(Finding(rel, "OKF002", SEVERITY_ERROR, "frontmatter missing non-empty `type`"))
    findings.extend(_check_timestamp(fm.keys.get("timestamp"), rel))
    findings.extend(_check_tags(fm.keys.get("tags"), rel))
    return findings


def _check_timestamp(value: t.Any, rel: str) -> t.List[Finding]:
    """Flag a present `timestamp` that is not a valid ISO-8601 date/datetime (OKF008)."""
    if value is None:
        return []
    if isinstance(value, (datetime.date, datetime.datetime)):
        return []
    if ISO_DATETIME.match(str(value).strip()):
        return []
    return [Finding(rel, "OKF008", SEVERITY_WARNING, f"timestamp is not ISO-8601: '{value}'")]


def _check_tags(value: t.Any, rel: str) -> t.List[Finding]:
    """Flag a present `tags` that is not a YAML list (OKF010).

    Only meaningful when PyYAML parsed the frontmatter; the minimal fallback
    parser cannot distinguish a list from a string, so it is skipped there.
    """
    if value is None or not _HAS_YAML:
        return []
    if isinstance(value, list):
        return []
    return [Finding(rel, "OKF010", SEVERITY_WARNING, "tags must be a YAML list, e.g. [a, b]")]


def check_index(path: Path, root: Path) -> t.List[Finding]:
    """Check an index.md for frontmatter and content rules (OKF003, OKF005)."""
    rel = str(path.relative_to(root))
    is_root = path.parent.resolve() == root.resolve()
    text = get_text(path)
    findings = _check_index_frontmatter(text, rel, is_root)
    findings.extend(_check_index_content(text, rel))
    return findings


def _check_index_frontmatter(text: str, rel: str, is_root: bool) -> t.List[Finding]:
    """Index files carry no frontmatter, except the root index (okf_version only)."""
    fm = parse_frontmatter(text)
    if not fm.present:
        return []
    if not is_root:
        return [Finding(rel, "OKF003", SEVERITY_ERROR, "index.md must not carry frontmatter")]
    extra = [k for k in fm.keys if k != "okf_version"]
    if extra:
        return [
            Finding(rel, "OKF003", SEVERITY_ERROR, f"root index.md frontmatter may only hold okf_version, found: {', '.join(extra)}")
        ]
    return []


def _check_index_content(text: str, rel: str) -> t.List[Finding]:
    """Index bodies are pointer lists — flag code fences and tables as content dumps."""
    body = parse_frontmatter(text).body or text
    findings: t.List[Finding] = []
    if "```" in body:
        findings.append(Finding(rel, "OKF005", SEVERITY_WARNING, "index.md contains a code fence — indexes are pointer lists, not content"))
    if any(TABLE_ROW.match(line) for line in body.splitlines()):
        findings.append(Finding(rel, "OKF005", SEVERITY_WARNING, "index.md contains a table — indexes are pointer lists, not content"))
    return findings


def check_log(path: Path, root: Path) -> t.List[Finding]:
    """Check a log.md for frontmatter (OKF003) and ISO date headings (OKF004)."""
    rel = str(path.relative_to(root))
    text = get_text(path)
    findings: t.List[Finding] = []

    if parse_frontmatter(text).present:
        findings.append(Finding(rel, "OKF003", SEVERITY_ERROR, "log.md must not carry frontmatter"))
    findings.extend(_check_log_dates(text, rel))
    return findings


def _check_log_dates(text: str, rel: str) -> t.List[Finding]:
    """Flag `##` date headings that are not ISO YYYY-MM-DD."""
    findings: t.List[Finding] = []
    for line in text.splitlines():
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        if not ISO_DATE.match(heading):
            findings.append(Finding(rel, "OKF004", SEVERITY_WARNING, f"log date heading not ISO YYYY-MM-DD: '{heading}'"))
    return findings


def _get_referenced(index_path: Path) -> t.Set[str]:
    """Return the set of normalized link targets in an index.md."""
    refs: t.Set[str] = set()
    for target in MD_LINK.findall(get_text(index_path)):
        normalized = target.split("#")[0].strip().lstrip("./").rstrip("/")
        if normalized:
            refs.add(normalized)
    return refs


def check_coverage(dirpath: Path, root: Path) -> t.List[Finding]:
    """Check that a directory's index.md references its concepts and indexed subdirs (OKF006)."""
    index_path = dirpath / "index.md"
    if not index_path.exists():
        return []

    refs = _get_referenced(index_path)
    concepts, subdirs = get_children(dirpath)
    findings: t.List[Finding] = []

    for concept in concepts:
        if concept.name not in refs:
            rel = str(concept.relative_to(root))
            findings.append(Finding(rel, "OKF006", SEVERITY_WARNING, f"not referenced in {dirpath.name}/index.md — invisible to future sessions"))

    for subdir in subdirs:
        if not (subdir / "index.md").exists():
            continue
        if subdir.name not in refs and f"{subdir.name}/index.md" not in refs:
            rel = str(subdir.relative_to(root))
            findings.append(Finding(rel, "OKF006", SEVERITY_WARNING, f"indexed subdirectory not referenced in {dirpath.name}/index.md"))
    return findings


def get_uncovered_files(dirpath: Path) -> t.List[Path]:
    """Return concept files rolling up to a directory that lacks indexed coverage.

    Own concept files plus, recursively, those of subdirectories that lack their
    own index.md (an indexed subdirectory covers its whole subtree).
    """
    concepts, subdirs = get_children(dirpath)
    files = list(concepts)
    for subdir in subdirs:
        if (subdir / "index.md").exists():
            continue
        files.extend(get_uncovered_files(subdir))
    return files


def count_uncovered(dirpath: Path) -> int:
    """Count concept files rolling up to a directory that lacks indexed coverage."""
    return len(get_uncovered_files(dirpath))


def check_missing_index(root: Path) -> t.List[Finding]:
    """Flag directories that lack an index.md but hold >= threshold concepts (OKF007).

    Reports the topmost qualifying directory in each branch; adding its index.md
    resolves the branch, so descendants are not separately flagged.
    """
    findings: t.List[Finding] = []
    _walk_missing_index(root, root, findings)
    return findings


def _walk_missing_index(dirpath: Path, root: Path, findings: t.List[Finding]) -> None:
    """Top-down walk emitting one OKF007 per qualifying branch."""
    has_index = (dirpath / "index.md").exists()
    if not has_index and count_uncovered(dirpath) >= INDEX_THRESHOLD:
        rel = str(dirpath.relative_to(root)) or "."
        findings.append(Finding(rel, "OKF007", SEVERITY_WARNING, f"directory has {INDEX_THRESHOLD}+ concept files but no index.md"))
        return

    _, subdirs = get_children(dirpath)
    for subdir in subdirs:
        _walk_missing_index(subdir, root, findings)


def check_spec_version() -> t.List[Finding]:
    """Warn if the vendored spec's version no longer matches the linter's rules.

    Best-effort: if the vendored spec cannot be found or declares no version, the
    check is skipped silently. This is a maintenance nudge, not a per-file issue.
    """
    spec = next((p for p in VENDORED_SPEC_CANDIDATES if p.is_file()), None)
    if spec is None:
        return []
    declared = parse_frontmatter(get_text(spec)).keys.get("okf_version")
    if declared is None or str(declared) == OKF_SPEC_VERSION:
        return []
    return [
        Finding(
            "(okf-lint)",
            "OKF000",
            SEVERITY_WARNING,
            f"linter implements OKF {OKF_SPEC_VERSION} but vendored spec declares {declared} — "
            "review okf_lint.py and the project-init template against the new spec",
        )
    ]


def lint_bundle(root: Path) -> t.List[Finding]:
    """Run every OKF check across a bundle and return all findings."""
    findings: t.List[Finding] = []
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        if path.name in EXEMPT or is_skipped(path, root):
            continue
        findings.extend(_lint_one_file(path, root))

    for dirpath in _iter_dirs(root):
        findings.extend(check_coverage(dirpath, root))
    findings.extend(check_missing_index(root))
    return findings


def _lint_one_file(path: Path, root: Path) -> t.List[Finding]:
    """Dispatch a single markdown file to the right checker by filename."""
    if path.name == "index.md":
        return check_index(path, root)
    if path.name == "log.md":
        return check_log(path, root)
    return check_concept(path, root)


def _iter_dirs(root: Path) -> t.List[Path]:
    """Return root and every non-hidden, non-skipped subdirectory."""
    dirs = [root]
    for path in sorted(root.rglob("*")):
        if not path.is_dir():
            continue
        parts = path.relative_to(root).parts
        if any(part.startswith(".") for part in parts) or any(part in SKIP_DIRS for part in parts):
            continue
        dirs.append(path)
    return dirs


def fix_missing_indexes(root: Path) -> t.List[str]:
    """Create a generated index.md wherever the house rule (OKF007) requires one.

    Enforces exactly the threshold: an index is created only in a directory
    whose uncovered concept count reaches INDEX_THRESHOLD. Runs deepest-first
    so a newly indexed subdirectory covers its subtree before its parent is
    counted — mirroring the coverage semantics. Safe, deterministic fix only:
    never creates an index below the threshold, never edits an existing
    index.md, and never touches frontmatter. Descriptions/Load-when triggers
    and entries added to existing indexes are left for the /okf-lint skill
    (agent judgment).
    """
    created: t.List[str] = []
    for dirpath in sorted(_iter_dirs(root), key=lambda p: len(p.parts), reverse=True):
        if (dirpath / "index.md").exists():
            continue
        if count_uncovered(dirpath) < INDEX_THRESHOLD:
            continue
        _write_generated_index(dirpath)
        created.append(str((dirpath / "index.md").relative_to(root)))
    return created


def _write_generated_index(dirpath: Path) -> None:
    """Write a pointer-list index.md covering the directory's uncovered files.

    Files in unindexed subdirectories are listed directly by relative path,
    per the house rule; indexed subdirectories get a # Subdirectories entry
    pointing at their own index.md.
    """
    _, subdirs = get_children(dirpath)
    indexed_subdirs = [s for s in subdirs if (s / "index.md").exists()]
    title = dirpath.name.replace("-", " ").replace("_", " ").title() or "Index"
    lines = [f"# {title}", ""]
    for concept in get_uncovered_files(dirpath):
        fm = parse_frontmatter(get_text(concept))
        display = str(fm.keys.get("title") or concept.stem)
        desc = str(fm.keys.get("description") or "").strip()
        suffix = f" - {desc}" if desc else ""
        lines.append(f"* [{display}]({concept.relative_to(dirpath).as_posix()}){suffix}")
    if indexed_subdirs:
        lines.extend(["", "# Subdirectories", ""])
        for subdir in indexed_subdirs:
            display = subdir.name.replace("-", " ").replace("_", " ").title()
            lines.append(f"* [{display}]({subdir.name}/index.md)")
    (dirpath / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_text(findings: t.List[Finding]) -> str:
    """Render findings as grouped, human-readable text."""
    if not findings:
        return "OKF: clean — no findings."
    order = {SEVERITY_ERROR: 0, SEVERITY_WARNING: 1}
    ordered = sorted(findings, key=lambda f: (order.get(f.severity, 9), f.path, f.rule))
    lines = [f"  [{f.severity.upper():7}] {f.rule}  {f.path}: {f.message}" for f in ordered]
    errors = sum(1 for f in findings if f.severity == SEVERITY_ERROR)
    warnings = len(findings) - errors
    lines.append(f"\n{errors} error(s), {warnings} warning(s).")
    return "\n".join(lines)


def format_json(findings: t.List[Finding], fixed: t.List[str]) -> str:
    """Render findings and applied fixes as JSON."""
    payload = {
        "findings": [f.__dict__ for f in findings],
        "errors": sum(1 for f in findings if f.severity == SEVERITY_ERROR),
        "warnings": sum(1 for f in findings if f.severity == SEVERITY_WARNING),
        "fixed": fixed,
    }
    return json.dumps(payload, indent=2)


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Lint an OKF bundle for conformance.")
    parser.add_argument("path", nargs="?", default=".", help="bundle root to lint (default: cwd)")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures (exit 1)")
    parser.add_argument("--errors-only", action="store_true", help="show and count errors only")
    parser.add_argument("--fix", action="store_true", help="create the index.md files the house rule requires (OKF007; safe fixes only)")
    parser.add_argument("--quiet", action="store_true", help="suppress the clean-bundle message")
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the lint (and optional fix) and return the process exit code."""
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"okf-lint: not a directory: {root}", file=sys.stderr)
        return 2

    fixed = fix_missing_indexes(root) if args.fix else []
    findings = lint_bundle(root)
    findings.extend(check_spec_version())
    if args.errors_only:
        findings = [f for f in findings if f.severity == SEVERITY_ERROR]

    _emit(findings, fixed, args)

    has_errors = any(f.severity == SEVERITY_ERROR for f in findings)
    has_warnings = any(f.severity == SEVERITY_WARNING for f in findings)
    if has_errors or (args.strict and has_warnings):
        return 1
    return 0


def _emit(findings: t.List[Finding], fixed: t.List[str], args: argparse.Namespace) -> None:
    """Print results in the requested format."""
    if args.json:
        print(format_json(findings, fixed))
        return
    if fixed:
        print("Created index.md in: " + ", ".join(fixed) + "\n")
    if findings or not args.quiet:
        print(format_text(findings))


def main() -> int:
    """CLI entrypoint."""
    return run(build_parser().parse_args())


if __name__ == "__main__":
    sys.exit(main())
