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
from dataclasses import dataclass, field
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

    Args:
        parent: Container the file attaches to.
        item: The resolved spec item (filename must not be None).
        pending: Accumulator for paths awaiting manual upload.
        registry: Path -> Target map, updated with the file's target.
    """
    content = item.meta.get("content", "text")
    if content == "real":
        pending.append(item.path)
        registry[item.path] = Target(
            kind="pending", container=parent, filename=item.filename
        )
        return
    data = get_file_contents(content, item.path)
    parent.upload_file(
        flywheel.FileSpec(item.filename, io.BytesIO(data), size=len(data))
    )
    registry[item.path] = Target(kind="file", container=parent, filename=item.filename)


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

    Pending (content="real") files are skipped: nothing was uploaded yet, so
    their metadata is applied by a re-run after the file is provided.

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
