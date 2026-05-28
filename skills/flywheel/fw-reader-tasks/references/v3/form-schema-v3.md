# V3 Form Schema Reference (Tasks Manager — `form.fields`)

This document covers the JSON schema for V3 reader task forms used with the Tasks Manager
and OHIF_V3 viewer. Identify V3 by the top-level key `form.fields`.

---

## Top-Level Structure

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

## Field Object Properties

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

---

## Field Types

| `type` | Input style | `options` needed? |
|--------|------------|-------------------|
| `radio` | Single choice, radio buttons | Yes |
| `dropdown` / `select` | Single choice, dropdown | Yes |
| `checkboxes` | Multi-select checkboxes | Yes |
| `textfield` / `text` | Short free-text | No |
| `textarea` | Long free-text | No |
| `paragraph` | Display-only text (no input) | No |
| `instructions` | Guidance text (can be conditional) | No |

---

## Conditional Display (`showWhen`)

Uses JSONLogic syntax. The field is shown when the condition evaluates to true.

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

**V3 uses strict equality (`===`) by convention.** This differs from V2 which uses `==`.

### Behavior Notes

- Fields hidden by conditional logic are not shown in the UI
- `requiredWhenVisible: true` means only required when the field IS visible
- The system supports sequential conditional chains (Q2 depends on Q1, Q3 depends on Q2)
- **Hidden field values are preserved** — when a reader changes an upstream answer that hides
  a downstream field, the old downstream answer persists in `response_data`. This is intentional
  (a bug that cleared values was fixed in Core 17.3.0).

---

## Validation

JSONLogic syntax in a `validation` array with `logic` and `message` properties:

```json
{
  "key": "score",
  "type": "textfield",
  "label": "Centiloid Score",
  "validation": [{
    "logic": {
      "and": [
        { ">=": [{ "var": "score" }, 0] },
        { "<=": [{ "var": "score" }, 500] }
      ]
    },
    "message": "Value must be between 0 and 500"
  }]
}
```

---

## E-Signature Configuration

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

---

## Completion Tags

Auto-apply Data Tags to the parent container when a task is completed:

```json
"completion_tags": ["read-complete", "site-a-reviewed"]
```

---

## Full V3 Example

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

## Creating a V3 Form via API

```python
form = fw.post("/api/forms", json={
    "viewer": "OHIF_V3",
    "parent": {"type": "project", "id": project_id},
    "form": {
        "title": "My Study Form",
        "description": "...",
        "defaults": {},
        "fields": [ ... ]
    }
})
form_id = form._id
```
