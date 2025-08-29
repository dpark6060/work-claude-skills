# Gear Readme's

## Values
The readme will take heavily from the gear manifest.json file. 
If you cannot find that file in the top level directory, do not attempt to create a readme, and
instead just say that you need a manifest to do this task.  

When I say "gear name", I'm referring to the "name" key in the manifest, and you should use the
value of the "name" key.  Here is a list of other name/key pairings:

 - "gear name": "name"
 - "gear label": "label"
 - "docker image": "custom.gear-builder.image"
 - "inputs": "inputs"
 - "config": "config"
 - "description": "description"
 - "license": "license"
 - "cite": "cite"
 - "classification": "custom.gear-builder.category"

Use these values for when when I refer to a section of the manifest. 

If I refer to a section that's not listed here, assume I am directly giving you the json key for the
manifest.


## Structure
Readme's should have at minimum the following sections:

- [ ] Title
- [ ] Overview
    - [ ] Summary
    - [ ] Cite
    - [ ] License
    - [ ] Classification
    - [ ] Table of contents
    - [ ] Inputs
    - [ ] Config
    - [ ] Outputs
    - [ ] Pre-requisites
- [ ] Usage
    - [ ] Description
        - [ ] File Specifications
    - [ ] Workflow
    - [ ] Use Cases
    - [ ] Logging
- [ ] FAQ
- [ ] Contributing

## Title
The title should be: "gear name (gear label)"

## Overview
This section begins with a link Usage and FAQ sections.  Do not modify this section of the skeleton.

### Summary
Copy "description" from the manifest and put it here.

### Cite
Copy "cite" from the manifest and put it here.

### License
Copy "license" from the manifest and put it here.

### Classification
Copy "classification" from the manifest and put it here.

Leave the "Gear Level" part here as well.


### Inputs
Create one entry for every item in the "inputs" section of the manifest.
Each item should be created as follows:

If I have this input entry in the manifests 'input' section:
```json
    input-key: {
      "base": "file",
      "description": "input description"
    }
```

Then create the following entry, where values in <> need to be populated from the entry above:

```
- <name>
    - Name: <name>
    - Type: <type>
    - Optional: <optional>
    - Classification: <classification>
    - Description: <description>
    - Notes: <notes>
```

where the values are from:

`<name>`: the key for this input item, "input-key" in the example above.

`<type>`: the value in `inputs.<name>.base`.

`<optional>`: the value in `inputs.<name>.optional`, or "False" if not present.

`<classification>`: the value in `inputs.<name>.base`.

`<description>`: the value in `inputs.<name>.description`, or blank if not present.

`<notes>`: leave blank, for the user to enter if they have notes.


### Config
Create one entry for every item in the "config" section of the manifest.
Each item should be created as follows:

If I have this input entry in the manifests 'config' section:

```json
    "config-key": {
      "default": false,
      "description": "Log debug messages",
      "type": "boolean"
    }
```

Then create the following entry, where values in <> need to be populated from the entry above:

- `<name>`
    - Name: `<name>`
    - Type: `<type>`
    - Description: `<description>`
    - Default: `<default>`

where the values are from:

`<name>`: the key for this config item, "config-key" in the example above.

`<type>`: the value in `config.<name>.type`.

`<description>`: the value in `config.<name>.description`, or blank if not present.

`<default>`: from `config.<name>.default` if present, otherwise "None"`


### Outputs

Has the following sub-sections:
- Files
- Metadata

#### Files
Scan the code as best you can for any output files you can identify.  Output files can either come
from sdk uploads to flywheel, or they're just files saved in the `/flywheel/v0` directory. 

If you can't identify any files, create this section, but leave it blank.  

If you do find files, list them here with the following format and do your best to fill in the
following items for each file:

- `<Name of output file>`

    - Name: `<Name of output file>`

    - Type: `<Type of output file from extension>`

    - Optional: `<If the output file only sometimes will be saved>`, or "unknown" if you can't tell

    - Classification: Honestly just leave blank

    - Description: Try to provide a brief description of the file

    - Notes: leave blank


#### Metadata
This section should just be general notes on any metadata saved.  Metadata is saved with sdk "update
info" calls, or by writing to the .metadata.json file, usually with the gear toolkit.

### Pre-requisites
Leave this entire section untouched, the user must do it themselves.

## Usage
This section provides a more detailed description of the gear, including not just WHAT it does, but 
HOW it works in flywheel.

### Description
Try to summarize how the gear works as best you can.  If there are parts you don't understand, make
a note that a user should add more clarity in that section. 

### File Specifications
Do not modify this section

### Workflow
Try to provide a summary of the workflow of this gear.   If possible, generate a very simplified
mermaid diagram.
 

### Use Cases
If you can infer some use cases from the code, list them here, otherwise do not modify this section.
It is ok to not modify this section. 

If you can infer use cases, list them like this:

Use Case 1
*Conditions*:

{A list of conditions that result in this use case}

 Possibly a list of check boxes indicating things that are absent

 and things that are present

{Description of the use case}


### Logging
An overview/orientation of the logging and how to interpret it.

If you cannot infer information on this from the code, do not alter this section. 


