"""Clockify MCP server.

Exposes Clockify time-tracking as native Claude tools. Flywheel-specific
workflow logic (Jira → client → project → task resolution) is embedded in
the server instructions so Claude knows the resolution strategy.

Required environment variables:
    CLOCKIFY_API  Clockify API key (from Profile Settings)
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from fastmcp import FastMCP

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("clockify-mcp")

CLOCKIFY_API_URL = "https://api.clockify.me/api/v1"
CACHE_PATH = Path(__file__).parent.parent / "cache" / "clients.json"

# ---------------------------------------------------------------------------
# Server instructions — embedded workflow rules for Claude
# ---------------------------------------------------------------------------

INSTRUCTIONS = """\
You have access to a Clockify time-tracking MCP. Use these tools to log time,
look up projects/tasks/clients, and query time entries.

## Flywheel workflow — logging time from a Jira ticket

1. Fetch the Jira ticket (Atlassian MCP, cloudId: flywheelio.atlassian.net).
   Extract: customfield_10108 (Customer/s), parent (Epic key), labels (Hourly/Fixed).
2. Call get_clients() to load the client cache. Match the Customer/s value to a client
   name (exact first, then fuzzy keyword match). If missing, call refresh_client_cache().
3. Call get_projects(client_id=...) and pick the project matching the label:
   - "Hourly" label → "Solutions Hourly" (exact name, not year-suffixed variants)
   - "Fixed" label → "Solutions Fixed"
   - No label → default "Solutions Hourly", ask user if ambiguous.
4. Call get_tasks(project_id=...) and match by the parent Epic's GEAR-XXXX key.
   If no parent Epic, match by the ticket's own key. Match on the key, not the text.
5. Call log_time() with the resolved IDs. Set billable=True for customer work.
6. ALWAYS show the user a confirmation summary BEFORE calling log_time() and wait
   for approval.

## Logging time without a Jira ticket

When the user names a project and task directly:
1. Internal Flywheel work uses client "Flywheel". Call get_clients() to get the ID.
2. Call get_projects(client_id=...) and match by project name.
3. Call get_tasks(project_id=...) and match by task name substring.
4. Set billable=False for internal projects (SSE Admin, SSE, Internal Projects, etc.).
5. Confirm with user before posting.

## When to stop and ask the user
- Client not found after cache refresh
- Multiple ambiguous projects for the same type
- No task matching the Epic/ticket key
- Jira ticket has no Customer/s field
- Any API error on a write operation
"""

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------

mcp = FastMCP("clockify", instructions=INSTRUCTIONS)

# ---------------------------------------------------------------------------
# Module-level state — populated on first API call
# ---------------------------------------------------------------------------

_session: Optional[requests.Session] = None
_workspace_id: Optional[str] = None
_user_id: Optional[str] = None


def _init() -> None:
    """Initialize the HTTP session and resolve workspace/user IDs on first call."""
    global _session, _workspace_id, _user_id
    if _session is not None:
        return

    api_key = os.environ.get("CLOCKIFY_API")
    if not api_key:
        raise RuntimeError(
            "Clockify API key is not set. "
            "Call the 'authenticate' tool with your API key to configure it. "
            "(Find your key at clockify.me → Profile Settings → API)"
        )

    session = requests.Session()
    session.headers.update({
        "x-api-key": api_key,
        "content-type": "application/json",
    })

    r = session.get(f"{CLOCKIFY_API_URL}/user")
    r.raise_for_status()
    user = r.json()

    r = session.get(f"{CLOCKIFY_API_URL}/workspaces")
    r.raise_for_status()
    workspaces = r.json()
    flywheel = next((w for w in workspaces if w.get("name") == "Flywheel"), None)

    _session = session
    _user_id = user["id"]
    _workspace_id = flywheel["id"] if flywheel else user.get("defaultWorkspace")
    log.info("Clockify initialized, workspace: %s", _workspace_id)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _get(endpoint: str, params: Optional[dict] = None) -> any:
    _init()
    r = _session.get(f"{CLOCKIFY_API_URL}/{endpoint}", params=params or {})
    r.raise_for_status()
    return r.json()


def _post(endpoint: str, data: dict) -> any:
    _init()
    r = _session.post(f"{CLOCKIFY_API_URL}/{endpoint}", data=json.dumps(data))
    r.raise_for_status()
    return r.json()


def _put(endpoint: str, data: dict) -> any:
    _init()
    r = _session.put(f"{CLOCKIFY_API_URL}/{endpoint}", data=json.dumps(data))
    r.raise_for_status()
    return r.json()


def _delete(endpoint: str) -> None:
    _init()
    r = _session.delete(f"{CLOCKIFY_API_URL}/{endpoint}")
    r.raise_for_status()


def _paginate(endpoint: str, params: Optional[dict] = None) -> list:
    """Fetch all pages of a list endpoint."""
    params = dict(params or {})
    all_results = []
    page = 1
    while True:
        params["page"] = page
        params["page-size"] = 50
        batch = _get(endpoint, params)
        if not isinstance(batch, list):
            return [batch] if batch else []
        all_results.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return all_results


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _encode_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _decode_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ===========================================================================
# CLIENT TOOLS
# ===========================================================================


@mcp.tool()
def get_clients(use_cache: bool = True) -> str:
    """Return all Clockify clients as a JSON object mapping client name to ID.

    Use this as the first step when resolving a Jira customer to a Clockify
    client. The cache avoids a slow API call on every lookup.

    Args:
        use_cache: Read from local cache (default True). Set False to force
                   a live fetch. If the cache doesn't exist yet, a live fetch
                   is done automatically.

    Returns:
        JSON object: {"Client Name": "clockify_id", ...}
    """
    if use_cache and CACHE_PATH.exists():
        return CACHE_PATH.read_text()
    return _refresh_client_cache()


@mcp.tool()
def refresh_client_cache() -> str:
    """Force-fetch all clients from the Clockify API and overwrite the cache.

    Call this when:
    - A client name from Jira is not found in the cached list
    - A cached client ID returns empty results or errors from the API
    - You suspect the cache is stale

    Returns:
        JSON object: {"Client Name": "clockify_id", ...}
    """
    return _refresh_client_cache()


# ===========================================================================
# PROJECT / TASK / TAG TOOLS
# ===========================================================================


@mcp.tool()
def get_projects(client_id: str = "") -> str:
    """Return projects in the workspace, optionally filtered by client.

    Use after resolving a client ID to find the right project. For Flywheel
    Jira tickets, filter by client and look for "Solutions Hourly" or
    "Solutions Fixed" depending on the ticket's labels.

    If a client_id is provided and returns no results, the server automatically
    refreshes the client cache once and retries. This handles stale cached IDs
    without requiring manual intervention.

    Args:
        client_id: Clockify client ID to filter by. Empty string returns
                   all projects (slow — 276+ projects in the workspace).

    Returns:
        JSON list: [{"id", "name", "clientId", "clientName", "archived"}, ...]
    """
    _init()
    result = _fetch_projects(client_id)

    if client_id and not result:
        log.warning("No projects for client_id=%s — refreshing client cache and retrying", client_id)
        _refresh_client_cache()
        result = _fetch_projects(client_id)

    return json.dumps([
        {
            "id": p["id"],
            "name": p["name"],
            "clientId": p.get("clientId", ""),
            "clientName": p.get("clientName", ""),
            "archived": p.get("archived", False),
        }
        for p in result
    ])


@mcp.tool()
def get_tasks(project_id: str) -> str:
    """Return all tasks for a Clockify project.

    Use after identifying the project to find the right task. For Jira
    tickets, match on the GEAR-XXXX key in the task name — tasks follow
    the format "[GEAR-XXXX]: description".

    Args:
        project_id: Clockify project ID.

    Returns:
        JSON list: [{"id", "name", "status", "assigneeIds"}, ...]
        status is "ACTIVE" or "DONE".
    """
    _init()
    all_tasks = _paginate(f"workspaces/{_workspace_id}/projects/{project_id}/tasks")
    return json.dumps([
        {
            "id": t["id"],
            "name": t["name"],
            "status": t.get("status", ""),
            "assigneeIds": t.get("assigneeIds", []),
        }
        for t in all_tasks
    ])


@mcp.tool()
def get_tags() -> str:
    """Return all tags in the workspace.

    Tags can be applied to time entries for additional categorization.

    Returns:
        JSON list: [{"id", "name", "archived"}, ...]
    """
    _init()
    all_tags = _paginate(f"workspaces/{_workspace_id}/tags")
    return json.dumps([
        {
            "id": t["id"],
            "name": t["name"],
            "archived": t.get("archived", False),
        }
        for t in all_tags
    ])


# ===========================================================================
# USER TOOLS
# ===========================================================================


@mcp.tool()
def get_current_user() -> str:
    """Return the authenticated user's profile.

    Returns:
        JSON object with id, email, name, defaultWorkspace, activeWorkspace.
    """
    user = _get("user")
    return json.dumps({
        "id": user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "defaultWorkspace": user.get("defaultWorkspace"),
        "activeWorkspace": user.get("activeWorkspace"),
    })


@mcp.tool()
def get_workspace_users() -> str:
    """Return all users in the current workspace.

    Returns:
        JSON list: [{"id", "name", "email", "status"}, ...]
    """
    _init()
    all_users = _paginate(f"workspaces/{_workspace_id}/users")
    return json.dumps([
        {
            "id": u["id"],
            "name": u.get("name", ""),
            "email": u.get("email", ""),
            "status": u.get("status", ""),
        }
        for u in all_users
    ])


# ===========================================================================
# TIME ENTRY TOOLS
# ===========================================================================


@mcp.tool()
def log_time(
    description: str,
    project_id: str,
    task_id: str,
    minutes: int,
    billable: bool = True,
    tag_ids: str = "",
) -> str:
    """Log a time entry ending at the current time.

    The entry starts (now - minutes) and ends now. This is the primary tool
    for logging work after the fact.

    IMPORTANT: Always confirm with the user before calling this tool.

    Args:
        description: Entry description. For Jira work use
                     "GEAR-XXXXX: <ticket summary>".
        project_id:  Clockify project ID (from get_projects).
        task_id:     Clockify task ID (from get_tasks).
        minutes:     Duration in minutes.
        billable:    True for customer work, False for internal (default True).
        tag_ids:     Comma-separated tag IDs (optional). Empty string for none.

    Returns:
        Confirmation string with start/end times.
    """
    _init()
    end_dt = _utc_now()
    start_dt = end_dt - timedelta(minutes=minutes)

    entry = _build_entry(description, project_id, task_id, start_dt, end_dt, billable, tag_ids)
    _post(f"workspaces/{_workspace_id}/time-entries", entry)

    return (
        f"Logged {minutes}min | '{description}' | "
        f"{_encode_dt(start_dt)} -> {_encode_dt(end_dt)} | billable={billable}"
    )


@mcp.tool()
def log_time_range(
    description: str,
    project_id: str,
    task_id: str,
    start: str,
    end: str,
    billable: bool = True,
    tag_ids: str = "",
) -> str:
    """Log a time entry with explicit start and end times.

    Use this instead of log_time when the user specifies exact times rather
    than a duration.

    IMPORTANT: Always confirm with the user before calling this tool.

    Args:
        description: Entry description.
        project_id:  Clockify project ID.
        task_id:     Clockify task ID.
        start:       Start time as ISO 8601 UTC string (YYYY-MM-DDTHH:MM:SSZ).
        end:         End time as ISO 8601 UTC string (YYYY-MM-DDTHH:MM:SSZ).
        billable:    True for customer work, False for internal (default True).
        tag_ids:     Comma-separated tag IDs (optional). Empty string for none.

    Returns:
        Confirmation string with start/end times and duration.
    """
    _init()
    start_dt = _decode_dt(start)
    end_dt = _decode_dt(end)

    if end_dt <= start_dt:
        return "Error: end time must be after start time."

    entry = _build_entry(description, project_id, task_id, start_dt, end_dt, billable, tag_ids)
    _post(f"workspaces/{_workspace_id}/time-entries", entry)

    duration_min = int((end_dt - start_dt).total_seconds() / 60)
    return (
        f"Logged {duration_min}min | '{description}' | {start} -> {end} | billable={billable}"
    )


@mcp.tool()
def get_time_entries(
    days_back: int = 7,
    start: str = "",
    end: str = "",
    description: str = "",
    project_id: str = "",
) -> str:
    """Query time entries for the current user.

    By default returns the last 7 days. Use start/end for custom ranges.
    All filters are optional and combinable.

    Args:
        days_back:   How many days back to fetch (default 7). Ignored if
                     start is provided.
        start:       ISO 8601 UTC string. Overrides days_back.
        end:         ISO 8601 UTC string. If omitted, defaults to now.
        description: Filter entries containing this substring.
        project_id:  Filter by project ID.

    Returns:
        JSON list: [{"id", "description", "projectId", "taskId", "duration",
                     "start", "end", "billable"}, ...]
    """
    _init()
    params: dict = {}

    if start:
        params["start"] = start
    else:
        params["start"] = _encode_dt(_utc_now() - timedelta(days=days_back))

    if end:
        params["end"] = end
    if description:
        params["description"] = description
    if project_id:
        params["project"] = project_id

    entries = _paginate(
        f"workspaces/{_workspace_id}/user/{_user_id}/time-entries",
        params,
    )
    return json.dumps([
        {
            "id": e.get("id"),
            "description": e.get("description"),
            "projectId": e.get("projectId"),
            "taskId": e.get("taskId"),
            "duration": _entry_duration(e),
            "start": e.get("timeInterval", {}).get("start"),
            "end": e.get("timeInterval", {}).get("end"),
            "billable": e.get("billable"),
        }
        for e in entries
    ])


@mcp.tool()
def update_time_entry(
    entry_id: str,
    description: str = "",
    project_id: str = "",
    task_id: str = "",
    start: str = "",
    end: str = "",
    billable: str = "",
    tag_ids: str = "",
) -> str:
    """Update an existing time entry.

    Only the fields you provide will be changed. Pass empty strings to leave
    fields unchanged. Use get_time_entries() first to find the entry ID.

    IMPORTANT: Always confirm with the user before calling this tool.

    Args:
        entry_id:    Clockify time entry ID to update.
        description: New description (empty = keep current).
        project_id:  New project ID (empty = keep current).
        task_id:     New task ID (empty = keep current).
        start:       New start ISO 8601 UTC (empty = keep current).
        end:         New end ISO 8601 UTC (empty = keep current).
        billable:    "true"/"false" (empty = keep current).
        tag_ids:     Comma-separated tag IDs (empty = keep current).

    Returns:
        Confirmation string or error message.
    """
    _init()
    existing = _get(f"workspaces/{_workspace_id}/time-entries/{entry_id}")
    if not existing:
        return f"Error: Time entry {entry_id} not found."

    update = {
        "description": description or existing.get("description", ""),
        "projectId": project_id or existing.get("projectId", ""),
        "taskId": task_id or existing.get("taskId", ""),
        "start": start or existing.get("timeInterval", {}).get("start", ""),
        "end": end or existing.get("timeInterval", {}).get("end", ""),
        "billable": existing.get("billable", False),
        "tagIds": existing.get("tagIds", []),
    }

    if billable:
        update["billable"] = billable.lower() == "true"
    if tag_ids:
        update["tagIds"] = [t.strip() for t in tag_ids.split(",")]

    _put(f"workspaces/{_workspace_id}/time-entries/{entry_id}", update)
    return f"Updated entry {entry_id}: '{update['description']}'"


@mcp.tool()
def delete_time_entry(entry_id: str) -> str:
    """Delete a time entry by ID.

    Use get_time_entries() first to find the entry. This is irreversible.

    IMPORTANT: Always confirm with the user before calling this tool.

    Args:
        entry_id: Clockify time entry ID to delete.

    Returns:
        Confirmation string or error message.
    """
    _init()
    _delete(f"workspaces/{_workspace_id}/time-entries/{entry_id}")
    return f"Deleted time entry {entry_id}."


# ===========================================================================
# INTERNAL HELPERS
# ===========================================================================


def _fetch_projects(client_id: str = "") -> list:
    """Fetch all projects, optionally filtered by client ID."""
    _init()
    params = {"clients": client_id} if client_id else {}
    all_projects = []
    page = 1
    while True:
        batch = _get(
            f"workspaces/{_workspace_id}/projects",
            {"page": page, "page-size": 50, **params},
        )
        all_projects.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return all_projects


def _refresh_client_cache() -> str:
    """Fetch all clients from API and write to cache file."""
    _init()
    all_clients = _paginate(f"workspaces/{_workspace_id}/clients")
    cache = {
        c["name"]: c["id"]
        for c in sorted(all_clients, key=lambda c: c["name"].lower())
    }
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))
    log.info("Client cache refreshed: %d clients", len(cache))
    return json.dumps(cache)


def _build_entry(
    description: str,
    project_id: str,
    task_id: str,
    start_dt: datetime,
    end_dt: datetime,
    billable: bool,
    tag_ids: str,
) -> dict:
    """Build a time entry dict for the Clockify API."""
    entry: dict = {
        "description": description,
        "projectId": project_id,
        "taskId": task_id,
        "start": _encode_dt(start_dt),
        "end": _encode_dt(end_dt),
        "billable": billable,
    }
    if tag_ids:
        entry["tagIds"] = [t.strip() for t in tag_ids.split(",")]
    return entry


def _entry_duration(entry: dict) -> str:
    """Compute HH:MM:SS duration string from a raw time entry dict."""
    interval = entry.get("timeInterval", {})
    start_str = interval.get("start")
    end_str = interval.get("end")
    if not start_str or not end_str:
        return ""
    return str(_decode_dt(end_str) - _decode_dt(start_str))


# ===========================================================================
# AUTHENTICATION
# ===========================================================================

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


@mcp.tool()
def authenticate(api_key: str) -> str:
    """Set the Clockify API key for this MCP server.

    Validates the key against the Clockify API, then saves it to
    ~/.claude/settings.json so it persists across Claude Code restarts.
    The key is also applied immediately to the current session.

    Find your API key at: clockify.me → Profile Settings → API

    Args:
        api_key: Your Clockify API key.

    Returns:
        Success message with your workspace and user name, or an error.
    """
    global _session, _workspace_id, _user_id

    # Validate the key before saving anything
    test_session = requests.Session()
    test_session.headers.update({
        "x-api-key": api_key,
        "content-type": "application/json",
    })
    r = test_session.get(f"{CLOCKIFY_API_URL}/user")
    if r.status_code == 401:
        return "Invalid API key — check clockify.me → Profile Settings → API."
    r.raise_for_status()
    user = r.json()

    # Apply to current process immediately
    os.environ["CLOCKIFY_API"] = api_key
    _session = None  # force _init() to re-run with the new key

    # Persist to ~/.claude/settings.json
    _write_api_key_to_settings(api_key)

    return (
        f"Authenticated as {user.get('name')} ({user.get('email')}). "
        f"API key saved to settings.json — will auto-load in future sessions."
    )


def _write_api_key_to_settings(api_key: str) -> None:
    """Write the Clockify API key into the MCP server env block in settings.json."""
    settings: dict = {}
    if SETTINGS_PATH.exists():
        settings = json.loads(SETTINGS_PATH.read_text())

    mcp_servers = settings.setdefault("mcpServers", {})
    clockify = mcp_servers.setdefault("clockify", {})
    env = clockify.setdefault("env", {})
    env["CLOCKIFY_API"] = api_key

    SETTINGS_PATH.write_text(json.dumps(settings, indent=2))


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    mcp.run()
