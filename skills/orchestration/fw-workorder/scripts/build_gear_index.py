"""Builds the gear index: gear manifest name -> local repo location and remotes.

Directory names under the gears root are not a usable index. The real repository is
usually nested one level below a wrapper directory, and the gear's actual name only
appears in `manifest.json:name`. This script scans for manifests, resolves the git
repository enclosing each one, and writes a lookup keyed on the manifest name.

Usage:
    python build_gear_index.py [--gears-root PATH] [--output PATH] [--quiet]

Writes JSON to the output path and prints a one-line summary to stdout.
"""

import argparse
import json
import subprocess
import typing as t
from dataclasses import dataclass, asdict
from pathlib import Path

DEFAULT_GEARS_ROOT = Path("/Users/davidparker/Documents/Flywheel/SSE/MyWork/Gears")
DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent / "cache" / "gear-index.json"
MANIFEST_SCAN_DEPTH = 3

FORGE_PATTERNS = {
    "gitlab": "gitlab.com",
    "github": "github.com",
}


@dataclass
class GearEntry:
    """One gear's resolved location, remotes, and git state."""

    name: str
    version: t.Optional[str]
    manifest_path: str
    repo_path: t.Optional[str]
    remotes: t.Dict[str, str]
    origin_forge: t.Optional[str]
    mirror_remotes: t.List[str]
    default_branch: t.Optional[str]
    is_dirty: t.Optional[bool]


def get_manifest_paths(gears_root: Path, max_depth: int = MANIFEST_SCAN_DEPTH) -> t.List[Path]:
    """Finds every manifest.json under the gears root, up to max_depth levels deep.

    Args:
        gears_root (Path): Directory holding the gear working copies.
        max_depth (int): How many directory levels below the root to search.

    Returns:
        List[Path]: Sorted manifest paths.
    """
    manifests: t.List[Path] = []
    for depth in range(1, max_depth + 1):
        pattern = "/".join(["*"] * depth) + "/manifest.json"
        manifests.extend(gears_root.glob(pattern))
    return sorted(set(manifests))


def get_manifest_fields(manifest_path: Path) -> t.Optional[t.Tuple[str, t.Optional[str]]]:
    """Reads the gear name and version out of a manifest.

    Args:
        manifest_path (Path): Path to a gear manifest.json.

    Returns:
        Tuple[str, Optional[str]] or None: (name, version), or None if the manifest is
        unreadable or has no name.
    """
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(manifest, dict):
        return None

    name = manifest.get("name")
    if not name or not isinstance(name, str):
        return None

    version = manifest.get("version")
    return name, str(version) if version is not None else None


def run_git(repo_path: Path, *args: str) -> t.Optional[str]:
    """Runs a git command in a repo and returns stripped stdout, or None on failure."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_repo_path(manifest_path: Path, gears_root: Path) -> t.Optional[Path]:
    """Finds the git repository containing a manifest.

    Walks upward from the manifest looking for a `.git` entry, stopping at the gears
    root so a stray manifest never resolves to an unrelated parent repository.

    Args:
        manifest_path (Path): Path to a gear manifest.json.
        gears_root (Path): Boundary directory; the walk does not go above it.

    Returns:
        Optional[Path]: The repository root, or None if the manifest is not in a repo.
    """
    for candidate in [manifest_path.parent, *manifest_path.parent.parents]:
        if (candidate / ".git").exists():
            return candidate
        if candidate == gears_root:
            return None
    return None


def get_remotes(repo_path: Path) -> t.Dict[str, str]:
    """Returns a {remote name: fetch URL} mapping for a repository."""
    output = run_git(repo_path, "remote", "-v")
    if not output:
        return {}

    remotes: t.Dict[str, str] = {}
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "(fetch)":
            remotes[parts[0]] = parts[1]
    return remotes


def get_forge(remote_url: str) -> t.Optional[str]:
    """Identifies the hosting forge from a remote URL."""
    for forge, host in FORGE_PATTERNS.items():
        if host in remote_url:
            return forge
    return None


def get_mirror_remotes(remotes: t.Dict[str, str]) -> t.List[str]:
    """Returns every remote name that is not `origin`.

    These are client mirrors (e.g. the `nacc` GitHub remote alongside a GitLab
    `origin`). They are published by a human at release time and must never be
    pushed automatically.
    """
    return sorted(name for name in remotes if name != "origin")


def get_default_branch(repo_path: Path) -> t.Optional[str]:
    """Returns the repository's default branch, without hitting the network."""
    head_ref = run_git(repo_path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if head_ref:
        return head_ref.split("/", 1)[-1]
    return run_git(repo_path, "branch", "--show-current")


def get_is_dirty(repo_path: Path) -> t.Optional[bool]:
    """Returns True when the working tree has uncommitted changes."""
    status = run_git(repo_path, "status", "--porcelain")
    if status is None:
        return None
    return bool(status)


def build_gear_entry(manifest_path: Path, gears_root: Path) -> t.Optional[GearEntry]:
    """Builds one index entry from a manifest path.

    Args:
        manifest_path (Path): Path to a gear manifest.json.
        gears_root (Path): Boundary directory for the repository walk.

    Returns:
        Optional[GearEntry]: The entry, or None if the manifest has no usable name.
    """
    fields = get_manifest_fields(manifest_path)
    if not fields:
        return None

    name, version = fields
    repo_path = get_repo_path(manifest_path, gears_root)
    if not repo_path:
        return GearEntry(
            name=name,
            version=version,
            manifest_path=str(manifest_path),
            repo_path=None,
            remotes={},
            origin_forge=None,
            mirror_remotes=[],
            default_branch=None,
            is_dirty=None,
        )

    remotes = get_remotes(repo_path)
    origin_url = remotes.get("origin", "")
    return GearEntry(
        name=name,
        version=version,
        manifest_path=str(manifest_path),
        repo_path=str(repo_path),
        remotes=remotes,
        origin_forge=get_forge(origin_url) if origin_url else None,
        mirror_remotes=get_mirror_remotes(remotes),
        default_branch=get_default_branch(repo_path),
        is_dirty=get_is_dirty(repo_path),
    )


def build_gear_index(gears_root: Path) -> t.Dict[str, dict]:
    """Builds the full gear index for a gears root.

    When two manifests declare the same gear name, the one whose repository has a
    configured `origin` wins; ties fall to the shallower path. Scratch copies of a
    gear therefore lose to the real working copy.

    Args:
        gears_root (Path): Directory holding the gear working copies.

    Returns:
        Dict[str, dict]: {gear name: entry}, sorted by gear name.
    """
    index: t.Dict[str, GearEntry] = {}
    for manifest_path in get_manifest_paths(gears_root):
        entry = build_gear_entry(manifest_path, gears_root)
        if not entry:
            continue
        existing = index.get(entry.name)
        if existing and not is_better_entry(entry, existing):
            continue
        index[entry.name] = entry

    return {name: asdict(index[name]) for name in sorted(index)}


def is_better_entry(candidate: GearEntry, existing: GearEntry) -> bool:
    """Decides whether a candidate entry should replace an existing one for the same gear."""
    candidate_has_origin = "origin" in candidate.remotes
    existing_has_origin = "origin" in existing.remotes
    if candidate_has_origin != existing_has_origin:
        return candidate_has_origin
    return len(candidate.manifest_path) < len(existing.manifest_path)


def run_build(gears_root: Path, output_path: Path, quiet: bool = False) -> t.Dict[str, dict]:
    """Builds the index and writes it to disk.

    Args:
        gears_root (Path): Directory holding the gear working copies.
        output_path (Path): Where to write the JSON index.
        quiet (bool): Suppress the stdout summary.

    Returns:
        Dict[str, dict]: The index that was written.
    """
    index = build_gear_index(gears_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(index, indent=2, sort_keys=True))

    if not quiet:
        dirty = sum(1 for entry in index.values() if entry["is_dirty"])
        mirrored = sum(1 for entry in index.values() if entry["mirror_remotes"])
        print(
            f"{len(index)} gears indexed -> {output_path} "
            f"({dirty} dirty, {mirrored} with mirror remotes)"
        )
    return index


def main() -> None:
    """Parses arguments and builds the gear index."""
    parser = argparse.ArgumentParser(description="Build the fw-workorder gear index.")
    parser.add_argument("--gears-root", type=Path, default=DEFAULT_GEARS_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not args.gears_root.is_dir():
        raise SystemExit(f"Gears root does not exist: {args.gears_root}")

    run_build(args.gears_root, args.output, quiet=args.quiet)


if __name__ == "__main__":
    main()
