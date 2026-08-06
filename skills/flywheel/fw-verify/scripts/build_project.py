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
