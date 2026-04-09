# fw-gear Metadata

Gears can write metadata back to Flywheel containers and files. There are two mechanisms:

1. **`.metadata.json`** (no SDK required) — updates destination container hierarchy on
   job completion. Handled by `context.metadata`.
2. **SDK methods** — can update any container. Requires `api-key` input.

Always prefer the `.metadata.json` approach when only updating the destination hierarchy.

---

## Update Container Metadata (No SDK)

Adds to the `info` dict of a container in the destination hierarchy:

```python
context.metadata.update_container(
    context.config.destination.get("type"),  # e.g., "acquisition", "analysis"
    info={"my_metric": 42, "processing_complete": True}
)

# Update a parent container (e.g., the session)
context.metadata.update_container(
    "session",
    label="Session 1",          # Optional: target by label
    info={"session_processed": True}
)
```

**Arguments:**
- `container_type` (str): Container type string (`"acquisition"`, `"session"`, `"subject"`, `"analysis"`)
- `deep` (bool): If True, recursively merge subdicts rather than overwrite (default: False)
- `**kwargs`: Fields to set — typically `info={}` but can also include `label`, `modality`, etc.

---

## Update File Metadata (No SDK)

Adds metadata to an output file or a sibling input file:

```python
context.metadata.update_file_metadata(
    file_="out-file.nii.gz",          # filename string, SDK file object, or config dict
    container_type="acquisition",      # optional, inferred from destination if omitted
    modality="MR",
    classification={"Measurement": ["T1"]}
)
```

**Arguments:**
- `file_` (str | dict | SDK file): The file to update
- `deep` (bool): Recursive merge (default: False)
- `container_type` (str, optional): Parent container type
- `**kwargs`: Metadata fields (`modality`, `classification`, `info`, etc.)

---

## Add QC Result to a File (No SDK)

Records a named QC result under the file's `info.qc.<gear-name>` namespace:

```python
# From an input file object
file_obj = context.config.get_input("input_file")
context.metadata.add_qc_result(
    file_obj,
    "my_qc_check",   # QC result name
    "pass",          # state: "pass", "fail", or "na"
    snr=42.5,
    motion_mm=0.2
)

# From an output filename
context.metadata.add_qc_result(
    "output.nii.gz",
    "quality_check",
    "fail",
    reason="motion too high"
)
```

**Arguments:**
- `file_` (str | dict | SDK file): Target file
- `name` (str): Name of the QC check
- `state` (str): `"pass"`, `"fail"`, or `"na"`
- `**data`: Additional key-value QC data

**Scope limitation:** `add_qc_result` writes to `.metadata.json`, which only applies
to the gear's launch container level and **parent** levels (i.e., the launched level
and UP the hierarchy). For example, a gear launched at session level can use
`add_qc_result` on files attached to the session, subject, or project — but **not**
on files attached to acquisitions (children). To add QC results to files on child
containers, use `add_qc_result_via_sdk` instead (requires `api-key` input).

---

## Add QC Result to the Analysis Container (No SDK)

When the gear destination is an analysis container:

```python
context.metadata.add_qc_result_to_analysis(
    "my_analysis_qc",
    "pass",
    metric1=0.95,
    metric2="good"
)
```

---

## Add File Tags (No SDK)

```python
file_obj = context.config.get_input("input_file")
context.metadata.add_file_tags(file_obj, "processed")

# Multiple tags
context.metadata.add_file_tags(file_obj, ["processed", "reviewed"])
```

---

## SDK-Enabled Metadata Methods

These require `context.client` to be available (i.e., an `api-key` input).

### Modify Container Info via SDK

```python
context.metadata.modify_container_info(
    "<container-id>",
    infoA="value1",
    infoB="value2"
)
```

Uses the SDK `set` operation — replaces existing keys rather than merging.

### Add QC Result via SDK (for Child Containers)

Use this when you need to add QC results to files on containers **below** the gear's
launch level. For example, a gear launched at session level that needs to write QC
results to files on individual acquisitions must use this method — `add_qc_result`
(the `.metadata.json` approach) cannot reach child containers.

```python
# By filename string (input file that triggered the gear)
context.metadata.add_qc_result_via_sdk(
    cont_="input_file.dcm",
    name="input_qc",
    state="PASS",
    data={"my-result": "test"}
)

# By SDK container object — e.g., targeting a child acquisition
acquisition = context.client.get_acquisition("<id>")
context.metadata.add_qc_result_via_sdk(
    cont_=acquisition,
    name="acquisition_qc",
    state="PASS",
    data={"score": 0.99}
)
```

---

## Complete Example

```python
def write_metadata(context: GearContext, output_filename: str, snr: float) -> None:
    dest_type = context.config.destination.get("type")

    # Update destination container
    context.metadata.update_container(dest_type, info={"snr": snr})

    # Update output file metadata
    context.metadata.update_file_metadata(
        output_filename,
        modality="MR",
        classification={"Measurement": ["T1"]}
    )

    # Add QC result to input file
    input_obj = context.config.get_input("input_file")
    context.metadata.add_qc_result(
        input_obj,
        "snr_check",
        "pass" if snr > 10 else "fail",
        snr=snr
    )
```

### Resulting .metadata.json (acquisition destination)

```json
{
    "acquisition": {
        "info": {"snr": 42.5},
        "files": [
            {
                "name": "output.nii.gz",
                "modality": "MR",
                "classification": {"Measurement": ["T1"]}
            },
            {
                "name": "input.dcm",
                "info": {
                    "qc": {
                        "my-gear-name": {
                            "snr_check": {
                                "state": "PASS",
                                "snr": 42.5
                            }
                        }
                    }
                }
            }
        ]
    }
}
```

---

## Notes

- `.metadata.json` is written automatically when the `GearContext` exits cleanly
- By default (`fail_on_validation=True`), invalid metadata fails the gear
- `.metadata.json` only applies to the gear's launch container level and its parents
  (launched level and UP); use SDK methods (`add_qc_result_via_sdk`,
  `modify_container_info`) for child containers
- Long lists in log output are truncated automatically
