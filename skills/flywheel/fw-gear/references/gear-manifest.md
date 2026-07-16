---
type: Library Reference
title: fw-gear Manifest (manifest.json)
description: The manifest.json structure — name rules, config and input fields, runtime directory layout, and the output metadata spec.
tags: [fw-gear, manifest, gears]
timestamp: 2026-07-15T00:00:00Z
---

# fw-gear Manifest (manifest.json)

## Contents
- [Name Rules](#name-rules)
- [Minimal manifest.json](#minimal)
- [Config Fields](#config-fields)
- [Input Fields](#input-fields)
- [Input Key Naming Rules](#key-naming)
- [Directory Layout at Runtime](#directory-layout)
- [Output Metadata Spec (.metadata.json)](#output-metadata)
- [Custom Manifest Fields](#custom-fields)
- [Output Configuration](#output-config)
- [Networking Capability](#networking)
- [Environment Variables](#environment)

---

The `manifest.json` lives at `/flywheel/v0/manifest.json` and describes the gear's
inputs, configuration, and metadata. It is baked into the Docker image at build time.

---

## Name Rules

The `"name"` field must match `^[a-z0-9\-]+$` (lowercase letters, digits, hyphens only;
max 100 characters). Underscores, spaces, and uppercase are not allowed.

---

## Minimal manifest.json

```json
{
  "name": "my-gear",
  "label": "My Gear",
  "description": "A brief description of what this gear does.",
  "version": "0.1.0",
  "author": "Flywheel",
  "maintainer": "Your Name",
  "cite": "",
  "license": "MIT",
  "url": "",
  "source": "",
  "config": {},
  "inputs": {},
  "custom": {
    "gear-builder": {
      "image": "flywheel/my-gear:0.1.0"
    }
  },
  "command": "python run.py"
}
```

---

## Config Fields

Each key under `"config"` is a configuration option:

```json
"config": {
  "threshold": {
    "type": "number",
    "default": 0.5,
    "minimum": 0.0,
    "maximum": 1.0,
    "description": "Threshold value for processing."
  },
  "debug": {
    "type": "boolean",
    "default": false,
    "description": "Enable debug logging."
  },
  "mode": {
    "type": "string",
    "enum": ["fast", "accurate"],
    "default": "accurate",
    "description": "Processing mode."
  },
  "optional_tag": {
    "type": "string",
    "optional": true,
    "description": "An optional tag to apply."
  }
}
```

**Rules:**
- `type` is required; valid values: `"string"`, `"integer"`, `"number"`, `"boolean"`, `"array"`
- Cannot have both `"default"` and `"optional"` on the same field
- Use `"optional": true` for fields that may be entirely absent at runtime
- JSON schema constraints (`minimum`, `maximum`, `enum`, `minItems`, `maxItems`) are supported

---

## Input Fields

Each key under `"inputs"` is a gear input:

### File Input

```json
"inputs": {
  "dicom": {
    "base": "file",
    "description": "Input DICOM file or ZIP archive.",
    "optional": false
  },
  "atlas": {
    "base": "file",
    "optional": true,
    "description": "Optional atlas file."
  }
}
```

To restrict to a specific file type (guides the UI, not strictly enforced):
```json
"dicom": {
  "base": "file",
  "type": { "enum": ["dicom"] },
  "description": "A DICOM file."
}
```

### API Key Input

Required for `context.client` to be available in the gear:

```json
"api-key": {
  "base": "api-key"
}
```

**Do NOT use `"read-only": true`** — it is deprecated. Declare the api-key input
as the plain `{"base": "api-key"}` form above whether or not the gear writes.

**Important:** The key name (`"api-key"` above) can be anything; `"base": "api-key"` is
what tells Flywheel to inject an API key at runtime.

### Context Input

Values pulled from container metadata (e.g., license keys set at the project level):
```json
"matlab_license_code": {
  "base": "context"
}
```

Access in gear code:
```python
ctx_input = context.config.get_input("matlab_license_code")
if ctx_input and ctx_input.get("found"):
    license_code = ctx_input["value"]
```

---

## Input Key Naming Rules

Input keys must match `^[A-Za-z0-9_-]+$`. No dots, spaces, or slashes. Dots break
dot-notation used in the UI (e.g., `inputs.dicom.path`).

---

## Directory Layout at Runtime

At gear execution time, the container has:

```
/flywheel/v0/
    manifest.json          # baked in at build time
    config.json            # provided by Flywheel at runtime
    input/
        <input-name>/
            <filename>     # e.g., input/dicom/my-scan.dcm
    output/                # write output files here
    work/                  # scratch space (not saved)
```

The gear's `run` command is executed from `/flywheel/v0/`.

---

## Output Metadata Spec (.metadata.json)

Placed in the output directory; Flywheel reads it after job completion.

```json
{
  "acquisition": {
    "info": { "my_key": "my_value" },
    "files": [
      {
        "name": "output.nii.gz",
        "type": "nifti",
        "modality": "MR",
        "classification": { "Measurement": ["T1"] },
        "info": { "custom_metric": 42 }
      }
    ]
  },
  "session": {
    "info": { "session_processed": true }
  }
}
```

Use `context.metadata.*` methods — they build this file automatically. Do not write it
manually unless absolutely necessary.

---

## Custom Manifest Fields (gear-builder namespace)

```json
"custom": {
  "gear-builder": {
    "image": "flywheel/my-gear:0.1.0",
    "category": "Image Processing"
  },
  "flywheel": {
    "suite": "Utility",
    "show-job": true,
    "classification": {
      "species": ["Human"],
      "organ": ["Brain"],
      "function": ["Image Processing - Structural"],
      "modality": ["MR"]
    }
  }
}
```

The `gear-builder.image` value is used by the Flywheel gear-builder toolchain to tag
the Docker image.

---

## Output Configuration

Controls how Flywheel handles output files:

```json
"output_configuration": {
  "enforce_file_version_match": true
}
```

`enforce_file_version_match`: If `true`, the job fails if a newer version of an output
file was uploaded to Flywheel while the job was running. Protects against overwriting
concurrent uploads. Default: `false`.

**Output file limit:** Flywheel saves a maximum of **100 files** from the output
directory. Gears that produce more will have output truncated. If you need to output
many files, ZIP them into a single archive.

---

## Networking Capability

If the gear makes outbound network calls (including to the Flywheel API), declare it:

```json
"capabilities": ["networking"]
```

---

## Environment Variables

```json
"environment": {
  "FREESURFER_HOME": "/opt/freesurfer",
  "PATH": "/opt/freesurfer/bin:/usr/local/bin:/usr/bin:/bin"
}
```
