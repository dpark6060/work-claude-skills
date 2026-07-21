---
name: fw-v3-reader-tasks
description: >
  Configure Flywheel V3 reader task protocols — form fields, conditional logic,
  validation, workflows, and e-signature. Use this skill whenever working with
  V3 reader task protocols, CustomForm, CustomField, field types, JSON Logic
  visibility or validation rules, adjudication workflows, e-signature config,
  protocol status, or task lifecycle in the V3 OHIF viewer. Triggers on:
  V3 reader task, protocol, CustomForm, CustomField, form fields, field type,
  requiredWhenVisible, visible logic, JSON Logic, adjudication, esignature,
  single workflow, completion_tags, viewer_config, labels, labelOnMeasure,
  fileBrowser, ohif_configv3.json, protocol editor.
  Do NOT use this skill for the V2 OHIF viewer (ohif_config.json / studyForm).
---

# Flywheel V3 Reader Task — Protocol & Form Configuration

Reference for authoring V3 reader task protocols.

---

## How Protocols Are Created

Protocols are created in the Flywheel UI via a **Create New Protocol** dialog, which sets three fields directly:

| Field | Notes |
|---|---|
| **Name** (`label`) | 2–32 characters |
| **Type** (`task_type`) | Currently `"read"` is the only available type |
| **Notes** (`notes`) | Optional, max 250 characters |

Once created, the protocol is edited in the **UI protocol editor**, which works with a JSON config containing:

| Field | Notes |
|---|---|
| `form` | Optional — the reader-facing form |
| `viewer_config` | Optional — V3 viewer settings (separate skill) |
| `esignature_config` | Optional — e-signature requirements |
| `completion_tags` | Tags applied to container on task completion |
| `workflow` | Optional — single or adjudication |

`label`, `task_type`, and `group_id` are set at creation time (UI dialog or API) and are not edited in the JSON editor.

`protocol_config` **is** editable in the JSON editor, but it exists almost entirely as the wrapper for `viewer_config` — that is the only field inside it that does anything. See the note below on `longitudinal`.

### `longitudinal` / `protocol_config` — set but inert (verified against source, 2026-07)

`protocol_config` holds `{ adjudication, longitudinal, viewer_config }`. Two of those three are traps:

- **`longitudinal` is a required boolean that is not wired to any behavior.** Traced across every Flywheel repo: it is defined and persisted in `core-api` (`core/workflows/protocols/_models.py:172`), mirrored as a TypeScript type in `fw-ohif-v3` (`protocols.ts`), required-present by the Monaco editor's JSON schema (`monaco-editor` `app.component.ts:~520-589`), and **hardcoded to `false`** by the main web app on protocol creation (`frontend` `group-protocols.component.ts:~395`). No code anywhere reads its value to change what loads, what a task spans, or how a read behaves. Every read path deliberately destructures around it to pull out `viewer_config`. Do not expect setting `longitudinal: true` to do anything.
- **What actually sets a task's container level is `parent_ref` at task-creation time**, not `longitudinal`. Tasks are created with `parent_ref: { type, id }` plus a `parents` block. The valid `type` values are restricted to **`session`, `acquisition`, or `file`** — there is **no subject-level or project-level reader task** (`core-api` `core/models/reader_tasks.py`: `VALID_TASK_PARENT_CONTAINER_TYPES = (session, acquisition, file)`; a bad type returns 422). Session is therefore the coarsest scope; one task cannot span a subject / multiple sessions. Cross-session comparison must be handled by curating the data into a single session upstream, not by task scope.
- The MR history confirms intent: every `protocol_config` MR (FLYW-32530, FLYW-33421, FLYW-42267) was about surfacing `viewer_config`; none touched `longitudinal` as a feature.

**Practical takeaway:** the only lever that changes cross-session visibility in the viewer is `viewer_config.fileBrowser` (see the viewer config reference). `longitudinal` is not a substitute and is currently a no-op.

---

## CustomForm

The form displayed to the reader inside the viewer panel.

```json
"form": {
  "title": "Radiology Read",
  "description": "Complete all questions for this study.",
  "defaults": {
    "finding": "",
    "severity": "",
    "confirmed": false
  },
  "fields": [ ...CustomField objects... ]
}
```

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `description` | string | Required |
| `defaults` | object | Required — key/value defaults for every field. Empty string for text, `false` for switch, `[]` for checkbox, `""` for select/radio. |
| `fields` | array | Required — ordered list of CustomField objects |

**`defaults` must include a key for every non-display field.** Missing defaults cause unpredictable form state.

---

## CustomField

Each element in `fields` is a CustomField:

| Field | JSON key | Type | Notes |
|---|---|---|---|
| `type` | `type` | FieldType | Required — see types below |
| `key` | `key` | string | Required — unique ID, used in conditionals |
| `label` | `label` | string | Display label. Not used by `paragraph`/`instruction` (use directly) |
| `description` | `description` | string | Optional subtext below the label. Optional in the API; **must be present** in the UI protocol editor (use `""` or `null` if not needed). |
| `placeholder` | `placeholder` | string | Input placeholder text. Optional in the API; **must be present** in the UI protocol editor (use `null` if not needed). |
| `helperText` | `helperText` | string | Helper text shown under the input. Optional in the API; **must be present** in the UI protocol editor (use `""` or `null` if not needed). |
| `visible` | `visible` | bool or array | JSON Logic array for conditional visibility |
| `requiredWhenVisible` | `requiredWhenVisible` | bool or array | `true`, `false`, or JSON Logic array |
| `validation` | `validation` | array | List of `{logic, message}` validation rules |
| `options` | `options` | array | Required for `select`, `radio`, `checkbox` — list of `{value, label?}` |

### Field Types

| `type` value | Renders as | Stores | Notes |
|---|---|---|---|
| `text` | Single-line text input | string | |
| `text-area` | Multi-line textarea | string | 3–7 rows |
| `int` | Integer number input | number | Native arrows |
| `float` | Float number input | number | No arrows |
| `date` | Date picker input | string | HTML date format (YYYY-MM-DD) |
| `select` | Dropdown | string | Requires `options` |
| `radio` | Radio button group | string | Requires `options`. Allows deselect. |
| `checkbox` | Checkbox group | array | Requires `options`. Stores selected values as array. |
| `switch` | Toggle switch | boolean | |
| `paragraph` | Section heading | — | Display only. Uses `label` + `description`. No data stored. |
| `instruction` | Info/callout box | — | Display only. Styled blue box. Uses `label` + `description`. No data stored. |
| `phone` | *(not rendered)* | — | Defined in schema but not implemented in the UI. Do not use. |

**`paragraph`** renders as a form section heading — use it to visually group related fields.

**`instruction`** renders as a styled informational callout — use it for directions or warnings to the reader.

### Options (for select, radio, checkbox)

```json
"options": [
  { "value": "yes", "label": "Yes" },
  { "value": "no", "label": "No" },
  { "value": "na" }
]
```

`label` is optional — if omitted, `value` is displayed.

---

## JSON Logic — Conditional Visibility

The `visible` field controls whether a field is shown. It accepts:
- `true` or `false` (always visible / always hidden)
- An **array** of JSON Logic rules — rules are **OR'd** together

```json
"visible": [
  { "==": [ { "var": "finding" }, "abnormal" ] }
]
```

When a field is hidden, the renderer assigns its **default** back into form state (verified against source + tested, 2026-07): `FormLayout.tsx` `updateHidden()` runs `form.state.values[key] = defaults[key]`. Tested behavior:
- **Concrete default set** → the reader's entered value is overwritten with the default when the field is hidden (and stays overwritten when re-shown).
- **Null / empty / absent default** → the entered value persists (the assignment doesn't clobber).

So a field's `default` doubles as its **on-hide reset value**. Set a concrete default only when you *want* a hidden field cleared/reset to it. For data-entry fields whose values must survive a hide→re-show (e.g. gated measurement fields), leave the default `null`/empty.

### OR logic (show if any condition matches)

```json
"visible": [
  { "==": [ { "var": "finding" }, "abnormal" ] },
  { "==": [ { "var": "finding" }, "indeterminate" ] }
]
```

### AND logic (show only if all conditions match)

Wrap in a single rule using `"and"`:

```json
"visible": [
  {
    "and": [
      { "==": [ { "var": "finding" }, "abnormal" ] },
      { "==": [ { "var": "severity" }, "high" ] }
    ]
  }
]
```

### Length check

A custom `length` operation is available:

```json
"visible": [
  { ">": [ { "length": [ { "var": "notes" } ] }, 0 ] }
]
```

### `var` references

`var` references the `key` of another field in the same form. For `checkbox` fields (which store arrays), use `in`:

```json
"visible": [
  { "in": [ "option_value", { "var": "checkbox_field_key" } ] }
]
```

---

## JSON Logic — Required When Visible

`requiredWhenVisible` accepts:
- `true` — always required when the field is visible
- `false` — never required (default)
- An **array** of JSON Logic rules — OR'd together (same syntax as `visible`)

```json
"requiredWhenVisible": true
```

```json
"requiredWhenVisible": [
  { "==": [ { "var": "finding" }, "abnormal" ] }
]
```

When required and the field is empty, the form shows: **"This is a required question."**

Type-specific empty checks:
- `string`: empty string or whitespace-only
- `number`: null/undefined (0 is valid)
- `array`: empty array
- `boolean`: never triggers required error

---

## JSON Logic — Field Validation

`validation` is a list of rules applied after required-check. Each rule:

```json
"validation": [
  {
    "logic": { "<=": [ { "var": "score" }, 10 ] },
    "message": "Score must be 10 or less."
  },
  {
    "logic": { ">=": [ { "var": "score" }, 0 ] },
    "message": "Score must be 0 or greater."
  }
]
```

- `logic`: JSON Logic expression applied against all form values. Must return truthy for the field to be valid.
- `message`: Error message shown when the rule fails.

Validation only runs when the field is visible and either required or non-empty.

### Numeric range (int / float fields)

```json
"validation": [
  { "logic": { ">=": [ { "var": "score" }, 0 ] }, "message": "Score must be 0 or greater." },
  { "logic": { "<=": [ { "var": "score" }, 10 ] }, "message": "Score must be 10 or less." }
]
```

### Text format validation (text fields)

**JSON Logic has no regex support.** For `text` fields with a required format, combine `length`, `substr`, and `in` to approximate structural validation:

- **`length`** — check total character count
- **`substr`** — check a character at a specific position: `{"substr": [{"var": "field_key"}, startIndex, length]}`
- **`in`** — check that a value is one of a known set: `{"in": [valueToCheck, ["allowed","values"]]}`

You cannot validate that characters are numeric or match a character class.

Example — field with a fixed-length code containing a delimiter at a known position:

```json
"validation": [
  {
    "logic": { "==": [ { "length": [ { "var": "code_field" } ] }, 8 ] },
    "message": "Code must be 8 characters."
  },
  {
    "logic": { "==": [ { "substr": [ { "var": "code_field" }, 4, 1 ] }, "-" ] },
    "message": "Code must contain a hyphen at position 5 (e.g. XXXX-XXX)."
  }
]
```

Example — field where a substring must be from a known set:

```json
"validation": [
  {
    "logic": { "in": [ { "substr": [ { "var": "code_field" }, 0, 3 ] }, ["AAA","BBB","CCC"] ] },
    "message": "Code must begin with a valid 3-letter prefix."
  }
]
```

`review_date` validation only runs when the field is non-empty (since `requiredWhenVisible` is `false`), so there is no risk of spurious errors on an unfilled optional field.

---

## Workflow Configuration

### Single read (default)

```json
"workflow": {
  "type": "single"
}
```

### Adjudication (double-read)

```json
"workflow": {
  "type": "adjudication",
  "read_count": 2,
  "trigger_fields": [
    { "key": "finding", "threshold": null }
  ],
  "form": null
}
```

| Field | Notes |
|---|---|
| `read_count` | Minimum 2 |
| `trigger_fields` | List of `{key, threshold?}` — field keys whose disagreement triggers adjudication |
| `form` | Optional separate `CustomForm` shown to the adjudicator |

#### Adjudication task states

When a task has an adjudication decision, `task.adjudication.decision` is one of:
- `own_read` — reader sees their own data, form is editable
- `reader_1` / `reader_2` — adjudicator reviewing a specific reader's read; form is **read-only**

When decision is `reader_1` or `reader_2`, measurements are **not re-saved** on submit.

---

## E-Signature Configuration

```json
"esignature_config": {
  "required": true,
  "reasons": [
    "Clinically reviewed",
    "Technically reviewed"
  ]
}
```

- **`esignature_config` must always be present** in the editor JSON — omitting it entirely causes a validation error. Use `null` when e-signatures are not needed.
- `reasons` is **required** when `required: true` — cannot be empty
- When e-signature is required, the submit dialog prompts for MFA code + reason selection
- MFA channels: `sms`, `call`, `totp`
- Resend cooldown: 60 seconds

---

## Task Lifecycle

| Status | Form state | Notes |
|---|---|---|
| `todo` | Unassigned | Reader can "Assign to me" before starting |
| `in_progress` | Editable | Set automatically on first Save Draft |
| `completed` | Disabled (read-only) | Set on successful submit |
| `cancelled` | Disabled | Form cannot be edited |

Tasks cannot skip directly from `todo` to `completed` — a task must be opened (transition to `in_progress`) before it can be submitted.

Save Draft saves form values and measurements without submitting.
Submit validates all fields, then shows a confirmation dialog (basic or MFA).

---

## Complete Example — Editor JSON

This is the shape of the JSON edited in the UI protocol editor (not the full API object):

```json
{
  "completion_tags": ["reviewed"],
  "workflow": {
    "type": "single"
  },
  "esignature_config": null,
  "viewer_config": {},
  "form": {
    "title": "Chest CT",
    "description": "Review the chest CT and complete all required fields.",
    "defaults": {
      "finding": "",
      "severity": "",
      "notes": ""
    },
    "fields": [
      {
        "type": "paragraph",
        "key": "section_findings",
        "label": "Findings",
        "description": "Characterize the primary finding.",
        "placeholder": null,
        "helperText": null
      },
      {
        "type": "radio",
        "key": "finding",
        "label": "Primary finding",
        "description": null,
        "placeholder": null,
        "helperText": null,
        "requiredWhenVisible": true,
        "options": [
          { "value": "normal", "label": "Normal" },
          { "value": "abnormal", "label": "Abnormal" },
          { "value": "indeterminate", "label": "Indeterminate" }
        ]
      },
      {
        "type": "select",
        "key": "severity",
        "label": "Severity",
        "description": null,
        "placeholder": null,
        "helperText": null,
        "requiredWhenVisible": true,
        "visible": [
          { "==": [ { "var": "finding" }, "abnormal" ] }
        ],
        "options": [
          { "value": "mild", "label": "Mild" },
          { "value": "moderate", "label": "Moderate" },
          { "value": "severe", "label": "Severe" }
        ]
      },
      {
        "type": "text-area",
        "key": "notes",
        "label": "Notes",
        "description": null,
        "placeholder": "Enter additional observations...",
        "helperText": null,
        "requiredWhenVisible": false
      }
    ]
  }
}
```

---

## Viewer Configuration

`viewer_config` is a top-level key in the editor JSON. Pass `{}` when no viewer configuration is needed. Available options:

- **`labels`** — annotation label list shown when measuring: `items` (array of `{value, label, color?}`), `labelOnMeasure` (boolean, auto-prompt on create), `exclusive` (boolean, disallow custom labels).
- **`fileBrowser`** — `enabled` (boolean, default `true` for non-task; **default `false` for task protocols** — must explicitly set `true` to enable), `scope` (`"subject"` or `"session"`).

If the user's question involves viewer configuration in depth, read the additional reference file before responding: `~/.claude/skills/fw-v3-reader-tasks/references/viewer_config.md`

---

## SDK / Programmatic Access

If the user's question involves querying, listing, or filtering reader tasks via the Flywheel Python SDK or API, read the additional reference file before responding: `~/.claude/skills/fw-v3-reader-tasks/references/sdk.md`

Do not load this file for questions about protocol authoring, form fields, or configuration.

---

## Common Mistakes

- **Missing `description`, `placeholder`, or `helperText` on a field** — optional at the API level, but the UI protocol editor flags their absence as errors. Always include all three on every field; use `""` or `null` when the value isn't needed.
- **Missing key in `defaults`** — every non-display field needs a default. Missing defaults cause unpredictable form state on re-open.
- **Using `phone` type** — defined in schema but not rendered in the UI; use `text` instead.
- **`visible: true` (bare boolean)** — valid but rarely needed; omitting `visible` entirely has the same effect.
- **Not realizing `defaults` double as on-hide reset values** — hiding a field writes its default back over the entered value. A concrete default overwrites reader input on hide; a null/empty default preserves it. Only set concrete defaults on fields you want wiped/reset when hidden.
- **Empty `options` array** for select/radio/checkbox — the field renders but has nothing to pick.
- **`requiredWhenVisible: [...]` with AND logic** — wrap in a single `"and"` rule; the array is OR'd.
- **`validation` logic that references a missing key** — `var` on an undefined key returns `null`; test your logic carefully.
- **Adjudication `form` left as `{}` instead of `null`** — pass `null` or a valid `CustomForm`, not an empty object.
- **`reasons: []` when `esignature_config.required: true`** — the API rejects this; reasons list must be non-empty.
- **Including `label`, `group_id`, `task_type`, or `protocol_config` in the editor JSON** — these are set via the UI at creation time and are not part of the editor config. The editor JSON contains `form`, `viewer_config`, `esignature_config`, `completion_tags`, and `workflow` only.
