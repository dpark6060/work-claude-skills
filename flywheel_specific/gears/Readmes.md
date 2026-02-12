# Gear Readme's

## Requirements
- Must have manifest.json in top-level directory (quit if missing)
- Pull values from manifest using these mappings:
  - "gear name" = `name`
  - "gear label" = `label`  
  - "docker image" = `custom.gear-builder.image`
  - "inputs" = `inputs`
  - "config" = `config`
  - "description" = `description`
  - "license" = `license`
  - "cite" = `cite`
  - "classification" = `custom.gear-builder.category`


## Structure
**Title**: `gear name (gear label)`

**Overview** (keep skeleton links intact):
- Summary: copy `description` 
- Cite: copy `cite`
- License: copy `license`
- Classification: copy `classification` + keep "Gear Level"
- Table of contents, Inputs, Config, Outputs, Pre-requisites

**Usage**:
- Description, File Specifications (don't modify), Workflow, Use Cases, Logging

**FAQ, Contributing**


## Inputs Template
For each item in manifest `inputs`:
```
- <name>
    - Name: <name>
    - Type: <inputs.name.base>
    - Optional: <inputs.name.optional> (default: False)
    - Classification: <inputs.name.base>
    - Description: <inputs.name.description>
    - Notes: <leave blank>
```


## Config Template
For each item in manifest `config`:
```
- <name>
    - Name: <name>
    - Type: <config.name.type>
    - Description: <config.name.description>
    - Default: <config.name.default> (default: None)
```


## Outputs
**Files**: Scan code for output files (SDK uploads or `/flywheel/v0` saves). If found, use template:
```
- <filename>
    - Name: <filename>
    - Type: <extension>
    - Optional: <sometimes saved?> (or "unknown")
    - Classification: <leave blank>
    - Description: <brief description>
    - Notes: <leave blank>
```

**Metadata**: Notes on metadata saved via SDK "update info" calls or `.metadata.json`

**Pre-requisites**: Don't modify - user fills this

## Usage Details
**Description**: Summarize HOW gear works in flywheel (note unclear parts for user to clarify)

**File Specifications**: Don't modify

**Workflow**: Provide workflow summary + mermaid diagram if possible

**Use Cases**: If inferable from code, list as:
```
Use Case 1
*Conditions*:
- condition checkboxes
- present/absent items
{Description}
```

**Logging**: Overview of logging interpretation (skip if unclear from code) 


