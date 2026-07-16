---
type: Form Schema Reference
title: V2 Form Schema Reference (Legacy)
description: JSON schema for V2 (legacy) reader task forms using the formio studyForm.components structure rendered in the OHIF V2 viewer.
tags: [reader-tasks, v2, form-schema, formio]
timestamp: 2026-07-15T00:00:00Z
---

# V2 Form Schema Reference (Legacy — `studyForm.components`)

This document covers the JSON schema for V2 (legacy) reader task forms. These use the
**formio** schema and are rendered in the OHIF (V2) viewer. Identify V2 by the top-level
key `studyForm.components`.

---

## Top-Level Structure

```json
{
  "studyForm": {
    "components": [ /* formio component objects */ ]
  }
}
```

The viewer config is a **separate** JSON object — not embedded in the form.

---

## Component Object Properties

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

---

## Field Types

| `type` | Input style |
|--------|------------|
| `radio` | Single choice, radio buttons |
| `dropdown` | Single choice, dropdown |
| `selectboxes` | Multi-select checkboxes |
| `textfield` / `text` | Short free-text |
| `textarea` | Long free-text |
| `info` | Display-only block that surfaces container metadata |

---

## ⚠️ `required` Gotcha — THE Most Common V2 Bug

**In formio, `required: true` at the top level of a component is SILENTLY IGNORED.**

Required must always be inside `validate`:

```json
// WRONG — top-level required is ignored by formio
{
  "key": "consensus_read",
  "required": true,       // ← IGNORED! Reader can submit without answering
  "type": "radio"
}

// CORRECT — must be inside validate
{
  "key": "consensus_read",
  "validate": { "required": true },
  "type": "radio"
}
```

When auditing a V2 form, **always check for this pattern**. It is the single most common
bug in legacy reader task forms.

---

## Conditional Display (`conditional.json`)

Uses JSONLogic syntax wrapped in `conditional.json`. V2 typically uses loose equality (`==`).

```json
// Show when scan_read == "elevated"
"conditional": {
  "json": { "==": [{ "var": "scan_read" }, "elevated"] }
}

// Show when either value is set
"conditional": {
  "json": {
    "or": [
      { "==": [{ "var": "scan_read" }, "elevated"] },
      { "==": [{ "var": "scan_read" }, "non-elevated"] }
    ]
  }
}
```

---

## Cross-Field Validation (`validate.custom`)

Custom validators on a field can reference other field values using JSONLogic:

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
**workaround for missing conditional logic**. Prefer adding `conditional` to the dependent
field instead.

---

## `info` Type — Display Container Metadata

Surfaces values from the parent container's metadata in a read-only display block:

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

The `containerType` can be `Acquisition`, `Session`, or `Subject`. The `field` uses
dot-notation into the container's metadata (e.g., `info.tracer`, `info.SeriesDescription`).

This field type has **no V3 equivalent** — V3 uses `paragraph` for static text or
viewer overlays for metadata display.

---

## ⚠️ Hidden Fields Preserve Responses

In the V2 formio engine, when a field is hidden by conditional logic, its previously
entered value is **preserved in the draft and submitted response**. This is intentional
behavior (a bug that cleared values was fixed in Core 17.3.0).

**Implication**: `response_data` may contain stale values for fields where the reader
changed their mind about an upstream answer. When the reader changes an upstream answer
that hides a downstream branch, the old downstream answer persists.

**Workarounds:**

- Post-process `response_data` by walking the conditional logic and nulling out keys
  for fields that would be hidden given the final upstream values
- Request a platform change to enable `clearOnHide` behavior
- Add a "Clear / change my answer" option to upstream fields as a UI convention
- Migrate to V3 (same behavior, but fresh start means no accumulated stale data)

---

## Full V2 Example

```json
{
  "studyForm": {
    "components": [
      {
        "key": "scan_acquisition_info",
        "type": "info",
        "label": "1. Scan Acquisition Information",
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
      },
      {
        "key": "scan_read",
        "type": "radio",
        "label": "2.2 Based on tracer-specific guidelines, this scan is:",
        "validate": { "required": true },
        "values": [
          { "value": "elevated", "label": "Elevated" },
          { "value": "non-elevated", "label": "Non-Elevated" }
        ]
      },
      {
        "key": "tracer_retention",
        "type": "selectboxes",
        "label": "2.3 Indicate regions with cortical tracer retention:",
        "validate": { "required": true },
        "conditional": {
          "json": { "==": [{ "var": "scan_read" }, "elevated"] }
        },
        "values": [
          { "value": "Frontal", "label": "Frontal" },
          { "value": "Parietal", "label": "Parietal" },
          { "value": "Post Cingulate/Precuneus", "label": "Post Cingulate/Precuneus" },
          { "value": "Temporal", "label": "Temporal" },
          { "value": "Occipital", "label": "Occipital" }
        ]
      },
      {
        "key": "notes",
        "type": "textarea",
        "label": "3.1 Reader Notes",
        "validate": { "required": false }
      },
      {
        "key": "consensus_read",
        "type": "radio",
        "label": "4.1 Is a consensus review needed?",
        "validate": { "required": true },
        "values": [
          { "value": "yes", "label": "Yes" },
          { "value": "no", "label": "No" }
        ]
      },
      {
        "key": "final_read",
        "type": "radio",
        "label": "5.1 Is the read final and ready to return?",
        "validate": { "required": true },
        "showWhen": { "===": [{ "var": "consensus_read" }, "no"] },
        "values": [
          { "value": "yes", "label": "Yes, read is complete" },
          { "value": "no", "label": "No" }
        ]
      }
    ]
  }
}
```

---

## V2 Permissions

- **Task Admin**: Full CRUD on tasks, protocols, forms within assigned projects
- **Reader**: View assigned tasks, manage own annotations and form responses only
- Site admins inherit all task permissions; read-write users get limited access

## V2 Task ID Format

V2 tasks use a batch-based naming convention: `R-[BatchID]-[TaskNumber]`
(e.g., R-1-01, R-1-02, R-2-01). This differs from V3 which uses system-generated hex IDs.

## V2 Batch Limit

Up to 1,000 tasks per batch. Same API endpoint (`POST /api/readertasks/batch`) as V3.
