"""Unit tests for build_gear_index."""

import json
import subprocess
import typing as t
from pathlib import Path

import pytest

from build_gear_index import (
    build_gear_entry,
    build_gear_index,
    get_default_branch,
    get_forge,
    get_manifest_fields,
    get_manifest_paths,
    get_mirror_remotes,
    get_remotes,
    get_repo_path,
    is_better_entry,
    run_build,
)

GITLAB_URL = "git@gitlab.com:flywheel-io/scientific-solutions/gears/nacc/loni-upload.git"
GITHUB_URL = "git@github.com:naccdata/fw-loni-export.git"


def write_manifest(directory: Path, name: str, version: str = "1.0.0") -> Path:
    """Writes a minimal gear manifest and returns its path."""
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "manifest.json"
    manifest_path.write_text(json.dumps({"name": name, "version": version}))
    return manifest_path


def init_repo(directory: Path, remotes: t.Optional[t.Dict[str, str]] = None) -> Path:
    """Initializes a git repo with one commit and the given remotes."""
    directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(directory)], check=True)
    subprocess.run(["git", "-C", str(directory), "config", "user.email", "t@t.io"], check=True)
    subprocess.run(["git", "-C", str(directory), "config", "user.name", "T"], check=True)
    (directory / "README.md").write_text("x")
    subprocess.run(["git", "-C", str(directory), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(directory), "commit", "-qm", "init"], check=True)
    for remote_name, url in (remotes or {}).items():
        subprocess.run(
            ["git", "-C", str(directory), "remote", "add", remote_name, url], check=True
        )
    return directory


def commit_all(directory: Path) -> None:
    """Stages and commits everything in the repo."""
    subprocess.run(["git", "-C", str(directory), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(directory), "commit", "-qm", "manifest"], check=True)


@pytest.fixture
def nested_gear(tmp_path: Path) -> Path:
    """A wrapper directory holding the real repo one level down, with dual remotes."""
    repo = tmp_path / "NACC-loni-upload-gear" / "nacc-loni-uploader"
    init_repo(repo, {"origin": GITLAB_URL, "nacc": GITHUB_URL})
    write_manifest(repo, "loni-upload", "2.0.0")
    commit_all(repo)
    (tmp_path / "NACC-loni-upload-gear" / "notes.pdf").write_text("x")
    return tmp_path


def test_getmanifestpaths_nested_manifest_is_found(nested_gear: Path):
    # Act
    manifests = get_manifest_paths(nested_gear)

    # Assert
    assert len(manifests) == 1
    assert manifests[0].parent.name == "nacc-loni-uploader"


def test_getmanifestpaths_respects_max_depth(tmp_path: Path):
    # Arrange
    write_manifest(tmp_path / "a" / "b" / "c" / "d", "too-deep")

    # Act & Assert
    assert get_manifest_paths(tmp_path, max_depth=3) == []
    assert len(get_manifest_paths(tmp_path, max_depth=4)) == 1


def test_getmanifestfields_returns_name_and_version(tmp_path: Path):
    # Arrange
    manifest_path = write_manifest(tmp_path, "redcap-processor", "0.4.0")

    # Act
    fields = get_manifest_fields(manifest_path)

    # Assert
    assert fields == ("redcap-processor", "0.4.0")


def test_getmanifestfields_malformed_json_returns_none(tmp_path: Path):
    # Arrange
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text("{not json")

    # Act & Assert
    assert get_manifest_fields(manifest_path) is None


def test_getmanifestfields_missing_name_returns_none(tmp_path: Path):
    # Arrange
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"version": "1.0.0"}))

    # Act & Assert
    assert get_manifest_fields(manifest_path) is None


def test_getrepopath_finds_enclosing_repo(nested_gear: Path):
    # Arrange
    manifest_path = get_manifest_paths(nested_gear)[0]

    # Act
    repo_path = get_repo_path(manifest_path, nested_gear)

    # Assert
    assert repo_path == manifest_path.parent


def test_getrepopath_manifest_outside_any_repo_returns_none(tmp_path: Path):
    # Arrange
    manifest_path = write_manifest(tmp_path / "loose-gear", "loose")

    # Act & Assert
    assert get_repo_path(manifest_path, tmp_path) is None


def test_getrepopath_does_not_walk_above_gears_root(tmp_path: Path):
    # Arrange — a repo ABOVE the gears root must not be claimed
    init_repo(tmp_path)
    gears_root = tmp_path / "gears"
    manifest_path = write_manifest(gears_root / "some-gear", "some-gear")

    # Act & Assert
    assert get_repo_path(manifest_path, gears_root) is None


def test_getremotes_returns_all_configured_remotes(nested_gear: Path):
    # Arrange
    repo = nested_gear / "NACC-loni-upload-gear" / "nacc-loni-uploader"

    # Act
    remotes = get_remotes(repo)

    # Assert
    assert remotes == {"origin": GITLAB_URL, "nacc": GITHUB_URL}


@pytest.mark.parametrize(
    "url,expected",
    [
        (GITLAB_URL, "gitlab"),
        (GITHUB_URL, "github"),
        ("https://github.com/flywheel-apps/GRP-9.git", "github"),
        ("git@bitbucket.org:someone/thing.git", None),
    ],
)
def test_getforge_identifies_host(url: str, expected: t.Optional[str]):
    assert get_forge(url) == expected


def test_getmirrorremotes_excludes_origin():
    # Act
    mirrors = get_mirror_remotes({"origin": GITLAB_URL, "nacc": GITHUB_URL})

    # Assert
    assert mirrors == ["nacc"]


def test_getmirrorremotes_no_mirrors_returns_empty():
    assert get_mirror_remotes({"origin": GITLAB_URL}) == []


def test_getdefaultbranch_falls_back_to_current_branch(nested_gear: Path):
    # Arrange — no origin/HEAD ref exists on a local-only repo
    repo = nested_gear / "NACC-loni-upload-gear" / "nacc-loni-uploader"

    # Act & Assert
    assert get_default_branch(repo) == "main"


def test_buildgearentry_dual_remote_repo_is_fully_resolved(nested_gear: Path):
    # Arrange
    manifest_path = get_manifest_paths(nested_gear)[0]

    # Act
    entry = build_gear_entry(manifest_path, nested_gear)

    # Assert
    assert entry.name == "loni-upload"
    assert entry.version == "2.0.0"
    assert entry.origin_forge == "gitlab"
    assert entry.mirror_remotes == ["nacc"]
    assert entry.default_branch == "main"
    assert entry.is_dirty is False


def test_buildgearentry_dirty_tree_is_flagged(nested_gear: Path):
    # Arrange
    repo = nested_gear / "NACC-loni-upload-gear" / "nacc-loni-uploader"
    (repo / "README.md").write_text("modified")
    manifest_path = get_manifest_paths(nested_gear)[0]

    # Act
    entry = build_gear_entry(manifest_path, nested_gear)

    # Assert
    assert entry.is_dirty is True


def test_buildgearentry_manifest_without_repo_returns_entry_with_no_repo(tmp_path: Path):
    # Arrange
    manifest_path = write_manifest(tmp_path / "loose-gear", "loose")

    # Act
    entry = build_gear_entry(manifest_path, tmp_path)

    # Assert
    assert entry.name == "loose"
    assert entry.repo_path is None
    assert entry.remotes == {}
    assert entry.is_dirty is None


def test_buildgearindex_keys_on_manifest_name_not_directory_name(nested_gear: Path):
    # Act
    index = build_gear_index(nested_gear)

    # Assert — the directory is nacc-loni-uploader, the gear is loni-upload
    assert "loni-upload" in index
    assert "nacc-loni-uploader" not in index


def test_buildgearindex_duplicate_name_prefers_repo_with_origin(tmp_path: Path):
    # Arrange — a scratch copy with no remote, and the real copy with origin
    scratch = tmp_path / "scratch"
    init_repo(scratch)
    write_manifest(scratch, "loni-upload")

    real = tmp_path / "real-gear" / "loni-upload"
    init_repo(real, {"origin": GITLAB_URL})
    write_manifest(real, "loni-upload")

    # Act
    index = build_gear_index(tmp_path)

    # Assert
    assert index["loni-upload"]["repo_path"] == str(real)


def test_isbetterentry_shallower_path_wins_when_neither_has_origin():
    # Arrange
    shallow = build_entry_stub("/a/manifest.json")
    deep = build_entry_stub("/a/b/c/manifest.json")

    # Act & Assert
    assert is_better_entry(shallow, deep) is True
    assert is_better_entry(deep, shallow) is False


def build_entry_stub(manifest_path: str):
    """Builds a minimal GearEntry for comparison tests."""
    from build_gear_index import GearEntry

    return GearEntry(
        name="g",
        version=None,
        manifest_path=manifest_path,
        repo_path=None,
        remotes={},
        origin_forge=None,
        mirror_remotes=[],
        default_branch=None,
        is_dirty=None,
    )


def test_runbuild_writes_json_to_output_path(nested_gear: Path, tmp_path: Path):
    # Arrange
    output_path = tmp_path / "out" / "gear-index.json"

    # Act
    index = run_build(nested_gear, output_path, quiet=True)

    # Assert
    assert output_path.exists()
    assert json.loads(output_path.read_text()) == index
    assert "loni-upload" in index
