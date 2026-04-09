#!/usr/bin/env python3
"""
pipeline_poll.py — Poll a GitLab MR pipeline to a terminal state.

Usage:
    python3 pipeline_poll.py                  # auto-detect from current branch
    python3 pipeline_poll.py <MR_URL>         # explicit MR URL
    python3 pipeline_poll.py <pipeline_URL>   # explicit pipeline URL

Polls until the pipeline reaches a terminal state, then prints a structured
result block. The calling agent reads ACTION_NEEDED and acts accordingly.

Exit codes:
    0 — terminal state reached (read stdout for ACTION_NEEDED)
    1 — script error (bad args, glab failure, etc.) — read stderr
"""

import json
import re
import subprocess
import sys
import time
from typing import Optional

POLL_INTERVAL_SECS = 180
LOG_TAIL_LINES = 150

INFRA_FAILURE_REASONS = {
    "ci_quota_exceeded",
    "runner_system_failure",
    "stuck_or_timeout_failure",
    "scheduler_failure",
    "data_integrity_failure",
}

LINT_PATTERNS = [
    "pre-commit", "isort", "black", "ruff", "flake8", "autopep8",
    "prettier", "eslint", "Files were modified by this hook",
    "reformatted", "would reformat", "pyproject_export", "poetry export",
    "hash mismatch", "requirements.txt", "The lock file is not up to date",
    "Refusing to push consecutive flywheel-bot commit",
]

CONFLICT_PATTERNS = [
    "CONFLICT (content):", "Automatic merge failed", "cannot merge", "merge conflict",
]

TEST_PATTERNS = ["FAILED", "pytest", "AssertionError", "ERRORS"]

SEP = "=" * 72


# ---------------------------------------------------------------------------
# GitLab API helpers
# ---------------------------------------------------------------------------

def glab_api(path: str) -> any:
    """Run glab api <path> and return parsed JSON. Raises on failure."""
    result = subprocess.run(["glab", "api", path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"glab api {path!r} failed:\n{result.stderr.strip()}")
    return json.loads(result.stdout)


def encode_path(project_path: str) -> str:
    return project_path.replace("/", "%2F")


def get_mr_pipelines(project_path: str, mr_iid: int, limit: int = 5) -> list:
    return glab_api(
        f"projects/{encode_path(project_path)}/merge_requests/{mr_iid}/pipelines?per_page={limit}"
    )


def get_pipeline_jobs(project_path: str, pipeline_id: int) -> list:
    return glab_api(
        f"projects/{encode_path(project_path)}/pipelines/{pipeline_id}/jobs?per_page=100"
    )


def get_mr_details(project_path: str, mr_iid: int) -> dict:
    return glab_api(f"projects/{encode_path(project_path)}/merge_requests/{mr_iid}")


def get_job_log_tail(project_path: str, job_id: int) -> str:
    result = subprocess.run(
        ["glab", "api", f"projects/{encode_path(project_path)}/jobs/{job_id}/trace"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"[Failed to fetch log: {result.stderr.strip()}]"
    lines = result.stdout.splitlines()
    return "\n".join(lines[-LOG_TAIL_LINES:])


# ---------------------------------------------------------------------------
# Input resolution
# ---------------------------------------------------------------------------

def _fatal(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def get_current_branch() -> str:
    result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    branch = result.stdout.strip()
    if not branch or branch in ("main", "master", "dev"):
        _fatal(f"Current branch '{branch or '(detached)'}' is not a feature branch. Nothing to monitor.")
    return branch


def get_remote_project_path() -> str:
    result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
    remote = result.stdout.strip()
    for pattern in (r"git@gitlab\.com:(.+?)(?:\.git)?$", r"https://gitlab\.com/(.+?)(?:\.git)?$"):
        m = re.match(pattern, remote)
        if m:
            return m.group(1)
    _fatal(f"Cannot parse project path from remote: {remote!r}")


def find_mr_iid_for_branch(project_path: str, branch: str) -> int:
    result = subprocess.run(
        ["glab", "mr", "list", "--source-branch", branch, "-R", project_path, "-F", "json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        _fatal(f"glab mr list failed: {result.stderr.strip()}")
    open_mrs = [mr for mr in json.loads(result.stdout) if mr.get("state") == "opened"]
    if not open_mrs:
        _fatal(f"No open MR found for branch '{branch}' in {project_path}.")
    if len(open_mrs) > 1:
        lines = [f"  !{mr['iid']} — {mr['title']} — {mr['web_url']}" for mr in open_mrs]
        _fatal("Multiple open MRs found:\n" + "\n".join(lines) + "\nPass the MR URL directly.")
    return open_mrs[0]["iid"]


def resolve_input(arg: Optional[str]) -> tuple[str, int]:
    """Return (project_path, mr_iid) from CLI arg or auto-detection."""
    if not arg:
        branch = get_current_branch()
        project_path = get_remote_project_path()
        return project_path, find_mr_iid_for_branch(project_path, branch)

    if "/-/merge_requests/" in arg:
        m = re.match(r"https://gitlab\.com/(.+)/-/merge_requests/(\d+)", arg)
        if not m:
            _fatal(f"Cannot parse MR URL: {arg!r}")
        return m.group(1), int(m.group(2))

    if "/-/pipelines/" in arg:
        m = re.match(r"https://gitlab\.com/(.+)/-/pipelines/(\d+)", arg)
        if not m:
            _fatal(f"Cannot parse pipeline URL: {arg!r}")
        project_path = m.group(1)
        pipeline_id = int(m.group(2))
        pipeline = glab_api(f"projects/{encode_path(project_path)}/pipelines/{pipeline_id}")
        return project_path, find_mr_iid_for_branch(project_path, pipeline["ref"])

    _fatal(f"Unrecognized argument: {arg!r}. Expected an MR URL, pipeline URL, or nothing.")


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_failure(log: str, failure_reason: str) -> str:
    if failure_reason in INFRA_FAILURE_REASONS:
        return "infrastructure"
    log_lower = log.lower()
    if any(p.lower() in log_lower for p in CONFLICT_PATTERNS):
        return "conflict"
    if any(p.lower() in log_lower for p in LINT_PATTERNS):
        return "lint"
    if any(p in log for p in TEST_PATTERNS):
        return "test"
    return "unknown"


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def print_header(project_path: str, mr_iid: int, mr_url: str,
                 source_branch: str, pipeline_id: int, pipeline_url: str) -> None:
    print(SEP)
    print("PIPELINE POLL RESULT")
    print(SEP)
    print(f"PROJECT:       {project_path}")
    print(f"MR:            !{mr_iid}")
    print(f"MR_URL:        {mr_url}")
    print(f"SOURCE_BRANCH: {source_branch}")
    print(f"PIPELINE_ID:   {pipeline_id}")
    print(f"PIPELINE_URL:  {pipeline_url}")
    print()


def handle_success(project_path: str, mr_iid: int, mr_url: str, source_branch: str,
                   pipeline_id: int, pipeline_url: str, mr_details: dict) -> None:
    merge_status = mr_details.get("detailed_merge_status", "")
    has_conflicts = mr_details.get("has_conflicts", False)

    print_header(project_path, mr_iid, mr_url, source_branch, pipeline_id, pipeline_url)
    print(f"RESULT:          success")
    print(f"MR_MERGE_STATUS: {merge_status}")

    if merge_status == "mergeable":
        print(f"ACTION_NEEDED:   none")
        print("\nPipeline passed and MR is ready to merge.")
    elif merge_status == "conflict" or has_conflicts:
        print(f"ACTION_NEEDED:   resolve_conflicts")
        print("\nPipeline passed but MR has merge conflicts.")
    else:
        print(f"ACTION_NEEDED:   unknown")
        print(f"\nPipeline passed but MR is blocked: {merge_status!r}")
        print("No automatic fix available — surface to user.")

    print(SEP)


def handle_failure(project_path: str, mr_iid: int, mr_url: str, source_branch: str,
                   pipeline_id: int, pipeline_url: str) -> None:
    jobs = get_pipeline_jobs(project_path, pipeline_id)
    failed_jobs = [j for j in jobs if j.get("status") == "failed"]

    print_header(project_path, mr_iid, mr_url, source_branch, pipeline_id, pipeline_url)
    print(f"RESULT:        failed")

    if not failed_jobs:
        sha = jobs[0].get("pipeline", {}).get("sha", "") if jobs else ""
        print(f"ACTION_NEEDED: check_external_scanners")
        print(f"PIPELINE_SHA:  {sha}")
        print("\nAll CI jobs passed but pipeline is marked failed.")
        print("Check commit statuses API for external scanner failures (e.g. Wiz).")
        print(SEP)
        return

    for job in failed_jobs:
        job_id = job["id"]
        job_name = job["name"]
        stage = job.get("stage", "unknown")
        failure_reason = job.get("failure_reason") or "script_failure"

        print(f"FAILED_JOB:     {job_name} (id={job_id}, stage={stage})")
        print(f"JOB_URL:        {job.get('web_url', '')}")
        print(f"FAILURE_REASON: {failure_reason}")

        if failure_reason in INFRA_FAILURE_REASONS:
            print(f"CLASSIFICATION: infrastructure")
            print(f"ACTION_NEEDED:  report_to_user")
            print(f"\nInfrastructure failure: {failure_reason}. No fix available.")
            print(SEP)
            continue

        log = get_job_log_tail(project_path, job_id)
        classification = classify_failure(log, failure_reason)
        print(f"CLASSIFICATION: {classification}")

        action_map = {
            "lint": "lint_fix",
            "conflict": "resolve_conflicts",
            "test": "report_to_user",
            "unknown": "unknown",
        }
        print(f"ACTION_NEEDED:  {action_map[classification]}")

        print(f"\nLOG_EXCERPT (last {LOG_TAIL_LINES} lines of job {job_id}):")
        print("-" * 40)
        print(log)
        print("-" * 40)
        print(SEP)


# ---------------------------------------------------------------------------
# Main polling loop
# ---------------------------------------------------------------------------

def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    project_path, mr_iid = resolve_input(arg)

    print(f"Monitoring !{mr_iid} in {project_path} ...")

    while True:
        pipelines = get_mr_pipelines(project_path, mr_iid)
        if not pipelines:
            _fatal("No pipelines found for this MR.")

        latest = pipelines[0]
        pipeline_id = latest["id"]
        status = latest["status"]
        pipeline_url = latest.get(
            "web_url", f"https://gitlab.com/{project_path}/-/pipelines/{pipeline_id}"
        )

        mr_details = get_mr_details(project_path, mr_iid)
        mr_url = mr_details.get("web_url", "")
        source_branch = mr_details.get("source_branch", "")

        print(f"[{time.strftime('%H:%M:%S')}] Pipeline #{pipeline_id}: {status}")

        if status in ("running", "pending", "created"):
            print(f"  Sleeping {POLL_INTERVAL_SECS}s ...")
            time.sleep(POLL_INTERVAL_SECS)
            continue

        if status in ("canceled", "skipped"):
            print_header(project_path, mr_iid, mr_url, source_branch, pipeline_id, pipeline_url)
            print(f"RESULT:        {status}")
            print(f"ACTION_NEEDED: none")
            print(f"\nPipeline was {status}. No action taken.")
            print(SEP)
            sys.exit(0)

        if status == "success":
            handle_success(project_path, mr_iid, mr_url, source_branch,
                           pipeline_id, pipeline_url, mr_details)
            sys.exit(0)

        if status == "failed":
            # If a newer pipeline started (auto-fix triggered by CI), wait for it
            fresh = get_mr_pipelines(project_path, mr_iid, limit=3)
            if fresh[0]["id"] != pipeline_id and fresh[0]["status"] in ("running", "pending", "created"):
                print(f"  Auto-fix pipeline #{fresh[0]['id']} is running — waiting ...")
                time.sleep(POLL_INTERVAL_SECS)
                continue

            handle_failure(project_path, mr_iid, mr_url, source_branch, pipeline_id, pipeline_url)
            sys.exit(0)

        # Unrecognized status — pass through to agent
        print_header(project_path, mr_iid, mr_url, source_branch, pipeline_id, pipeline_url)
        print(f"RESULT:        {status}")
        print(f"ACTION_NEEDED: unknown")
        print(f"\nUnrecognized pipeline status: {status!r}. Passing through to agent.")
        print(SEP)
        sys.exit(0)


if __name__ == "__main__":
    main()
