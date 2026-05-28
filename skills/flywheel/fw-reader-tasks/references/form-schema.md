# Form Schema Reference

This document covers the JSON schema for reader task forms in both format generations.
Check the top-level key of your form JSON to determine which format you're working with.

## Contents
- [Which format do I have?](#which-format)
- [V3 Format (Tasks Manager)](#v3-format)
  - [Top-level structure](#v3-top-level)
  - [Field object properties](#v3-field-properties)
  - [Field types](#v3-field-types)
  - [Conditional display (`showWhen`)](#v3-conditional)
  - [Validation](#v3-validation)
  - [E-signature config](#v3-esignature)
  - [Completion tags](#v3-completion-tags)
  - [Full V3 example](#v3-example)
- [V2 Format (Legacy viewer)](#v2-format)
  - [Top-level structure](#v2-top-level)
  - [Component object properties](#v2-component-properties)
  - [Field types](#v2-field-types)
  - [⚠️ `required` gotcha](#v2-required-gotcha)
  - [Conditional display (`conditional.json`)](#v2-conditional)
  - [Cross-field validation](#v2-cross-field-validation)
  - [`info` type (display container metadata)](#v2-info-type)
  - [⚠️ Hidden fields preserve responses](#v2-hidden-fields)
  - [V2 viewer config](#v2-viewer-config)
- [Migrating V2 → V3](#migration)

---

## Which format do I have?

| Top-level key | Format | Viewer |
|---------------|--------|--------|
| `form.fields` | **V3 — Tasks Manager** (current) | OHIF_V3 |
| `studyForm.components` | **V2 — Legacy viewer** (formio) | OHIF |

---

## V3 Format (Tasks Manager — `form.fields`)

### Top-level structure

```json
{
  "form": {
    "title": "Protocol Display Name",
    "description": "Optional description",
    "defaults": {},
    "fields": [ /* field objects */ ]
  },
  "esignature_config": null,
  "completion_tags": []
}
```

**`esignature_config` is always required** — omitting it entirely causes a validation
error. Use `null` if e-signatures are not needed.

---

### V3 Field Object Properties

```json
{
  "key": "field_key",           // unique identifier — used as the key in response_data
  "type": "radio",              // see field types below
  "label": "Display label",     // shown to reader in viewer
  "description": "...",         // optional extra context below the label
  "helperText": "...",          // placeholder / helper text
  "requiredWhenVisible": true,  // if true: must answer before submitting (when visible)
  "options": [                  // for radio, dropdown, checkboxes
    { "label": "Yes", "value": "yes" },
    { "label": "No", "value": "no" }
  ],
  "showWhen": { ... }           // JSONLogic condition for conditional display
}
```

### V3 Field Types

| `type` | Input style | `options` needed? |
|--------|------------|-------------------|
| `radio` | Single choice, radio buttons | Yes |
| `dropdown` / `select` | Single choice, dropdown | Yes |
| `checkboxes` | Multi-select checkboxes | Yes |
| `textfield` | Short free-text | No |
| `textarea` | Long free-text | No |
| `paragraph` | Display-only text (no input) | No |
| `instructions` | Guidance text (can be conditional) | No |

### V3 Conditional Display (`showWhen`)

Uses JSONLogic syntax. Field is shown when the condition is true.

```json
// Show "regions" only when scan_read == "elevated"
"showWhen": {
  "===": [{ "var": "scan_read" }, "elevated"]
}

// Show when either of two values is selected
"showWhen": {
  "or": [
    { "===": [{ "var": "consensus_read" }, "yes"] },
    { "===": [{ "var": "consensus_read" }, "maybe"] }
  ]
}

// Show when a numeric field is above a threshold
"showWhen": {
  ">": [{ "var": "centiloid_value" }, 24]
}
```

The `var` key references the `key` of another field. Fields are evaluated top-to-bottom;
only reference keys of fields that appear earlier in the `fields` array.

### V3 Validation

JSONLogic syntax, referenced in a `validation` property:

```json
{
  "key": "score",
  "type": "textfield",
  "label": "Centiloid Score",
  "validation": {
    "and": [
      { ">=": [{ "var": "score" }, 0] },
      { "<=": [{ "var": "score" }, 500] }
    ]
  }
}
```

### V3 E-Signature Configuration

```json
"esignature_config": {
  "required": true,
  "reasons": [
    "I confirm this read is accurate and complete",
    "Data reviewed and ready for submission"
  ]
}
```

E-signatures are MFA-verified and create an immutable audit record. Required for
21 CFR Part 11 compliance on Validated Instances.

### V3 Completion Tags

Auto-apply Data Tags to the parent container when a task is completed:

```json
"completion_tags": ["read-complete", "site-a-reviewed"]
```

---

### Full V3 Example

```json
{
  "form": {
    "title": "PET Amyloid Visual Read",
    "description": "Standard amyloid PET visual read form",
    "defaults": {},
    "fields": [
      {
        "key": "scan_read",
        "type": "radio",
        "label": "2.1 Based on tracer-specific guidelines, this scan is:",
        "requiredWhenVisible": true,
        "options": [
          { "label": "Non-Elevated (No evidence for cortical tracer binding)", "value": "non-elevated" },
          { "label": "Elevated", "value": "elevated" }
        ]
      },
      {
        "key": "regions",
        "type": "checkboxes",
        "label": "2.2 Indicate regions with cortical tracer retention:",
        "requiredWhenVisible": true,
        "showWhen": { "===": [{ "var": "scan_read" }, "elevated"] },
        "options": [
          { "label": "Frontal", "value": "Frontal" },
          { "label": "Parietal", "value": "Parietal" },
          { "label": "Post Cingulate/Precuneus", "value": "Post Cingulate/Precuneus" },
          { "label": "Temporal", "value": "Temporal" },
          { "label": "Occipital", "value": "Occipital" }
        ]
      },
      {
        "key": "consensus_read",
        "type": "radio",
        "label": "3.1 Is a consensus review needed?",
        "requiredWhenVisible": true,
        "options": [
          { "label": "Yes", "value": "yes" },
          { "label": "No", "value": "no" }
        ]
      },
      {
        "key": "final_read",
        "type": "radio",
        "label": "4.1 Is the read final and ready to return?",
        "requiredWhenVisible": true,
        "showWhen": { "===": [{ "var": "consensus_read" }, "no"] },
        "options": [
          { "label": "Yes, read is complete", "value": "yes" },
          { "label": "No", "value": "no" }
        ]
      }
    ]
  },
  "esignature_config": null,
  "completion_tags": []
}
```

---

## V2 Format (Legacy Viewer — `studyForm.components`)

The V2 format uses the **formio** schema. It is used by the legacy OHIF viewer (`viewer: "OHIF"`).

### Top-level structure

```json
{
  "studyForm": {
    "components": [ /* component objects */ ]
  }
}
```

The viewer config is a separate JSON object (not embedded in the form).

---

### V2 Component Object Properties

```json
{
  "key": "field_key",
  "type": "radio",
  "label": "Display label",
  "validate": {
    "required": true,
    "custom": { /* JSONLogic cross-field validation */ }
  },
  "conditional": {
    "json": { /* JSONLogic show condition */ }
  },
  "values": [
    { "value": "yes", "label": "Yes" },
    { "value": "no", "label": "No" }
  ]
}
```

### V2 Field Types

| `type` | Input style |
|--------|------------|
| `radio` | Single choice, radio buttons |
| `dropdown` | Single choice, dropdown |
| `selectboxes` | Multi-select checkboxes |
| `textfield` / `text` | Short free-text |
| `textarea` | Long free-text |
| `info` | Display-only block that can surface container metadata |

### ⚠️ V2 `required` Gotcha

**This is the most common bug found in legacy forms:**

```json
// WRONG — top-level required is ignored by formio
{
  "key": "consensus_read",
  "required": true,       // ← ignored!
  "type": "radio"
}

// CORRECT — must be inside validate
{
  "key": "consensus_read",
  "validate": { "required": true },
  "type": "radio"
}
```

### V2 Conditional Display (`conditional.json`)

```json
// Show when scan_read == "elevated"
"conditional": {
  "json": { "==": [{ "var": "scan_read" }, "elevated"] }
}

// Show when either value is set (i.e. scan_read has any answer)
"conditional": {
  "json": {
    "or": [
      { "==": [{ "var": "scan_read" }, "elevated"] },
      { "==": [{ "var": "scan_read" }, "non-elevated"] }
    ]
  }
}
```

### V2 Cross-Field Validation (`validate.custom`)

Custom validators on a field can reference other field values:

```json
"validate": {
  "required": true,
  "custom": {
    "if": [
      {
        "and": [
          { "==": [{ "var": "scan_read" }, "elevated"] },
          { "all": [{ "var": "tracer_retention" }, { "==": [{ "var": "" }, "None"] }] }
        ]
      },
      false,
      true
    ]
  }
}
```

This pattern (checking another field's value in a custom validator) is typically a
workaround for missing conditional logic. Prefer adding `conditional` to the dependent
field instead.

### V2 `info` Type (Display Container Metadata)

Surfaces values from the container's metadata in a read-only display block:

```json
{
  "key": "scan_acquisition_info",
  "type": "info",
  "label": "1. Scan Acquisition",
  "values": [
    {
      "label": "1.1 Tracer type",
      "type": "Object",
      "value": [
        {
          "label": "Tracer",
          "containerType": "Acquisition",
          "field": "info.tracer",
          "type": "String"
        }
      ]
    }
  ]
}
```

---

### ⚠️ V2 Behavior: Hidden Fields Preserve Responses

In the V2 formio engine, when a field is hidden by conditional logic, its previously
entered value is **preserved in the draft and submitted response**. This is intentional
(a bug that cleared values was fixed in Core 17.3.0).

**Implication**: `response_data` may contain stale values for fields the reader changed
their mind about. When the reader changes an upstream answer that hides a downstream
branch, the old downstream answer persists.

**Workarounds:**
- Post-process `response_data` by walking the conditional logic and nulling out keys
  for fields that would be hidden given the final upstream values.
- Request a platform change to enable `clearOnHide` behavior.
- Add a "Clear / change my answer" option to upstream fields as a UI convention.

---

## V2 Viewer Config (separate JSON object)

The viewer config for V2 protocols is a separate JSON file (not embedded in the form):

```json
{
  "showStudyList": false,
  "evaluatePerformance": true,
  "enableSegmentationPanel": false,
  "toolbar": {
    "Annotate": { "except": ["Annotate"] },
    "Measure": { "except": ["Length", "Bidirectional", "Angle"] },
    "2D MPR": { "only": [] }
  },
  "hotkeys": [
    { "commandName": "incrementActiveViewport", "label": "Next Viewport", "keys": ["right"] },
    { "commandName": "decrementActiveViewport", "label": "Previous Viewport", "keys": ["left"] }
  ],
  "mouseActions": [
    { "toolName": "Zoom", "button": "middle" },
    { "toolName": "Pan", "button": "right" },
    { "toolName": "Wwwc", "button": "left" },
    { "toolName": "StackScrollMouseWheel", "button": "wheel" }
  ],
  "labels": [
    { "label": "Frontal", "value": "Frontal", "color": "rgba(255,0,0,0.5)" },
    { "label": "Parietal", "value": "Parietal", "color": "rgba(0,255,222,0.5)" }
  ],
  "overlay": {
    "topLeft": ["WL: {windowCenter:required} WW: {windowWidth:required}"],
    "topRight": ["{patientId}", "{patientName}"],
    "bottomLeft": ["Zoom: {zoomPercentage:required}%"],
    "bottomRight": ["{acquisitionDate}"]
  },
  "layouts": [
    {
      "name": "2x2 Orthogonal Layout",
      "selector": { "tag": "00080060", "match": "^M.*" },
      "type": "grid",
      "viewports": [ ... ]
    }
  ],
  "scaleIndicator": [
    { "scaleIndicator": { "type": "percent", "division": 25, "subdivision": 5, "showEndLinesValue": true } }
  ]
}
```

---

## Migrating V2 → V3

The Flywheel platform **does not support migrating existing V2 tasks, annotations, or
history to V3**. Migration means starting fresh:

1. Rewrite the form JSON using V3 `form.fields` format
2. Create a new ViewerConfig for `OHIF_V3`
3. Create a new Protocol pointing to the new form + viewer config
4. Create new tasks from the new protocol

Any existing completed V2 tasks and their data remain accessible in the old format.

Key translation notes:
- `studyForm.components[].values` → `form.fields[].options`
- `validate.required: true` → `requiredWhenVisible: true`
- `conditional.json` → `showWhen`
- `selectboxes` → `checkboxes`
- `info` type has no V3 equivalent — use a `paragraph` field instead, or pre-populate via container metadata display in viewer config
