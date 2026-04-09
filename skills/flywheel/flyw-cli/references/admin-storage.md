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
