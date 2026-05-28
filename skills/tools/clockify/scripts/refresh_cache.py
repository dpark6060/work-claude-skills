"""Rebuild the hierarchical Client > Project > Task cache.

Writes two files under skills/tools/clockify/cache/:
  - workspace.json — nested {clients: [{projects: [{tasks: [...]}]}, ...]}
  - clients.json   — flat {name: id} (consumed by the MCP server)

Usage:
    python3 refresh_cache.py [--include-archived] [--clients-only] [--projects-only]

Expect ~1–3 minutes — one pagination per workspace for clients/projects,
then one API call per project for its tasks.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
sys.path.insert(0, SDK_PATH)

SCRIPTS_PATH = str(Path(__file__).parent)
sys.path.insert(0, SCRIPTS_PATH)

from ClockifySdk.clockify_sdk import Clockify

from lookup import (
    CACHE_DIR,
    CLIENTS_CACHE_PATH,
    WORKSPACE_CACHE_PATH,
    paginate_all,
)

UNCLIENTED_KEY = "(no client)"


def get_all_clients(cl: Clockify) -> list[dict]:
    """Fetch every client in the current workspace.

    Args:
        cl (Clockify): Initialized SDK instance with workspace set.

    Returns:
        list[dict]: Raw client dicts (id, name, archived, ...).
    """
    return paginate_all(cl, f"workspaces/{cl.workspaceId}/clients")


def get_all_projects(cl: Clockify, include_archived: bool) -> list[dict]:
    """Fetch every project in the current workspace.

    Args:
        cl (Clockify): Initialized SDK instance with workspace set.
        include_archived (bool): When False, only active projects are returned.

    Returns:
        list[dict]: Raw project dicts (id, name, clientId, clientName,
            archived, billable, ...).
    """
    params = {} if include_archived else {"archived": "false"}
    return paginate_all(cl, f"workspaces/{cl.workspaceId}/projects", params)


def get_project_tasks(cl: Clockify, project_id: str) -> list[dict]:
    """Fetch every task for a single project.

    Args:
        cl (Clockify): Initialized SDK instance with workspace set.
        project_id (str): Clockify project ID.

    Returns:
        list[dict]: Raw task dicts (id, name, status, ...).
    """
    return paginate_all(
        cl,
        f"workspaces/{cl.workspaceId}/projects/{project_id}/tasks",
    )


def build_workspace_tree(
    cl: Clockify,
    clients: list[dict],
    projects: list[dict],
) -> list[dict]:
    """Group projects under their clients and attach each project's tasks.

    Args:
        cl (Clockify): Initialized SDK instance (used to fetch tasks).
        clients (list[dict]): Raw clients from the API.
        projects (list[dict]): Raw projects from the API.

    Returns:
        list[dict]: Sorted clients tree. Each client has a `projects` list;
            each project has a `tasks` list. Projects with no client are
            grouped under a synthetic "(no client)" entry with id="".
    """
    by_client: dict[str, list[dict]] = {}
    for p in projects:
        by_client.setdefault(p.get("clientId", "") or "", []).append(p)

    tree: list[dict] = []
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())

    project_count = sum(len(v) for v in by_client.values())
    seen = 0

    for c in sorted_clients:
        client_projects = by_client.pop(c["id"], [])
        tree.append(_build_client_node(cl, c, client_projects, project_count, seen))
        seen += len(client_projects)

    orphans = by_client.get("", [])
    if orphans:
        synthetic = {"id": "", "name": UNCLIENTED_KEY, "archived": False}
        tree.append(_build_client_node(cl, synthetic, orphans, project_count, seen))

    return tree


def _build_client_node(
    cl: Clockify,
    client: dict,
    client_projects: list[dict],
    total: int,
    seen: int,
) -> dict:
    """Assemble one client entry with its projects and each project's tasks.

    Args:
        cl (Clockify): Initialized SDK instance.
        client (dict): Raw client dict.
        client_projects (list[dict]): Projects belonging to this client.
        total (int): Total project count across all clients (for progress).
        seen (int): Projects processed so far (for progress).

    Returns:
        dict: Client node with `id`, `name`, `archived`, `projects`.
    """
    sorted_projects = sorted(client_projects, key=lambda p: p["name"].lower())
    project_nodes = []
    for i, p in enumerate(sorted_projects, start=1):
        print(
            f"  [{seen + i}/{total}] {client['name']} → {p['name']}",
            file=sys.stderr,
        )
        tasks = get_project_tasks(cl, p["id"])
        project_nodes.append({
            "id": p["id"],
            "name": p["name"],
            "archived": p.get("archived", False),
            "billable": p.get("billable", True),
            "tasks": [
                {"id": t["id"], "name": t["name"], "status": t.get("status", "ACTIVE")}
                for t in tasks
            ],
        })
    return {
        "id": client["id"],
        "name": client["name"],
        "archived": client.get("archived", False),
        "projects": project_nodes,
    }


def write_clients_cache(clients: list[dict]) -> None:
    """Write the flat {name: id} cache consumed by the MCP server.

    Args:
        clients (list[dict]): Raw client dicts from the API.
    """
    flat = {
        c["name"]: c["id"]
        for c in sorted(clients, key=lambda c: c["name"].lower())
    }
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CLIENTS_CACHE_PATH.write_text(json.dumps(flat, indent=2))
    print(f"wrote {CLIENTS_CACHE_PATH} ({len(flat)} clients)", file=sys.stderr)


def write_workspace_cache(workspace_id: str, tree: list[dict]) -> None:
    """Write the hierarchical workspace cache.

    Args:
        workspace_id (str): Clockify workspace ID.
        tree (list[dict]): Output of build_workspace_tree.
    """
    payload = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace_id": workspace_id,
        "clients": tree,
    }
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_CACHE_PATH.write_text(json.dumps(payload, indent=2))
    total_projects = sum(len(c["projects"]) for c in tree)
    total_tasks = sum(len(p["tasks"]) for c in tree for p in c["projects"])
    print(
        f"wrote {WORKSPACE_CACHE_PATH} "
        f"({len(tree)} clients, {total_projects} projects, {total_tasks} tasks)",
        file=sys.stderr,
    )


def run_refresh(include_archived: bool, clients_only: bool, projects_only: bool) -> None:
    """Top-level orchestration: fetch from API and write cache files.

    Args:
        include_archived (bool): Include archived projects in workspace.json.
        clients_only (bool): Skip projects/tasks; only refresh clients.json.
        projects_only (bool): Skip the clients.json write; only refresh
            workspace.json.
    """
    cl = Clockify(api_key=os.environ["CLOCKIFY_API"])
    cl.get_flywheel_workspace()

    print("fetching clients...", file=sys.stderr)
    clients = get_all_clients(cl)
    print(f"  {len(clients)} clients", file=sys.stderr)

    if not projects_only:
        write_clients_cache(clients)

    if clients_only:
        return

    print("fetching projects...", file=sys.stderr)
    projects = get_all_projects(cl, include_archived)
    print(f"  {len(projects)} projects", file=sys.stderr)

    print("fetching tasks (one call per project)...", file=sys.stderr)
    tree = build_workspace_tree(cl, clients, projects)
    write_workspace_cache(cl.workspaceId, tree)


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include archived projects in the workspace tree.",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--clients-only",
        action="store_true",
        help="Only refresh clients.json; skip the project/task tree.",
    )
    scope.add_argument(
        "--projects-only",
        action="store_true",
        help="Only refresh workspace.json; skip the flat clients.json.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_refresh(args.include_archived, args.clients_only, args.projects_only)
