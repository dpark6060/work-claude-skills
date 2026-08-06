#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["flywheel-sdk"]
# ///
"""Create a dummy Flywheel project from a hierarchy spec JSON.

Spec format: see assets/hierarchy.example.json. Path depth sets the level
(1 segment = project file ... 4 = acquisition file; trailing "/" = empty
container). Files marked content="real" are not uploaded — they are reported
as pending uploads for a human to provide.
"""

import argparse
import io
import json
import sys
import typing as t
from dataclasses import asdict, dataclass, field
from pathlib import Path

import flywheel

from fwv_common import get_api_key, get_run_id, get_site_config

CONTAINER_LEVELS = ("subject", "session", "acquisition")
FAKE_DICOM_BYTES = b"FWV-FAKE-DICOM\x00"


@dataclass
class ItemSpec:
    """One resolved entry from the spec: container chain plus optional file."""

    containers: t.Tuple[str, ...]
    filename: t.Optional[str]
    meta: t.Dict[str, t.Any] = field(default_factory=dict)

    @property
    def path(self) -> str:
        """The original spec path for this item (no trailing slash)."""
        parts = list(self.containers) + ([self.filename] if self.filename else [])
        return "/".join(parts)


def parse_item(entry: str, metadata: dict) -> ItemSpec:
    """Resolve one items entry into a container chain and optional filename.

    Args:
        entry: A spec path like "sub-01/ses-01/acq-01/file.dcm" or "sub-02/".
        metadata: The spec's metadata dict, keyed by path.

    Returns:
        ItemSpec: the resolved item with any matching metadata attached.

    Raises:
        ValueError: the entry nests deeper than subject/session/acquisition.
    """
    is_container_only = entry.endswith("/")
    parts = [p for p in entry.split("/") if p]
    filename = None if is_container_only else parts.pop()
    if len(parts) > len(CONTAINER_LEVELS):
        raise ValueError(
            f"Entry {entry!r} nests deeper than subject/session/acquisition."
        )
    key = entry.rstrip("/")
    return ItemSpec(
        containers=tuple(parts), filename=filename, meta=metadata.get(key, {})
    )


def parse_spec(spec: dict, run_id: str) -> t.Tuple[str, t.List[ItemSpec]]:
    """Parse a raw spec dict into a project label and resolved items.

    Args:
        spec: The loaded hierarchy spec JSON.
        run_id: The run id substituted for "{run_id}" in the project label.

    Returns:
        Tuple of (project label, list of ItemSpec).
    """
    label = spec["project"].replace("{run_id}", run_id)
    metadata = spec.get("metadata", {})
    items = [parse_item(entry, metadata) for entry in spec.get("items", [])]
    return label, items


@dataclass
class Target:
    """A created container or file, addressable by its spec path."""

    kind: str  # "container" | "file" | "pending"
    container: t.Any
    filename: t.Optional[str] = None


def add_containers(
    project: t.Any,
    containers: t.Tuple[str, ...],
    registry: t.Dict[str, Target],
) -> t.Any:
    """Create (or reuse) the container chain and return the leaf container.

    Args:
        project: The Flywheel project container.
        containers: Labels ordered subject -> session -> acquisition.
        registry: Path -> Target map, updated with every container touched.

    Returns:
        t.Any: the deepest container in the chain (the project itself if empty).
    """
    parent = project
    path_parts: t.List[str] = []
    for level, label in zip(CONTAINER_LEVELS, containers):
        path_parts.append(label)
        finder = getattr(parent, f"{level}s")
        child = finder.find_first(f'label="{label}"')
        if child is None:
            child = getattr(parent, f"add_{level}")(label=label)
        registry["/".join(path_parts)] = Target(kind="container", container=child)
        parent = child
    return parent


def add_file(
    parent: t.Any,
    item: ItemSpec,
    pending: t.List[str],
    registry: t.Dict[str, Target],
) -> None:
    """Upload the item's file, or record it as a pending manual upload.

    A content="real" file is never uploaded by this script. If a human already
    put it on the container (a re-run), it is registered as a normal file so its
    metadata gets applied; otherwise it is recorded as pending.

    Args:
        parent: Container the file attaches to.
        item: The resolved spec item (filename must not be None).
        pending: Accumulator for paths awaiting manual upload.
        registry: Path -> Target map, updated with the file's target.
    """
    content = item.meta.get("content", "text")
    if content == "real":
        is_present = is_file_on_container(parent, item.filename)
        if not is_present:
            pending.append(item.path)
        registry[item.path] = Target(
            kind="file" if is_present else "pending",
            container=parent,
            filename=item.filename,
        )
        return
    data = get_file_contents(content, item.path)
    parent.upload_file(
        flywheel.FileSpec(item.filename, io.BytesIO(data), size=len(data))
    )
    registry[item.path] = Target(kind="file", container=parent, filename=item.filename)


def is_file_on_container(parent: t.Any, filename: str) -> bool:
    """Check whether the container already carries a file with this name.

    Args:
        parent: The container to look on.
        filename: File name to look for.

    Returns:
        bool: True if the file is present. Any SDK failure counts as absent —
            a lookup we cannot complete must not block the pending path.
    """
    try:
        return bool(parent.get_file(filename))
    except Exception:  # noqa: BLE001 - SDK raises assorted errors for "no such file"
        return False


def get_file_contents(content: str, path: str) -> bytes:
    """Build the placeholder bytes uploaded for a spec item.

    Args:
        content: The item's "content" metadata value.
        path: The item's spec path, embedded in text placeholders.

    Returns:
        bytes: fake DICOM bytes for "fake-dicom", else a text placeholder.
    """
    if content == "fake-dicom":
        return FAKE_DICOM_BYTES
    return f"fw-verify placeholder: {path}\n".encode()


def process_metadata(registry: t.Dict[str, Target], metadata: dict) -> None:
    """Apply spec metadata entries to their created containers/files.

    Pending (content="real") files are skipped: nothing is on the container yet,
    so there is nothing to tag. Re-run the script once the file is uploaded and
    it registers as a normal file target, which applies its metadata then.

    Args:
        registry: Path -> Target map built during creation.
        metadata: The spec's metadata dict.

    Raises:
        ValueError: a metadata key matches no created container or file.
    """
    for path, meta in metadata.items():
        target = registry.get(path.rstrip("/"))
        if target is None:
            raise ValueError(
                f"Metadata key {path!r} matches no created container or file."
            )
        if target.kind == "pending":
            continue
        if target.kind == "container":
            _apply_container_meta(target, meta)
            continue
        _apply_file_meta(target, meta)


def _apply_container_meta(target: Target, meta: dict) -> None:
    """Apply info metadata to a container."""
    if "info" in meta:
        target.container.update_info(meta["info"])


def _apply_file_meta(target: Target, meta: dict) -> None:
    """Apply info/classification/type metadata to a file via its parent."""
    if "info" in meta:
        target.container.update_file_info(target.filename, meta["info"])
    if "classification" in meta:
        target.container.update_file_classification(
            target.filename, meta["classification"]
        )
    if "type" in meta:
        target.container.update_file(target.filename, {"type": meta["type"]})


@dataclass
class BuildResult:
    """Outcome of a build: the created project and files awaiting manual upload."""

    project_id: str
    project_label: str
    run_id: str
    pending_uploads: t.List[str] = field(default_factory=list)


def get_or_add_project(fw: t.Any, group_id: str, label: str) -> t.Any:
    """Return the group's project with this label, creating it if absent.

    Args:
        fw: Flywheel client.
        group_id: Group the project lives under.
        label: Project label.

    Returns:
        t.Any: the existing or newly created project container.
    """
    existing = fw.projects.find_first(f'group._id={group_id},label="{label}"')
    if existing is not None:
        return existing
    group = fw.get_group(group_id)
    return group.add_project(label=label)


def orchestrate_build(fw: t.Any, group_id: str, spec: dict, run_id: str) -> BuildResult:
    """Build the full dummy project described by the spec.

    Args:
        fw: Flywheel client.
        group_id: Namespace group all artifacts live under.
        spec: The loaded hierarchy spec.
        run_id: Namespacing run id (must already carry the fwv- prefix).

    Returns:
        BuildResult: project identifiers and pending manual uploads.
    """
    label, items = parse_spec(spec, run_id)
    project = get_or_add_project(fw, group_id, label)
    registry: t.Dict[str, Target] = {}
    pending: t.List[str] = []
    for item in items:
        parent = add_containers(project, item.containers, registry)
        if item.filename is not None:
            add_file(parent, item, pending, registry)
    process_metadata(registry, spec.get("metadata", {}))
    return BuildResult(
        project_id=str(project.id),
        project_label=label,
        run_id=run_id,
        pending_uploads=pending,
    )


def get_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to hierarchy spec JSON")
    parser.add_argument("--run-id", default=None, help="Run id (generated if omitted)")
    parser.add_argument(
        "--site", default=None, help="Named site from config (default: default_site)"
    )
    return parser


SETUP_ERRORS = (KeyError, FileNotFoundError, RuntimeError, json.JSONDecodeError)


def get_error_message(exc: Exception) -> str:
    """Return an exception's message, unwrapping KeyError's repr quoting."""
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc)


def main(argv: t.Optional[t.List[str]] = None) -> int:
    """CLI entrypoint: build the project and print the result as JSON.

    Every setup mistake a user can make — missing config.json, unknown --site,
    unset API key env var, missing or malformed --spec — prints the underlying
    message and exits 1 rather than dumping a traceback.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        int: 0 on success, 1 if config, credentials, or the spec file are bad.
    """
    args = get_arg_parser().parse_args(argv)
    try:
        cfg = get_site_config(args.site)
        fw = flywheel.Client(get_api_key(cfg))
        spec = json.loads(Path(args.spec).read_text())
    except SETUP_ERRORS as exc:
        print(f"Setup error: {get_error_message(exc)}", file=sys.stderr)
        return 1
    run_id = args.run_id or get_run_id()
    result = orchestrate_build(fw, cfg.group, spec, run_id)
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
