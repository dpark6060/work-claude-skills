---
type: CLI Reference
title: Admin Storage Commands
description: flyw admin storage commands for registering, listing, and managing external cloud storages used by imports and exports (site admin only).
tags: [flyw, cli, storage, admin]
timestamp: 2026-07-15T00:00:00Z
---

# Admin Storage Commands

Manage external cloud storages registered for imports and exports. Requires site admin role.

## `admin storage create` — Register a Storage

```bash
# Amazon S3
flyw admin storage create \
    --url "s3://bucket/prefix?access_key_id=...&secret_access_key=..."

# Google Cloud Storage
flyw admin storage create \
    --url "gs://bucket/prefix?application_credentials=/path/to/service_account.json"

# Azure Blob Storage
flyw admin storage create \
    --url "az://account/container/prefix?access_key=..."

# With label and project binding
flyw admin storage create \
    --url "s3://bucket" \
    --label "Research Data" \
    -p fw://group/project

# From existing core-api provider (for ref-in-place)
flyw admin storage create --provider <PROVIDER_ID>
```

### Options

| Option | Description |
|---|---|
| `-u, --url URL` | Storage connection URL |
| `--provider PRVD` | Create from existing core-api storage provider |
| `--label TXT` | Human-readable label |
| `-g, --group GRP` | Bind to group (permissions) |
| `-p, --project PRJ` | Bind to project (permissions) |
| `--connector ID` | Attach to specific connector |
| `-m, --mode M` | Restrict to `import` or `export` only |
| `--scan / --no-scan` | Enable malware scanning on import |
| `--wait / --no-wait` | Wait for status check |

### Storage URI Formats

| Provider | Format | Credential Params |
|---|---|---|
| **Amazon S3** | `s3://bucket[/prefix]` | `access_key_id`, `secret_access_key` |
| **Google Cloud** | `gs://bucket[/prefix]` | `application_credentials` (path to JSON) |
| **Azure Blob** | `az://account/container[/prefix]` | `access_key` |
| | | OR `tenant_id`, `client_id`, `client_secret` |
| **AWS HealthImaging** | `ahi://datastore_id` | `access_key_id`, `secret_access_key` |

The Azure `account` may be either the bare account name or the full
`<account>.blob.core.windows.net` host; existing registrations show the FQDN form.

### Credential Sources

Credentials can be provided via URL query params or environment variables:

| Provider | Environment Variables |
|---|---|
| AWS | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| GCS | `GOOGLE_APPLICATION_CREDENTIALS` (may be filepath) |
| Azure | `AZURE_ACCESS_KEY` |

### Service/Workload Credentials

Role-based credentials (Azure Workload Identity on AKS, IAM Roles for Service Accounts on EKS) don't require explicit keys. Use `?connector_creds=true` in the URL. Contact support@flywheel.io for setup.

## `admin storage get` — Get Storage Details

```bash
flyw admin storage get <STORAGE_ID>
flyw admin storage get <STORAGE_ID> -o json
```

## `admin storage list` — List Storages

```bash
flyw admin storage list
flyw admin storage list --filter status_check=success
flyw admin storage list --sort created:desc
flyw admin storage list -o json
```

### Options

| Option | Description |
|---|---|
| `--filter EXPR` | Filter expression |
| `--sort FIELD` | Sort by `field[:order]` |
| `--after-id ID` | Pagination token |
| `--limit INT` | Page limit |
| `-o, --output OUTPUT` | Output format |

## `admin storage update` — Update a Storage

```bash
flyw admin storage update <STORAGE_ID> --label "New Label"
flyw admin storage update <STORAGE_ID> --config access_key=newkey
flyw admin storage update <STORAGE_ID> --mode import --scan
```

### Options

| Option | Description |
|---|---|
| `STORAGE` | Storage ID [required] |
| `--label TXT` | Update label |
| `--config KEY=VAL` | Update config options |
| `-m, --mode M` | Set mode (import/export only) |
| `--scan / --no-scan` | Toggle malware scanning |
| `--wait / --no-wait` | Wait for status check |

## `admin storage delete` — Delete a Storage

```bash
flyw admin storage delete <STORAGE_ID>
```

## Referencing Files In Place

For large datasets, reference files in place to avoid transferring and duplicating data:

1. Create a **read-only storage provider** in Core-API:
```bash
curl -XPOST https://<DOMAIN>/api/site/providers \
    -H "Content-Type: application/json" \
    -H "Authorization: <API_KEY>" \
    -d '{
        "label": "ref-in-place",
        "provider_class": "storage",
        "provider_type": "aws",
        "creds": {"aws_access_key_id": "<ID>", "aws_secret_access_key": "<KEY>"},
        "config": {"region": "<REGION>", "bucket": "<BUCKET>"},
        "access_type": "read-only"
    }'
```

2. Create storage from that provider:
```bash
flyw admin storage create --provider <PROVIDER_ID>
```

3. Import with this storage — files are referenced, not copied.

## Finding a Storage in the Web App

Site Admin only. `External Storages` is not visible to non-admins at all.

1. Left menu, **ADMIN** section → **Interfaces** → **External Storages** tab.
2. Click a storage to open its detail page. The **Connection** card holds the **Storage ID** —
   the value `-s/--storage` wants.
3. **+ New Storage Provider** to register one: Storage Name → provider tile → **Provider
   Details** (Azure Account / Azure Container / Azure Prefix) → **Data Access Control**
   (**Allow Importing** / **Allow Exporting**, at least one required; optional Malware
   Scanning) → **Authentication Details** (Access Key *or* Client Credentials) →
   **Visibility** (Site / Group / Project) → **Save**, which runs a connection test.

CLI equivalent: `flyw admin storage list`.

## Reading Storage Health

`admin storage get <ID> -o json` returns the fields worth checking:

- `status_check` — `success` means the last connection test passed
- `last_status_check` / `next_status_check` — re-checked roughly every 4 hours, so a bucket
  that breaks shows up in `admin storage list` without anyone running a transfer
- `imports_enabled` / `exports_enabled` — set by `-m/--mode`. Omitting `--mode` at creation
  leaves **both** enabled; passing it restricts to one direction.
- `config.access_key` masked as `**********`, `connector_creds` false when using explicit keys

## Docs

Verified 200 as of 2026-07-27. Do not guess these paths — the
`admin_external-storage_how-to-configure-an-external-storage/` form is a 404.

| Page | URL |
|---|---|
| External Storage overview | <https://docs.flywheel.io/admin/external_storage/> |
| How to configure a storage | <https://docs.flywheel.io/admin/external_storage/how-to-configure-external-storage/> |
| Locating a storage ID | <https://docs.flywheel.io/admin/external_storage/external-storage-id/> |
| Admin-provided credentials | <https://docs.flywheel.io/admin/external_storage/external-storage-preconfigured-creds-option/> |
| Amazon HealthImaging | <https://docs.flywheel.io/admin/external_storage/external-storage-amazon-healthimaging/> |
| CLI command reference | <https://flywheel-io.gitlab.io/tools/app/cli/main/flyw/admin/storage/create/> |
