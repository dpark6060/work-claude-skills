"""Shared lookup helpers for the Clockify skill.

Loads the hierarchical Client > Project > Task cache (see refresh_cache.py)
and resolves human-phrased substring hints to Clockify IDs.

Importable module — no CLI entry point.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

SDK_PATH = "/Users/davidparker/Documents/Flywheel/Code/clockify"
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)

CACHE_DIR = Path(__file__).parent.parent / "cache"
WORKSPACE_CACHE_PATH = CACHE_DIR / "workspace.json"
CLIENTS_CACHE_PATH = CACHE_DIR / "clients.json"

STALE_DAYS = 30

REFRESH_HINT = "→ run scripts/refresh_cache.py if the cache is stale."


def paginate_all(cl: Any, endpoint: str, params: Optional[dict] = None) -> list[dict]:
    """Page through a list endpoint until the API returns fewer items than page-size.

    The SDK's high-level wrappers (`get_workplace_clients`,
    `get_current_workspace_projects`, `get_project_tasks`) return only the
    first page. For full-workspace scans, use this helper instead.

    Args:
        cl (Any): An initialized `Clockify` instance (workspace already set).
        endpoint (str): Workspace-relative endpoint, e.g.
            f"workspaces/{cl.workspaceId}/clients".
        params (Optional[dict]): Extra query params merged into each request.

    Returns:
        list[dict]: Concatenated results across all pages.
    """
    page_size = 200
    base = dict(params or {})
    base["page-size"] = page_size

    results: list[dict] = []
    page = 1
    while True:
        batch = cl.client.make_call("get", endpoint, params={**base, "page": page})
        if not isinstance(batch, list):
            return [batch] if batch else []
        results.extend(batch)
        if len(batch) < page_size:
            return results
        page += 1


def load_workspace() -> dict:
    """Read the hierarchical workspace cache from disk.

    Warns to stderr if the cache is older than STALE_DAYS days. Raises
    `FileNotFoundError` (with a refresh hint) if the cache does not exist.

    Returns:
        dict: Parsed `workspace.json` payload (top-level keys: `fetched_at`,
            `workspace_id`, `clients`).
    """
    if not WORKSPACE_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"Workspace cache not found at {WORKSPACE_CACHE_PATH}. "
            "Run scripts/refresh_cache.py to build it."
        )

    cache = json.loads(WORKSPACE_CACHE_PATH.read_text())
    fetched_at = cache.get("fetched_at")
    if fetched_at:
        try:
            fetched_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - fetched_dt
            if age > timedelta(days=STALE_DAYS):
                days = int(age.total_seconds() // 86400)
                print(
                    f"warning: workspace cache is {days} days old. {REFRESH_HINT}",
                    file=sys.stderr,
                )
        except ValueError:
            pass
    return cache


def load_clients() -> dict[str, str]:
    """Read the flat clients cache (used by the MCP server).

    Returns:
        dict[str, str]: `{client_name: client_id}`.
    """
    if not CLIENTS_CACHE_PATH.exists():
        raise FileNotFoundError(
            f"Clients cache not found at {CLIENTS_CACHE_PATH}. "
            "Run scripts/refresh_cache.py to build it."
        )
    return json.loads(CLIENTS_CACHE_PATH.read_text())


class LookupError(Exception):
    """Raised when a hint matches 0 or >1 candidates at any tree level."""


def _match(candidates: list[dict], hint: str) -> list[dict]:
    """Filter candidates by case-insensitive substring; prefer exact match on tie.

    Args:
        candidates (list[dict]): Nodes from the cache (each has a `name`).
        hint (str): Substring to search for.

    Returns:
        list[dict]: Filtered candidates. If multiple match and exactly one
            equals the hint (case-insensitive), that one is returned alone.
    """
    needle = hint.strip().lower()
    matches = [c for c in candidates if needle in c["name"].lower()]
    if len(matches) > 1:
        exact = [c for c in matches if c["name"].lower() == needle]
        if len(exact) == 1:
            return exact
    return matches


def _build_lookup_error(level: str, hint: str, candidates: list[dict], pool: list[dict]) -> "LookupError":
    """Build a LookupError describing why resolution failed at one tree level.

    Args:
        level (str): "client", "project", or "task".
        hint (str): The user-supplied hint that failed to resolve.
        candidates (list[dict]): What the hint matched (0 or >1 items).
        pool (list[dict]): The full pool that was searched, for context on
            no-match errors.

    Returns:
        LookupError: Configured exception with a candidate listing.
    """
    if not candidates:
        sample = ", ".join(sorted(p["name"] for p in pool)[:8])
        more = "" if len(pool) <= 8 else f" (+ {len(pool) - 8} more)"
        return LookupError(
            f"No {level} matches '{hint}'. Available: {sample}{more}. {REFRESH_HINT}"
        )
    listing = "\n  - " + "\n  - ".join(c["name"] for c in candidates)
    return LookupError(
        f"Ambiguous {level} hint '{hint}' matched {len(candidates)} entries:{listing}\n{REFRESH_HINT}"
    )


def resolve(
    client_hint: str,
    project_hint: Optional[str] = None,
    task_hint: Optional[str] = None,
    cache: Optional[dict] = None,
) -> dict:
    """Resolve client/project/task hints to cache nodes by walking the tree.

    Hints are case-insensitive substrings. At each level, if multiple
    candidates match the hint but exactly one is an exact (case-insensitive)
    name match, that one wins. Otherwise ambiguity raises `LookupError`.

    Args:
        client_hint (str): Substring of the client name. Required.
        project_hint (Optional[str]): Substring of the project name. If
            omitted, the returned `project` is None.
        task_hint (Optional[str]): Substring of the task name. If
            `project_hint` is omitted, the task search runs across all
            projects under the matched client.
        cache (Optional[dict]): Pre-loaded workspace cache. If omitted,
            `load_workspace()` is called.

    Returns:
        dict: `{"client": <node>, "project": <node>|None, "task": <node>|None}`.
            Each node carries `id` and `name` at minimum.

    Raises:
        LookupError: If any level matches 0 or >1 candidates.
    """
    cache = cache if cache is not None else load_workspace()
    clients = cache["clients"]

    client_matches = _match(clients, client_hint)
    if len(client_matches) != 1:
        raise _build_lookup_error("client", client_hint, client_matches, clients)
    client = client_matches[0]

    project = None
    task = None

    if project_hint is not None:
        projects = client.get("projects", [])
        project_matches = _match(projects, project_hint)
        if len(project_matches) != 1:
            raise _build_lookup_error(
                f"project under client '{client['name']}'",
                project_hint,
                project_matches,
                projects,
            )
        project = project_matches[0]

        if task_hint is not None:
            tasks = project.get("tasks", [])
            task_matches = _match(tasks, task_hint)
            if len(task_matches) != 1:
                raise _build_lookup_error(
                    f"task under project '{project['name']}'",
                    task_hint,
                    task_matches,
                    tasks,
                )
            task = task_matches[0]

    elif task_hint is not None:
        all_tasks_with_project = [
            {**t, "_project": p}
            for p in client.get("projects", [])
            for t in p.get("tasks", [])
        ]
        task_matches = _match(all_tasks_with_project, task_hint)
        if len(task_matches) != 1:
            raise _build_lookup_error(
                f"task across all projects under client '{client['name']}'",
                task_hint,
                task_matches,
                all_tasks_with_project,
            )
        chosen = task_matches[0]
        project = chosen.pop("_project")
        task = chosen

    return {"client": client, "project": project, "task": task}
