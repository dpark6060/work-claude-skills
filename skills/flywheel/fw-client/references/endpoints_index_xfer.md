# Flywheel Transfer API (/xfer/) — Endpoints Index

One line per endpoint. For full parameter details, read `endpoints/xfer_<tag>.md`.

| Method | Path | Tag | Summary |
|---|---|---|---|
| `POST` | `/xfer/blob-sessions` | Blobs | Create blob session to upload files into |
| `GET` | `/xfer/blob-sessions/{session_id}` | Blobs | Get blob session by id |
| `DELETE` | `/xfer/blob-sessions/{session_id}` | Blobs | Delete blob session and all related blob |
| `POST` | `/xfer/blob-sessions/{session_id}/finish` | Blobs | Mark blob session as complete |
| `GET` | `/xfer/blobs` | Blobs | List blobs |
| `POST` | `/xfer/blobs` | Blobs | Create blob entry for uploading a file to storage |
| `POST` | `/xfer/blobs/batch-delete` | Blobs | Delete a batch of blobs *(deprecated)* |
| `GET` | `/xfer/blobs/{blob_id}` | Blobs | Get blob |
| `DELETE` | `/xfer/blobs/{blob_id}` | Blobs | Delete blob |
| `POST` | `/xfer/blobs/{blob_id}/download` | Blobs | Generate pre-signed download URL for a blob in storage |
| `POST` | `/xfer/blobs/{blob_id}/finish` | Blobs | Finalize blob upload |
| `POST` | `/xfer/blobs/{blob_id}/upload` | Blobs | Generate pre-signed upload URL for a blob or blob part in storage |
| `GET` | `/xfer/conflicts` | Conflicts | List upload conflicts |
| `GET` | `/xfer/conflicts/report` | Conflicts | Get conflict report download URL |
| `GET` | `/xfer/conflicts/report/download` | Conflicts | Download conflicts report |
| `POST` | `/xfer/conflicts/resolve` | Conflicts | Resolve upload conflicts |
| `GET` | `/xfer/conflicts/resolve-methods` | Conflicts | Return applicable resolve methods for each conflict type |
| `GET` | `/xfer/connectors` | Connectors | List the registered connectors |
| `PUT` | `/xfer/connectors/self/info` | Connectors | Set connector info like version and fs-mounts |
| `GET` | `/xfer/connectors/{connector_id}` | Connectors | Retrieve a connector by id |
| `GET` | `/xfer/exports` | Exports | List exports |
| `POST` | `/xfer/exports` | Exports | Create a new export |
| `GET` | `/xfer/exports/{export_id}` | Exports | Retrieve an export |
| `POST` | `/xfer/exports/{export_id}/cancel` | Exports | Cancel an export |
| `GET` | `/xfer/exports/{export_id}/progress2` | Exports | Get export progress totals and items |
| `GET` | `/xfer/exports/{export_id}/progress2/jsonl` | Exports | Stream export progress totals and items in JSONL format |
| `GET` | `/xfer/exports/{export_id}/report` | Exports | Get report in either jsonl or csv format |
| `POST` | `/xfer/exports/{export_id}/rerun` | Exports | Re-run an export |
| `GET` | `/xfer/imports` | Imports | List imports |
| `POST` | `/xfer/imports` | Imports | Create a new import |
| `GET` | `/xfer/imports/{import_id}` | Imports | Retrieve an import |
| `POST` | `/xfer/imports/{import_id}/cancel` | Imports | Cancel an import |
| `GET` | `/xfer/imports/{import_id}/progress2` | Imports | Get import progress totals and items |
| `GET` | `/xfer/imports/{import_id}/progress2/jsonl` | Imports | Stream import progress totals and items in JSONL format |
| `GET` | `/xfer/imports/{import_id}/progress2/sse` | Imports | Stream import progress totals and items with Server-Sent Events |
| `GET` | `/xfer/imports/{import_id}/report` | Imports | Get report in either jsonl or csv format |
| `POST` | `/xfer/imports/{import_id}/rerun` | Imports | Re-run an import |
| `GET` | `/xfer/rule-sets` | Rule Sets | List the available rule sets |
| `POST` | `/xfer/rule-sets` | Rule Sets | Create a new rule set |
| `GET` | `/xfer/rule-sets/schema` | Rule Sets | Get JSON schemas for rule set spec validation |
| `GET` | `/xfer/rule-sets/{rule_set_id}` | Rule Sets | Get a rule set by ID |
| `PATCH` | `/xfer/rule-sets/{rule_set_id}` | Rule Sets | Partially update a rule set and create a new version marked as .latest |
| `POST` | `/xfer/rule-sets/{rule_set_id}/archive` | Rule Sets | Archive a rule set and all its versions |
| `POST` | `/xfer/rule-sets/{rule_set_id}/restore` | Rule Sets | Restore a archived rule set and all its versions |
| `GET` | `/xfer/schedules` | Schedules | List schedules |
| `GET` | `/xfer/schedules/{schedule_id}` | Schedules | Retrieve a schedule |
| `PATCH` | `/xfer/schedules/{schedule_id}` | Schedules | Update a schedule |
| `GET` | `/xfer/storage-lists/{operation_id}` | Storages | Retrieve a storage list operation |
| `GET` | `/xfer/storage-settings` | Storages | List the available storage settings |
| `GET` | `/xfer/storage-settings/{settings_id}` | Storages | Get storage settings |
| `PATCH` | `/xfer/storage-settings/{settings_id}` | Storages | Update storage settings |
| `GET` | `/xfer/storages` | Storages | List the available storages |
| `POST` | `/xfer/storages` | Storages | Create a new storage for import and/or export operations |
| `GET` | `/xfer/storages/{storage_id}` | Storages | Retrieve a storage |
| `PATCH` | `/xfer/storages/{storage_id}` | Storages | Update a storage |
| `DELETE` | `/xfer/storages/{storage_id}` | Storages | Delete a storage |
| `POST` | `/xfer/storages/{storage_id}/check` | Storages | Check storage access by executing an operation on target connector |
| `POST` | `/xfer/storages/{storage_id}/list` | Storages | List storage files by executing an operation on target connector |
| `POST` | `/xfer/upload` | Upload | Create upload ticket to upload a file |
| `POST` | `/xfer/upload/finish` | Upload | Finish an upload previously initiated by creating an upload ticket |
| `POST` | `/xfer/upload/lookup` | Upload | Lookup project to upload to |
