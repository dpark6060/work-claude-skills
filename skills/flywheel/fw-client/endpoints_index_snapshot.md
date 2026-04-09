# Flywheel Snapshot API (/snapshot/) — Endpoints Index

One line per endpoint. For full parameter details, read `endpoints/snapshot_<tag>.md`.

| Method | Path | Tag | Summary |
|---|---|---|---|
| `GET` | `/healthz` | untagged | Check Health |
| `GET` | `/snapshot/projects/{project_id}/snapshots` | untagged | List Snapshots |
| `POST` | `/snapshot/projects/{project_id}/snapshots` | untagged | Create Snapshot |
| `GET` | `/snapshot/projects/{project_id}/snapshots/{snapshot_id}` | untagged | Download Snapshot |
| `DELETE` | `/snapshot/projects/{project_id}/snapshots/{snapshot_id}` | untagged | Delete Snapshot |
| `POST` | `/snapshot/projects/{project_id}/snapshots/{snapshot_id}/access_log` | untagged | Write Access Log |
| `GET` | `/snapshot/projects/{project_id}/snapshots/{snapshot_id}/detail` | untagged | Get Snapshot Detail |
| `GET` | `/snapshot/projects/{project_id}/subjects/{snapshot_id}` | untagged | Download Subjects |
