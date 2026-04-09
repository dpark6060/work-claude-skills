# New Gears
## Description
Flywheel gears are often started from a "skeleton gear" template.  This template has several
template files that come with placeholders for certain values.  I would like your help replacing
these values.

## Values to replace
Please ask me for the following values:
1. Gear Name
2. Gear Label

## Files to replace values in
### manifest.json
 - replace the value of the "name" key with <Gear Name>
 - replace the value of the "label" key with <Gear Label>
 - replace the value of the `custom.gear-builder.image` key with: `flywheel/<Gear Name>:0.1.0`
 
 ### pyproject.toml
 - replace "name" under `[tool.poetry] with <Gear Name>
 - change the "version" under `[tool.poetry] to "0.1.0"
 
 