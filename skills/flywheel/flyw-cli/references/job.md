# Job Commands

## `job ls` — List Jobs

```bash
flyw job ls                                    # List recent jobs
flyw job ls -g my-gear                         # Filter by gear name
flyw job ls -u user@example.com                # Filter by user
flyw job ls -s pending                         # Filter by state
flyw job ls -p fw://group/project              # Filter by project
flyw job ls -g my-gear -s failed -l 50         # Combined filters
flyw job ls -o json                            # JSON output
flyw job ls -a                                 # Sort ascending by date
```

### Options

| Option | Description |
|---|---|
| `-g, --gear NAME` | Filter by gear name |
| `-u, --user EMAIL` | Filter by user |
| `-s, --state STATE` | Filter by job state |
| `-p, --project PRJ` | Filter by project ID or path |
| `-f, --filter FILT` | Full filter (overrides simple filters) |
| `-l, --limit N` | Number of jobs to return |
| `-a, --ascending` | Sort ascending by creation date |
| `-o, --output OUTPUT` | Output format |

## `job run` — Run Job on Site

Run a gear job on a Flywheel site. Prompts for input files and configuration.

```bash
flyw job run gear_name 1.0.0                          # Basic run
flyw job run gear_name 1.0.0 -m                       # Modify config first
flyw job run gear_name 1.0.0 -d fw://group/project    # Specify destination
flyw job run gear_name 1.0.0 -y                       # Auto-confirm all prompts
```

### Options

| Option | Description |
|---|---|
| `GEAR_NAME` | Gear name [required] |
| `VERSION` | Gear version [required] |
| `-m, --modify-config` | Modify gear config before running |
| `-d, --destination DEST` | Destination container (FW path or ID) |
| `-y, --yes` | Auto-confirm all prompts |

### Destination Container

**Analysis jobs**: destination is where the analysis container is attached. Defaults to the session of the first input file. Valid: projects, subjects, sessions, acquisitions.

**Utility jobs**: destination is where outputs are uploaded. Defaults to the parent container of the first input file. Modifying the destination should be done with caution.

### Input Specification

Inputs can be specified as:
- Flywheel container/file ID
- Flywheel path: `fw://group/project/subject/session/acquisition` (`fw://` prefix optional)

## `job pull` — Pull Job for Local Debugging

Download a completed job's configuration, inputs, and gear image for local debugging:

```bash
flyw job pull <JOB_ID>                    # Pull to temp directory
flyw job pull <JOB_ID> /tmp/debug         # Pull to specific directory
flyw job pull <JOB_ID> --no-image         # Skip pulling gear image
```

### Options

| Option | Description |
|---|---|
| `JOB_ID` | Job ID [required] |
| `DIR` | Output directory [optional] |
| `--image / --no-image` | Pull gear image if not present |

### Pulled Directory Structure

```
<gear-name>-<version>-<job-id>/
├── config.json          # Job configuration (API key redacted)
├── manifest.json        # Gear manifest
├── input/
│   └── <input-name>/
│       └── <file>
├── output/
├── run.sh
└── work/
```

**Important**: API keys are redacted in the pulled config. Add them back with:
```bash
flyw gear config -i api_key=$MY_API_KEY
```

Then run locally with `flyw gear run .` (see gear-development.md).

## `job retry` — Retry a Job

```bash
flyw job retry <JOB_ID>              # Retry (prompts if already retried)
flyw job retry <JOB_ID> -f           # Force relaunch without prompt
```

### Options

| Option | Description |
|---|---|
| `JOB_ID` | Job ID [required] |
| `-f, --force` | Force relaunch if already retried |

Creates a new job if the original has already been retried.

## `job batch run` — Run Gear Across Multiple Containers

Execute a gear across multiple containers simultaneously:

```bash
flyw job batch run gear_name 1.0.0 'fw://group/project/sub1' 'fw://group/project/sub2'
flyw job batch run gear_name 1.0.0 'fw://group/project' -m     # Modify config
flyw job batch run gear_name 1.0.0 'fw://group/project' -o flexible
flyw job batch run gear_name 1.0.0 'fw://group/project' -y     # Auto-confirm
```

### Options

| Option | Description |
|---|---|
| `GEAR_NAME` | Gear name [required] |
| `VERSION` | Gear version [required] |
| `CONTAINER...` | Container paths or IDs [required] |
| `-m, --modify-config` | Modify config before running |
| `-o, --optional-input-policy POLICY` | Handle optional inputs: `ignored` (default), `flexible`, `required` |
| `-y, --yes` | Auto-confirm all prompts |

### Target Container Logic

- If gear requires input files → one job per child **acquisition**
- If gear has no inputs → one job per child **session**
- If a container has ambiguous file matches (multiple files matching same input type) → **skipped**

### Optional Input Policy

| Policy | Behavior |
|---|---|
| `ignored` (default) | Run without optional input |
| `flexible` | Use optional input if matching file found |
| `required` | Only run where matching optional input exists |

Before execution, the command reports:
- Number of jobs queued
- Number of containers skipped (ambiguous inputs)
