# fw-gear Utils

## exec_command — Run External Binaries

Import: `from fw_gear.utils.wrapper.command import exec_command`

(Also works as `from fw_gear.utils.wrapper import exec_command` but the `.command` submodule path is preferred.)

Runs a subprocess and returns `(stdout, stderr, return_code)`. Raises `RuntimeError`
on non-zero exit.

```python
from fw_gear.utils.wrapper.command import exec_command

# Basic usage
stdout, stderr, rc = exec_command(["freesurfer", "--version"])

# Stream output live (useful for long-running tools)
stdout, stderr, rc = exec_command(
    ["recon-all", "-all", "-s", subject_id],
    stream=True,
    stream_mode="throttled",   # only show important lines frequently
    throttle_sec=5.0,
    logfile=str(context.output_dir / "recon-all.log")
)
```

### stream_mode Options

| Mode | Behavior |
|---|---|
| `"all"` | Print every line live |
| `"filter_only"` | Print only lines matching the important-line pattern |
| `"throttled"` | Print important lines always; throttle non-important by `throttle_sec` |

### Customizing the "Important Lines" Filter

By default, `exec_command` treats lines matching a built-in regex as "important" (always
printed). Override it with `EXEC_ALWAYS_PRINT_RE` before importing the module:

```python
import os
os.environ["EXEC_ALWAYS_PRINT_RE"] = r"\b(error|failed|timeout|warn(?:ing)?)\b"
from fw_gear.utils.wrapper import exec_command
```

Or override after import:
```python
import re
from fw_gear.utils import wrapper
wrapper._ALWAYS_PRINT_RE = re.compile(r"\b(error|failed|timeout|warn(?:ing)?)\b", re.I)
```

Or set it in the `Dockerfile` so all runs use a custom filter:
```dockerfile
ENV EXEC_ALWAYS_PRINT_RE="\b(error|failed|timeout|warn(?:ing)?)\b"
```

### Shell Redirects

```python
cmd = ["my-tool", "--output", "out.txt", ">>", "run.log", "2>&1"]
stdout, stderr, rc = exec_command(cmd, shell=True)
```

### Custom Environment Variables

```python
stdout, stderr, rc = exec_command(
    ["my-tool"],
    environ={"MY_ENV_VAR": "value", "ANOTHER": "123"}
)
```

**Key behaviors:**
- `stdin` is set to `DEVNULL` to avoid interactive blocking
- When `stream=True`, stderr is merged into stdout to prevent deadlocks
- Raises `RuntimeError` on non-zero return code

---

## ZIP Archive Utilities

Import: `from fw_gear.utils.archive.zip_manager import unzip_archive, zip_output, zip_info, get_config_from_zip`

### Unzip

```python
from fw_gear.utils.archive.zip_manager import unzip_archive

unzip_archive(
    zipfile_path=str(context.config.get_input_path("archive")),
    output_dir=str(context.work_dir)
)
```

### Create ZIP

```python
from fw_gear.utils.archive.zip_manager import zip_output

zip_output(
    root_dir=str(context.work_dir),
    source_dir="results",                         # subdir within root_dir to zip
    output_zip_filename=str(context.output_dir / "results.zip"),
    exclude_files=["results/temp.txt"]
)
```

### List ZIP Contents

```python
from fw_gear.utils.archive.zip_manager import zip_info

files = zip_info(str(context.config.get_input_path("archive")))
for f in files:
    print(f)
```

### Extract Config JSON from ZIP

```python
from fw_gear.utils.archive.zip_manager import get_config_from_zip

config_dict = get_config_from_zip(str(context.config.get_input_path("archive")))
if config_dict:
    setting = config_dict["config"]["some_key"]
```

---

## SDK Retry Handler

Import: `from fw_gear.utils.contextutils import sdk_post_retry_handler`

Patches the SDK session to retry on HTTP 429, 500, 502, 503, 504. Use around
update/metadata operations, **not** uploads or container creation.

```python
from fw_gear.utils.contextutils import sdk_post_retry_handler

with sdk_post_retry_handler(context.client):
    context.client.modify_container_info(container_id, {"key": "value"})
```

---

## Report Open File Descriptors

Import: `from fw_gear.utils.contextutils import report_open_fds`

Decorator that logs the count of open file descriptors before and after a function.
Useful for diagnosing file descriptor leaks in gears that process many files.

```python
from fw_gear.utils.contextutils import report_open_fds

@report_open_fds(sockets_only=False)    # True = only count open sockets
def process_batch():
    pass
```

---

### SDK Delete 404 Handler

Silences 404 errors on delete operations (useful when a resource may already be gone):

```python
from fw_gear.utils.contextutils import sdk_delete_404_handler

with sdk_delete_404_handler(context.client):
    context.client.delete_container(container_id)
```

---

## Install Requirements at Runtime

Import: `from fw_gear.utils.utils_helpers import install_requirements`

Installs packages from a `requirements.txt` file at gear runtime. Useful for gears that
accept a user-supplied `requirements.txt` as an optional input.

```python
from fw_gear.utils.utils_helpers import install_requirements

requirements = gear_context.config.get_input_path("requirements")
if requirements:
    install_requirements(requirements)
```

Typical manifest entry:
```json
"requirements": {
  "base": "file",
  "optional": true,
  "description": "Optional requirements.txt to install additional packages."
}
```

---

## FLYWHEEL_HIERARCHY — Container Level Constants

Import: `from fw_gear.file import FLYWHEEL_HIERARCHY`

An ordered list of Flywheel container type strings from top to bottom:
`["group", "project", "subject", "session", "acquisition"]`

Useful for walking the hierarchy to build a path or find a parent container:

```python
from fw_gear.file import FLYWHEEL_HIERARCHY

# Build a slash-delimited path from project → destination parent
parent = context.config.get_destination_parent()

hierarchy_list = []
for level in FLYWHEEL_HIERARCHY[1:]:  # skip "group"
    if level == parent.container_type:
        break
    fw_object = context.client.get(parent.parents.get(level))
    hierarchy_list.append(fw_object.label)

hierarchy_list.append(parent.label)  # add the lowest level
path = "/".join(hierarchy_list)
```

---

## Launching a Child Gear (setup_gear_run)

Import: `from fw_gear.utils.sdk_helpers import setup_gear_run`

Prepares and launches another gear from within a gear. Requires `context.client`.

```python
from fw_gear.utils.sdk_helpers import setup_gear_run

# Get the input file object from current gear
input_file_id = context.config.get_input("dicom")["hierarchy"]["id"]
input_file = context.client.get_file(input_file_id)

geardoc, inputs, config = setup_gear_run(
    context.client,
    "dicom-fixer",                   # gear name
    {
        "dicom": input_file,         # gear inputs (SDK file objects)
        "debug": True,               # gear config options
        "tag": "auto-run"
    }
)

# Launch the gear
parent_container = input_file.parent_ref.get("type")
geardoc.run(inputs=inputs, config=config, destination=parent_container)
```

---

## FreeSurfer License

Import: `from fw_gear.utils.licenses.freesurfer import install_freesurfer_license`

Installs the FreeSurfer license from one of three sources (in priority order):
1. `freesurfer_license_file` input file
2. `freesurfer_license_key` config string
3. Flywheel project metadata key `FREESURFER_LICENSE`

```python
from fw_gear.utils.licenses.freesurfer import install_freesurfer_license

with GearContext() as context:
    install_freesurfer_license(context)               # default $FREESURFER_HOME/license.txt
    install_freesurfer_license(context, "/opt/fs/license.txt")  # custom path
```

Raises `FileNotFoundError` if no license source is found.

Required manifest entries (all optional — gear falls back through sources):
```json
{
  "inputs": {
    "freesurfer_license_file": {
      "base": "file",
      "optional": true,
      "description": "FreeSurfer license file"
    }
  },
  "config": {
    "freesurfer_license_key": {
      "type": "string",
      "optional": true,
      "description": "FreeSurfer license key text"
    }
  }
}
```

---

## Resource Usage Monitoring

Requires `fw-gear[monitoring]` (installs `psutil`, `pandas`, `matplotlib`). Decorator
that records CPU, memory, disk, and network usage during a function:

```python
from fw_gear.utils.contextutils import report_usage_stats

@report_usage_stats(
    interval=2.0,           # sampling interval in seconds
    save_output=True,       # save CSV to output dir
    plot=True,              # generate PNG chart
    output_format="png",
    disk_monitor_dirs=["/", "/tmp"],  # directories to track disk usage
    cpu_usage=True,
    mem_usage=True,
    disk_usage=True,
    net_usage=True,
)
def run_analysis():
    # long-running work
    pass
```

Outputs `{function_name}.csv` and optional `{function_name}.png` to
`/flywheel/v0/output/` by default.

---

## Nipype Integration

Requires `fw-gear[nipype]`. Generates a Nipype interface from a gear manifest so the
gear can be used as a Nipype workflow node.

Import: `from fw_gear.utils.wrapper.nipype import GearContextInterfaceBase`

```python
from fw_gear.utils.wrapper.nipype import GearContextInterfaceBase
from fw_gear.context import GearContext

with GearContext() as context:
    # Create a Nipype interface class from the manifest
    MyGearInterface = GearContextInterfaceBase.factory(context.manifest.to_dict())

    # Use in a Nipype workflow
    from nipype import Workflow, Node
    wf = Workflow(name="my_workflow")
    gear_node = Node(MyGearInterface(), name="gear_step")
    gear_node.inputs.config_dict = {
        "config": context.config.opts,
        "inputs": context.config.inputs,
    }
    wf.add_nodes([gear_node])
    wf.run()
```

Flywheel types map to Nipype traits: `boolean→Bool`, `string→Str`, `integer→Int`,
`number→Float`, `array→List`, `file→File`.
