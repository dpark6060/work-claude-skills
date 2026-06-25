#!/usr/bin/env python3
"""Build a searchable, code-grounded index of the Flywheel BIDS tooling repos.

This is the *depth layer* under the curated `references/flywheel/*.md` overviews.
When a technical question can't be answered from the lean markdown, the skill
searches this index (scripts/search_code.py) and reads the actual source.

Unlike the llm-knowledge-consolidation POC, there is NO LLM distill step: the
cards hold ground-truth source (signature + docstring + real code, or a real
template rule), not a paraphrase. The skill is the reasoner — it reads the code
directly — so a lossy summary layer would only add error. That also makes this
fully deterministic and free to regenerate when the repos update.

Two extractors:
  - Python symbols (stdlib `ast`): every function / class / method as a card.
  - Curation template JSON: every rule and definition in the base templates as
    a card (the real `where`/`initialize`/`auto_update`).

Output:
  references/flywheel/code-index/cards.jsonl   — one card per line (the database)
  references/flywheel/code-index/code-manifest.md — repo commit SHAs + counts

Usage:
    python build_code_index.py [--pull]
    # --pull runs `git pull` in each repo first to index the latest versions
"""

import argparse
import ast
import json
import subprocess
import typing as t
from pathlib import Path

# Repos to index: (repo label, absolute path, list of subdirs/files to walk).
# Paths are the local checkouts; `--pull` updates them before indexing.
REPOS: t.List[t.Dict[str, t.Any]] = [
    {
        "label": "bids-client",
        "path": Path("/Users/davidparker/Documents/Flywheel/GitLab/public/bids-client"),
        "code_roots": ["flywheel_bids"],
        "template_globs": ["flywheel_bids/templates/*.json"],
    },
    {
        "label": "curate-bids",
        "path": Path("/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/Bids-Curator-gear/curate-bids"),
        "code_roots": ["fw_curate_bids", "run.py"],
        "template_globs": [],
    },
    {
        "label": "relabel-container",
        "path": Path("/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears/Bids_precurate_Gitlab/relabel-container"),
        "code_roots": ["fw_gear_relabel_container", "run.py"],
        "template_globs": [],
    },
]

EXCLUDE_PARTS = {"tests", "test", ".venv", "venv", "build", "dist", "__pycache__", "node_modules"}


def should_skip(path: Path) -> bool:
    """True if a file is a test/vendor/generated file we don't want to index."""
    parts = set(path.parts)
    if parts & EXCLUDE_PARTS:
        return True
    name = path.name
    return name.startswith("test_") or name.endswith("_test.py") or name in {"conftest.py", "setup.py"}


def git_sha(repo: Path) -> str:
    """Return short SHA + nearest tag for a repo, or 'unknown'."""
    try:
        sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True).strip()
        desc = subprocess.check_output(["git", "-C", str(repo), "describe", "--tags", "--always"], text=True).strip()
        return f"{sha} ({desc})"
    except subprocess.CalledProcessError:
        return "unknown"


def git_pull(repo: Path) -> None:
    """Pull the latest on the repo's current branch (best effort)."""
    try:
        subprocess.run(["git", "-C", str(repo), "pull", "--ff-only"], check=True)
    except subprocess.CalledProcessError as exc:
        print(f"  warning: git pull failed for {repo}: {exc}")


def iter_py_files(repo: Path, code_roots: t.List[str]) -> t.Iterator[Path]:
    """Yield indexable .py files under the given roots of a repo."""
    for root in code_roots:
        target = repo / root
        if target.is_file() and target.suffix == ".py":
            if not should_skip(target):
                yield target
        elif target.is_dir():
            for path in sorted(target.rglob("*.py")):
                if not should_skip(path):
                    yield path


def extract_python(repo_label: str, repo_path: Path, file_path: Path) -> t.List[dict]:
    """Extract function/class/method cards from one Python file via ast."""
    source = file_path.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines(keepends=True)
    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        print(f"  skip {file_path} (syntax error: {exc})")
        return []

    rel = file_path.relative_to(repo_path).as_posix()
    cards: t.List[dict] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cards.append(_py_card(repo_label, rel, lines, node, node.name))
        elif isinstance(node, ast.ClassDef):
            cards.append(_class_card(repo_label, rel, lines, node))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cards.append(_py_card(repo_label, rel, lines, sub, f"{node.name}.{sub.name}"))
    return cards


def _span(lines: t.List[str], node: ast.AST) -> t.Tuple[int, str]:
    """Return (start_line, full_source) for a node, including any decorators."""
    starts = [node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])]
    start = min(starts)
    end = getattr(node, "end_lineno", node.lineno)
    return start, "".join(lines[start - 1 : end])


def _signature(lines: t.List[str], node: ast.AST) -> str:
    """Reconstruct the def/class signature (decorators through the colon line)."""
    start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    body_line = node.body[0].lineno if node.body else node.lineno
    sig = "".join(lines[start - 1 : body_line - 1]).strip()
    return sig if sig else lines[node.lineno - 1].strip()


def _py_card(repo: str, rel: str, lines: t.List[str], node: ast.AST, name: str) -> dict:
    """Build a card for a function or method."""
    start, text = _span(lines, node)
    return {
        "id": f"{repo}:{rel}:{name}",
        "kind": "code",
        "repo": repo,
        "path": rel,
        "line": start,
        "name": name,
        "signature": _signature(lines, node),
        "doc": ast.get_docstring(node) or "",
        "text": text,
    }


def _class_card(repo: str, rel: str, lines: t.List[str], node: ast.ClassDef) -> dict:
    """Build a card for a class (signature + docstring + method list, no bodies)."""
    methods = [s.name for s in node.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
    doc = ast.get_docstring(node) or ""
    body = f"{_signature(lines, node)}\n\nMethods: {', '.join(methods) or '(none)'}"
    return {
        "id": f"{repo}:{rel}:{node.name}",
        "kind": "code",
        "repo": repo,
        "path": rel,
        "line": node.lineno,
        "name": node.name,
        "signature": _signature(lines, node),
        "doc": doc,
        "text": body,
    }


def extract_templates(repo_label: str, repo_path: Path, globs: t.List[str]) -> t.List[dict]:
    """Extract per-rule and per-definition cards from curation template JSONs."""
    cards: t.List[dict] = []
    for glob in globs:
        for path in sorted(repo_path.glob(glob)):
            cards.extend(_template_cards(repo_label, repo_path, path))
    return cards


def _template_cards(repo: str, repo_path: Path, path: Path) -> t.List[dict]:
    """Build rule and definition cards from one template JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  skip template {path} ({exc})")
        return []
    rel = path.relative_to(repo_path).as_posix()
    template_name = data.get("json_name") or path.stem
    cards: t.List[dict] = []

    for rule in data.get("rules", []) + data.get("upload_rules", []):
        rule_id = rule.get("id") or rule.get("template") or "rule"
        cards.append({
            "id": f"{repo}:{rel}:rule:{rule_id}",
            "kind": "template-rule",
            "repo": repo,
            "path": rel,
            "name": f"{template_name} rule {rule_id}",
            "doc": f"Rule applying template '{rule.get('template', '')}' in {template_name}.",
            "text": json.dumps(rule, indent=2),
        })
    for def_name, definition in (data.get("definitions") or {}).items():
        cards.append({
            "id": f"{repo}:{rel}:def:{def_name}",
            "kind": "template-def",
            "repo": repo,
            "path": rel,
            "name": f"{template_name} definition {def_name}",
            "doc": f"Definition '{def_name}' in template {template_name}.",
            "text": json.dumps(definition, indent=2),
        })
    return cards


def build(out_dir: Path, do_pull: bool) -> None:
    """Run both extractors over all repos and write cards.jsonl + manifest."""
    out_dir.mkdir(parents=True, exist_ok=True)
    all_cards: t.List[dict] = []
    manifest_rows: t.List[str] = []

    for repo in REPOS:
        label, path = repo["label"], repo["path"]
        if not path.exists():
            print(f"skip {label}: {path} not found")
            continue
        if do_pull:
            git_pull(path)
        print(f"indexing {label} ...")
        before = len(all_cards)
        for py_file in iter_py_files(path, repo["code_roots"]):
            all_cards.extend(extract_python(label, path, py_file))
        all_cards.extend(extract_templates(label, path, repo["template_globs"]))
        count = len(all_cards) - before
        sha = git_sha(path)
        manifest_rows.append(f"| {label} | {sha} | {count} |")
        print(f"  {count} cards, {sha}")

    cards_path = out_dir / "cards.jsonl"
    with cards_path.open("w", encoding="utf-8") as fh:
        for card in all_cards:
            fh.write(json.dumps(card, ensure_ascii=False) + "\n")

    _write_manifest(out_dir / "code-manifest.md", manifest_rows, len(all_cards))
    print(f"wrote {cards_path} ({len(all_cards)} cards)")


def _write_manifest(path: Path, rows: t.List[str], total: int) -> None:
    """Write the provenance manifest (repo SHAs + counts + regen command)."""
    content = "\n".join([
        "# Flywheel code index — provenance",
        "",
        f"Total cards: **{total}**. Ground-truth source/template snippets, no LLM paraphrase.",
        "",
        "| Repo | Commit | Cards |",
        "| --- | --- | --- |",
        *rows,
        "",
        "## Regenerate (latest repo versions)",
        "",
        "```bash",
        "python scripts/build_code_index.py --pull",
        "```",
        "",
        "Search it with `python scripts/search_code.py \"<query>\"`.",
        "",
    ])
    path.write_text(content)


def main() -> None:
    """Parse args and build the index."""
    skill_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pull", action="store_true", help="git pull each repo before indexing")
    parser.add_argument("--out", type=Path, default=skill_root / "references" / "flywheel" / "code-index")
    args = parser.parse_args()
    build(args.out, args.pull)


if __name__ == "__main__":
    main()
