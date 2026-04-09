# Clockify MCP Server — Setup

Exposes Clockify time-tracking as native Claude tools. The server embeds
Flywheel-specific workflow instructions so Claude knows how to resolve
Jira tickets to the right client/project/task.

## Requirements

- Python 3.10+
- `fastmcp` — `uv pip install fastmcp --python /path/to/python3.10`
- `fw_http_client` — in the same Python environment
- `ClockifySdk` repo cloned locally

## Register in ~/.claude/settings.json

```json
"mcpServers": {
  "clockify": {
    "command": "/path/to/python3.10",
    "args": ["/path/to/skills/clockify/server/clockify_mcp.py"],
    "env": {
      "CLOCKIFY_SDK_PATH": "/path/to/directory/containing/ClockifySdk"
    }
  }
}
```

`CLOCKIFY_API` must be set in your shell environment (e.g. `~/.zprofile`).
The MCP server inherits it from the parent process.

Restart Claude Code after editing settings.json.

## Tools

### Lookup

| Tool | Description |
|---|---|
| `get_clients(use_cache)` | All clients as `{name: id}`. Cached by default. |
| `refresh_client_cache()` | Force re-fetch clients and overwrite cache. |
| `get_projects(client_id)` | Projects, optionally filtered by client. |
| `get_tasks(project_id)` | Tasks for a project. |
| `get_tags()` | All tags in the workspace. |
| `get_current_user()` | Authenticated user profile. |
| `get_workspace_users()` | All users in the workspace. |

### Time entries

| Tool | Description |
|---|---|
| `log_time(desc, project_id, task_id, minutes, billable, tag_ids)` | Entry ending now, by duration. |
| `log_time_range(desc, project_id, task_id, start, end, billable, tag_ids)` | Entry with explicit start/end. |
| `get_time_entries(days_back, start, end, description, project_id)` | Query entries with flexible filters. |
| `update_time_entry(entry_id, ...)` | Modify an existing entry (partial updates). |
| `delete_time_entry(entry_id)` | Delete an entry by ID. |

## Design

The server handles API calls only. All workflow logic — Jira ticket lookup,
client/project/task resolution, user confirmation — lives in the embedded
`instructions` string and the skill reference files. This keeps the server
simple and the skill portable.

Write operations (`log_time`, `log_time_range`, `update_time_entry`,
`delete_time_entry`) include "IMPORTANT: Always confirm with the user" in
their docstrings. Claude will show a summary and wait for approval before
calling these tools.
