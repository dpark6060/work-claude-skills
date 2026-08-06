#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["flywheel-sdk"]
# ///
"""Delete every fw-verify artifact carrying a given run id.

Refuses to touch anything whose label/name does not contain the run id, and
refuses run ids that don't start with "fwv-". This is the ONLY deletion path
the fw-verify skill is allowed to use.
"""

import argparse
import json
import re
import sys
import typing as t

import flywheel

from fwv_common import (
    RUN_ID_PREFIX,
    SETUP_ERRORS,
    get_api_key,
    get_error_message,
    get_site_config,
)

RUN_ID_FORMAT = f"{RUN_ID_PREFIX}MMDD-xxxx"
RUN_ID_PATTERN = re.compile(rf"{re.escape(RUN_ID_PREFIX)}\d{{4}}-[0-9a-f]{{4}}")

# A site with audit-trail enabled rejects container deletes that carry no
# reason (400 "Need to have delete reason while audit-trail is enabled").
# Sites without it ignore the parameter, so it is always sent.
DELETE_REASON = flywheel.ContainerDeleteReason.TEST_DATA


def validate_run_id(run_id: str) -> None:
    """Reject anything that is not a whole, well-formed fw-verify run id.

    The prefix alone is not enough. A bare "fwv-" or a truncated "fwv-0806"
    is a substring of every run id in its namespace, so accepting one would
    turn a typo into a delete-everything sweep. Only the exact shape
    get_run_id() emits is allowed.

    Args:
        run_id: The run id to check.

    Raises:
        ValueError: run_id is not a complete fwv-MMDD-xxxx run id.
    """
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError(
            f"Refusing cleanup: {run_id!r} is not a complete run id. "
            f"Expected the {RUN_ID_PREFIX!r} format {RUN_ID_FORMAT!r} "
            f"(e.g. 'fwv-0806-a3f2')."
        )


def delete_projects(
    fw: t.Any, group_id: str, run_id: str, dry_run: bool
) -> t.List[str]:
    """Delete the namespace group's projects whose label contains the run id.

    Args:
        fw: Flywheel SDK client.
        group_id: Group holding the fw-verify projects.
        run_id: Run id that a project label must contain to be deleted.
        dry_run: List matches without deleting them.

    Returns:
        list[str]: labels of deleted (or would-delete, in dry-run) projects.
    """
    deleted = []
    for project in fw.projects.iter_find(f"group._id={group_id}"):
        if run_id not in project.label:
            continue
        deleted.append(project.label)
        if not dry_run:
            fw.delete_project(project.id, delete_reason=DELETE_REASON)
    return deleted


def delete_gears(fw: t.Any, run_id: str, dry_run: bool) -> t.List[str]:
    """Delete gears whose name contains the run id.

    Asks for all_versions because /gears returns only each gear's latest version
    by default, and a run that uploads a probe gear twice must not leave the
    older version behind for the next cleanup to miss.

    Uses the raw `get_all_gears` call and NOT `fw.gears.iter_find`. The generic
    Finder pages with `after_id`, `/gears` ignores it, and the endpoint then
    re-serves the same page forever: an iter_find sweep pulled 3000 gears of
    which 250 were unique and never terminated. `get_all_gears` returns the
    whole list (1081 versions on the test site) in one request.

    Args:
        fw: Flywheel SDK client.
        run_id: Run id that a gear name must contain to be deleted.
        dry_run: List matches without deleting them.

    Returns:
        list[str]: names of deleted (or would-delete, in dry-run) gears.
    """
    deleted = []
    for gear in fw.get_all_gears(all_versions=True):
        if run_id not in gear.gear.name:
            continue
        deleted.append(gear.gear.name)
        if not dry_run:
            fw.delete_gear(gear.id)
    return deleted


def get_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id", required=True, help="Run id (must start with fwv-)"
    )
    parser.add_argument(
        "--site", default=None, help="Named site from config (default: default_site)"
    )
    parser.add_argument("--dry-run", action="store_true", help="List, don't delete")
    return parser


def main(argv: t.Optional[t.List[str]] = None) -> int:
    """CLI entrypoint: delete run-id-scoped projects and gears, print summary.

    A bad run id raises ValueError — that is a refusal to delete, not a setup
    mistake, so it is loud on purpose. Config and credential problems print the
    underlying message and exit 1 rather than dumping a traceback.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:]).

    Returns:
        int: 0 on success, 1 if config or credentials are bad.

    Raises:
        ValueError: the run id is not a complete "fwv-MMDD-xxxx" run id. The
            prefix alone is not enough — a truncated id matches every run in its
            namespace, so the whole format is validated.
    """
    args = get_arg_parser().parse_args(argv)
    validate_run_id(args.run_id)
    try:
        cfg = get_site_config(args.site)
        fw = flywheel.Client(get_api_key(cfg))
    except SETUP_ERRORS as exc:
        print(f"Setup error: {get_error_message(exc)}", file=sys.stderr)
        return 1
    projects = delete_projects(fw, cfg.group, args.run_id, args.dry_run)
    gears = delete_gears(fw, args.run_id, args.dry_run)
    summary = {"projects": projects, "gears": gears, "dry_run": args.dry_run}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
