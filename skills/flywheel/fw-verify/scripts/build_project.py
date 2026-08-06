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
import time
import typing as t
from dataclasses import asdict, dataclass, field
from pathlib import Path

import flywheel

from fwv_common import (
    SETUP_ERRORS,
    get_api_key,
    get_error_message,
    get_run_id,
    get_site_config,
)

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


def get_project_label(spec: dict, run_id: str) -> str:
    """Resolve the spec's project label without creating anything.

    Args:
        spec: The loaded hierarchy spec JSON.
        run_id: The run id substituted for "{run_id}".

    Returns:
        str: the resolved project label.

    Raises:
        KeyError: the spec has no "project" value.
    """
    return spec["project"].replace("{run_id}", run_id)


def parse_spec(spec: dict, run_id: str) -> t.Tuple[str, t.List[ItemSpec]]:
    """Parse a raw spec dict into a project label and resolved items.

    Args:
        spec: The loaded hierarchy spec JSON.
        run_id: The run id substituted for "{run_id}" in the project label.

    Returns:
        Tuple of (project label, list of ItemSpec).
    """
    label = get_project_label(spec, run_id)
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


FILE_ATTRS = ("type", "modality")
CLASSIFICATION_ATTEMPTS = 4
CLASSIFICATION_CONFIRMS = 2
CLASSIFICATION_WAIT_SECONDS = 6


def _apply_file_meta(target: Target, meta: dict) -> None:
    """Apply type/modality, then classification, then info to a file.

    The order is load-bearing. Classification keys are validated against the
    file's modality, and a file with no modality accepts only "Custom" — send
    "Intent" first and the API answers 422 "Unknown modalities can only use the
    custom attribute". The API also clears classification whenever modality
    changes, so classification has to land after both attributes are set.
    """
    attrs = {key: meta[key] for key in FILE_ATTRS if key in meta}
    if attrs:
        target.container.update_file(target.filename, attrs)
    if "classification" in meta:
        set_file_classification(target, meta["classification"])
    if "info" in meta:
        target.container.update_file_info(target.filename, meta["info"])


def set_file_classification(target: Target, classification: dict) -> bool:
    """Write a file's classification and confirm it survived the ingest gears.

    Uploading a file makes the site spawn its own gears — on a stock instance
    file-metadata-importer then file-classifier. file-classifier owns
    classification and replaces whatever is there when it finishes, so a write
    that lands while it is still queued is silently thrown away: the PATCH
    returns modified=1 and the value is gone seconds later. Write, re-read, and
    write again until it sticks.

    Args:
        target: The file target to classify.
        classification: Classification dict to apply.

    Returns:
        bool: True if the classification was observed on the file. False means
            every attempt was overwritten — the caller warns, because a fixture
            with silently missing metadata is worse than a slow build.
    """
    for _ in range(CLASSIFICATION_ATTEMPTS):
        target.container.update_file_classification(target.filename, classification)
        if is_classification_durable(target, classification):
            return True
    print(
        f"Warning: classification on {target.filename!r} keeps getting overwritten "
        f"by the site's ingest gears; it is not set.",
        file=sys.stderr,
    )
    return False


def is_classification_durable(target: Target, classification: dict) -> bool:
    """Confirm a classification write is still there once the gears have run.

    Reading straight back after the write proves nothing. Observed live on a
    22.3.9 site: the read-back confirmed, then file-classifier finished a few
    seconds later and replaced classification with what it derived — for a
    placeholder DICOM with no readable header, nothing at all. So wait before
    reading, and demand two agreeing reads a wait apart, which is the only
    thing that actually distinguishes "the write stuck" from "the gear has not
    clobbered it yet".

    Args:
        target: The file target to re-read.
        classification: The classification that was requested.

    Returns:
        bool: True if both delayed reads show the requested classification.
    """
    for _ in range(CLASSIFICATION_CONFIRMS):
        time.sleep(CLASSIFICATION_WAIT_SECONDS)
        if not is_classification_applied(target, classification):
            return False
    return True


def is_classification_applied(target: Target, classification: dict) -> bool:
    """Check whether every requested classification key is on the file now.

    Args:
        target: The file target to re-read from the server.
        classification: The classification that was requested.

    Returns:
        bool: True if a fresh read shows every requested key and value. The
            check is a subset test — the ingest gears add keys of their own and
            those are not a failure.
    """
    fresh = target.container.reload().get_file(target.filename)
    if fresh is None:
        return False
    current = dict(fresh.classification or {})
    return all(current.get(key) == value for key, value in classification.items())


@dataclass
class BuildResult:
    """Outcome of a build: the created project and files awaiting manual upload."""

    project_id: str
    project_label: str
    run_id: str
    pending_uploads: t.List[str] = field(default_factory=list)


def get_or_add_group(fw: t.Any, group_id: str) -> t.Any:
    """Return the namespace group, creating it if the site does not have it.

    The configured group is a namespace this skill owns, so a site that has
    never run fw-verify simply does not have it yet. Only a 404 is treated as
    "absent" — a 403 means the key cannot read groups, which is a real setup
    problem and must not be papered over by trying to create one.

    Args:
        fw: Flywheel client.
        group_id: Group id from the site config.

    Returns:
        t.Any: the existing or newly created group container.

    Raises:
        flywheel.ApiException: the lookup failed for any reason other than 404.
    """
    try:
        return fw.get_group(group_id)
    except flywheel.ApiException as exc:
        if exc.status != 404:
            raise
    fw.add_group(flywheel.GroupInput(id=group_id, label=group_id))
    return fw.get_group(group_id)


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
    group = get_or_add_group(fw, group_id)
    return group.add_project(label=label)


def delete_project_rules(fw: t.Any, project_id: str) -> t.List[str]:
    """Remove every gear rule on the project so no site gear touches the fixture.

    A new project inherits the site's default gear rules, so uploading a file
    queues the instance's own gears against it. file-classifier is the one that
    hurts: it owns file classification and REPLACES it when it finishes, and
    what it derives from a placeholder DICOM with no readable header is nothing
    at all. The build's classification write then vanishes seconds after it was
    confirmed. Strip the rules and the race does not exist.

    Runs on reused projects too — listing an already-stripped project returns an
    empty list and nothing is deleted, so it is safe to repeat.

    Args:
        fw: Flywheel client.
        project_id: Project to strip.

    Returns:
        list[str]: ids of the removed rules (empty if there were none).
    """
    rules = fw.get_project_rules(project_id)
    for rule in rules:
        fw.remove_project_rule(project_id, rule.id)
    return [str(rule.id) for rule in rules]


def validate_label_carries_run_id(label: str, run_id: str) -> None:
    """Refuse a project label that cleanup would never be able to find.

    cleanup.py deletes by substring-matching the run id against project labels,
    so a spec whose "project" omits "{run_id}" builds something no cleanup can
    ever reach — and worse, a fixed label makes every run adopt the same project
    and inherit the last run's containers. Fail before anything is created.

    Args:
        label: The resolved project label.
        run_id: The run id that must appear in it.

    Raises:
        ValueError: the label does not contain the run id.
    """
    if run_id in label:
        return
    raise ValueError(
        f"Project label {label!r} does not contain the run id {run_id!r}. Add "
        f'"{{run_id}}" to the spec\'s "project" value — cleanup matches on it, '
        f"so a label without it can never be deleted."
    )


def orchestrate_build(fw: t.Any, group_id: str, spec: dict, run_id: str) -> BuildResult:
    """Build the full dummy project described by the spec.

    Args:
        fw: Flywheel client.
        group_id: Namespace group all artifacts live under.
        spec: The loaded hierarchy spec.
        run_id: Namespacing run id (must already carry the fwv- prefix).

    The project's gear rules are stripped before anything is uploaded, so the
    site's own gears never run on the fixture and cannot rewrite its metadata.

    Returns:
        BuildResult: project identifiers and pending manual uploads.

    Raises:
        ValueError: the resolved project label does not contain the run id.
    """
    label, items = parse_spec(spec, run_id)
    validate_label_carries_run_id(label, run_id)
    project = get_or_add_project(fw, group_id, label)
    delete_project_rules(fw, str(project.id))
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


# The shared setup errors plus ValueError, which is how every semantic spec
# problem surfaces (path too deep, metadata key matching nothing, label missing
# the run id). SKILL.md promises a bad spec prints "Setup error:", so the build
# has to be inside the guard, not just the config loading. cleanup.py keeps the
# bare tuple on purpose — there, a ValueError is a refusal to delete and must
# stay loud.
BUILD_ERRORS = SETUP_ERRORS + (ValueError,)


def get_orphan_hint(run_id: str, label: t.Optional[str]) -> t.List[str]:
    """Build the stderr lines that point cleanup at a half-built project.

    Some spec errors only surface after the project exists — process_metadata
    raises on a key matching nothing, and by then containers and files are
    already on the instance. Printing just the message leaves an orphan whose
    run id the user has no way to recover, because a generated run id is never
    echoed on the failure path. So name both the run id and the resolved label.

    Args:
        run_id: This run's id.
        label: The resolved project label, or None if the failure happened
            before the spec could be read (nothing was created, so no hint).

    Returns:
        list[str]: stderr lines to print after the error, empty when there is
            nothing that could have been built.
    """
    if label is None:
        return []
    return [
        f"Run id: {run_id} | project label: {label}",
        f"Anything already created is an orphan. Clean it up with: "
        f"cleanup.py --run-id {run_id} --dry-run",
    ]


def main(argv: t.Optional[t.List[str]] = None) -> int:
    """CLI entrypoint: build the project and print the result as JSON.

    Every setup mistake a user can make — missing config.json, unknown --site,
    unset API key env var, missing or malformed --spec, or a spec whose contents
    are semantically wrong — prints the underlying message and exits 1 rather
    than dumping a traceback. The build itself is inside the guarded block for
    that last case: a too-deep path, a metadata key matching nothing, or a label
    without the run id are all the user's spec to fix, not bugs. Once the spec
    has been read the error also names the run id and project label, because a
    metadata failure fires after the project exists and a generated run id is
    otherwise never echoed — the user would be left with an unfindable orphan.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        int: 0 on success, 1 if config, credentials, or the spec are bad.
    """
    args = get_arg_parser().parse_args(argv)
    run_id = args.run_id or get_run_id()
    label = None
    try:
        cfg = get_site_config(args.site)
        fw = flywheel.Client(get_api_key(cfg))
        spec = json.loads(Path(args.spec).read_text())
        label = get_project_label(spec, run_id)
        result = orchestrate_build(fw, cfg.group, spec, run_id)
    except BUILD_ERRORS as exc:
        lines = [f"Setup error: {get_error_message(exc)}"]
        lines.extend(get_orphan_hint(run_id, label))
        print("\n".join(lines), file=sys.stderr)
        return 1
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
