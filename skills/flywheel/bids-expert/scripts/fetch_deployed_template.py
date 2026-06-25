#!/usr/bin/env python3
"""Report the curation template + version that ACTUALLY ran on an instance.

The vendored references (`references/flywheel/templates/`, the code index) are
pinned to one bids-client version. Deployed gears often run an older one, where
rule ids and template structure differ. Before grounding a diagnosis against the
vendored files, use this to confirm what really ran:

  - the curate-bids gear version and the bids-client version baked into it
  - the `base_template` config (reproin / bids-v1)
  - whether a CUSTOM template was supplied as an input (and download it if so)

Read-only. Give it a curate-bids job id, or a project (it finds the latest run).

Usage:
    uv run --with flywheel-sdk --with fw-client python fetch_deployed_template.py \
        (--job <jobid> | --project <id>) --api-key-env BMGF_API [--out custom_template.json]
"""

import argparse
import os
import sys

import flywheel
from fw_client import FWClient


def latest_curate_job(fw_http: FWClient, project_id: str) -> str:
    """Return the most-recent curate-bids job id on a project, or ''."""
    jobs = fw_http.get("/api/jobs", params={
        "filter": f"gear_info.name=curate-bids,parents.project={project_id}",
        "sort": "created:desc", "limit": 1})
    rows = jobs if isinstance(jobs, list) else jobs.get("results", jobs)
    return rows[0].get("_id") if rows else ""


def parse_bids_client_version(gear_version: str) -> str:
    """curate-bids gear versions look like '<gearver>_<bidsclientver>'."""
    return gear_version.rsplit("_", 1)[-1] if "_" in gear_version else "(unknown)"


def report(fw: flywheel.Client, fw_http: FWClient, job_id: str, out: str) -> None:
    """Print the deployed template/version picture for one curate-bids job."""
    job = fw_http.get(f"/api/jobs/{job_id}")
    gi = job.get("gear_info", {})
    gear_ver = gi.get("version", "")
    print(f"job:          {job_id}  ({job.get('state')})")
    pid = (job.get("parents") or {}).get("project")
    if pid:
        try:
            proj = fw_http.get(f"/api/projects/{pid}")
            print(f"project:      {proj.get('label')}  ({pid})  group={proj.get('group')}")
        except Exception:  # noqa: BLE001
            print(f"project:      {pid}")
    print(f"gear:         {gi.get('name')} {gear_ver}")
    if gi.get("name") == "curate-bids":
        print(f"bids-client:  {parse_bids_client_version(gear_ver)}  <-- the templates/rules this run used")
    else:
        print(f"  note: gear is '{gi.get('name')}', not curate-bids — the version suffix is NOT bids-client.")
        print("  pass --project to find the project's actual curate-bids run, or a curate-bids --job id.")

    cfg = fw_http.get(f"/api/jobs/{job_id}/config.json")
    config = dict(cfg.get("config") or {})
    inputs = dict(cfg.get("inputs") or {})
    print(f"base_template: {config.get('base_template', '(default)')}")
    print(f"config:        {config}")

    if "template" not in inputs:
        print("\ncustom template input: NONE — the run used the built-in base template above.")
        print("Match it to the bids-client repo at the version above (rule ids differ across versions).")
        return

    tmpl = inputs["template"]
    loc = (tmpl.get("location") or {})
    hier = (tmpl.get("hierarchy") or {})
    name = loc.get("name", "")
    print(f"\ncustom template input: {name}  on {hier.get('type')} {hier.get('id')}")
    if not out:
        print("Pass --out to download it.")
        return
    try:
        container = fw.get(hier.get("id"))
        container.download_file(name, out)
        print(f"downloaded custom template -> {out}")
    except Exception as exc:  # noqa: BLE001
        print(f"could not download ({exc}); pull it manually from {hier.get('type')} {hier.get('id')}")


def main() -> None:
    """CLI: resolve a curate-bids job and report its template/version."""
    parser = argparse.ArgumentParser(description=__doc__)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--job", help="curate-bids job id")
    src.add_argument("--project", help="project id (uses its most-recent curate-bids run)")
    parser.add_argument("--api-key-env", default="FW_API_KEY")
    parser.add_argument("--out", help="download a custom template input here, if present")
    args = parser.parse_args()

    key = os.environ.get(args.api_key_env)
    if not key:
        sys.exit(f"env var {args.api_key_env} not set")
    fw = flywheel.Client(key)
    fw_http = FWClient(key)

    job_id = args.job or latest_curate_job(fw_http, args.project)
    if not job_id:
        sys.exit("no curate-bids job found")
    report(fw, fw_http, job_id, args.out)


if __name__ == "__main__":
    main()
