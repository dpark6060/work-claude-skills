---
name: fw-v2-reader-tasks
description: >
  Configure Flywheel V2 (legacy) reader task protocols — ohif_config.json, studyForm
  JSON, viewer settings, and form fields. Use this skill whenever working with V2 reader
  task forms, annotation labels, window/level presets, hotkeys, mouse actions, toolbar
  settings, layouts, overlays, or study form questions. Triggers on: V2 reader task,
  ohif_config, ohif_config.json, studyForm, studyForm.components, ViewerForm, formio,
  NTL, target lesion, annotation label, bSlices, hotkeys, mouseActions, toolbar, layout,
  hanging protocol, RECIST, window level preset, OHIF, V2 viewer, Viewer Protocol.
  Do NOT use for V3 reader tasks (Tasks Manager / OHIF_V3). Use fw-v3-reader-tasks for those.
---

# Flywheel OHIF V2 Viewer Configuration

Reference for authoring and editing `ohif_config.json` and `studyForm` JSON files
for the Flywheel OHIF V2 viewer.

---

## V2 Reader Task File Structure

V2 reader tasks use **two separate JSON files** uploaded independently:

| File | Purpose |
|---|---|
| `ohif_config.json` | Viewer-level settings: `labels`, `toolbar`, `hotkeys`, `mouseActions`, `layouts`, `overlays`, `wwwcPresets`, `studyFormWorkflow` |
| Study form JSON | The reader-facing form: `studyForm` (with `components` and optionally `subForms`). Also contains `labels` and `studyFormWorkflow` at root. |

**Do not merge these into a single file.** They are uploaded to separate fields in the reader task protocol. Never suggest combining them.

---

## Schema Version

The config supports V1 (`questions` key, deprecated) and V2 (`studyForm` key).
**Always use V2.** You cannot use both keys in the same config.

V2-only keys: `studyForm`, `bSlices`, `studyFormWorkflow`, `contourUnique`

---

## ohif_config.json — Key Root-Level Properties

| Property | Type | Notes |
|---|---|---|
| `labels` | array | Annotation labels available in the viewer |
| `toolbar` | object | Show/hide toolbar sections and tools |
| `wwwcPresets` | object | Window/level presets (keys "1"–"10") |
| `hotkeys` | array | **Replaces all defaults — include everything needed** |
| `mouseActions` | array | Map tools to left/right/middle/wheel |
| `studyForm` | object | The reader task form |
| `studyFormWorkflow` | string | "Form", "ROI", or "Mixed" |
| `bSlices` | object | Per-slice form responses |
| `contourUnique` | boolean | Prevent overlapping ROIs |
| `allowDraft` | boolean | Enable draft saves (default: true) |
| `timerOn` / `timerVisible` | boolean | Track/show study read time |
| `enableSegmentationPanel` | boolean | Show segmentation panel |
| `layouts` | array | Hanging protocols |
| `overlay` | object | Viewport text overlays |
| `scaleIndicator` | array | Scale bar configuration |
| `hideMeasurements` | boolean | Hide the measurement panel in single-task review mode |
| `sortByTriggerTime` | boolean | Set to `false` to disable trigger-time sorting of display sets |

**Multi-task override behavior:** When a session is opened with multiple simultaneous tasks,
the viewer forces `contourUnique: false`, `timerOn: false`, and `timerVisible: false`
regardless of what the config specifies. These three properties cannot be enabled in
multi-task mode.

### labels

Each label must be defined here for annotations to work. Readers cannot create labels on the fly.

```json
"labels": [
  {
    "label": "NTL-01",
    "value": "NTL-01",
    "color": "rgba(255, 0, 0, 0.2)"
  },
  {
    "label": "NTL-additional",
    "value": "NTL-additional"
  }
]
```

**Important:** Omit `"limit"` to allow unlimited annotations for a label.
Set `"limit": N` to cap annotations at N per study.

### wwwcPresets + hotkeys

Presets are numbered 1–10. Each preset maps to a `windowLevelPreset<N>` hotkey command.

```json
"wwwcPresets": {
  "1": { "description": "Soft Tissue", "window": "550", "level": "40" },
  "2": { "description": "Lung", "window": "1600", "level": "-600" }
}
```

**Hotkeys completely replace defaults — do not partially override.**
Always include the full set of hotkeys you want active.

```json
"hotkeys": [
  { "commandName": "windowLevelPreset1", "label": "Soft Tissue", "keys": ["1"] },
  { "commandName": "setActiveToolHotkey", "commandOptions": { "toolName": "Wwwc" }, "label": "W/L", "keys": ["w"] },
  { "commandName": "setActiveToolHotkey", "commandOptions": { "toolName": "Pan" }, "label": "Pan", "keys": ["p"] },
  { "commandName": "setActiveToolHotkey", "commandOptions": { "toolName": "Zoom" }, "label": "Zoom", "keys": ["z"] },
  { "commandName": "resetViewport", "label": "Reset", "keys": ["space"] },
  { "commandName": "performUndo", "label": "Undo", "keys": ["ctrl+z"] }
]
```

Supported `toolName` values for `setActiveToolHotkey`: `Wwwc`, `Pan`, `Zoom`, `Magnify`,
`StackScroll`, `Angle`. **`Crosshair` is not reliably supported via hotkeys** — assign it
via `mouseActions` instead.

### mouseActions

Valid buttons: `left`, `right`, `middle`, `wheel`.
On MacBook trackpad: `left` = click, `right` = two-finger click, `middle` = not accessible.

Valid tools: `Rotate`, `Pan`, `Zoom`, `StackScroll`, `Wwwc`, `Crosshair` (left only),
`StackScrollMouseWheel`, `ZoomMouseWheel`.

```json
"mouseActions": [
  { "toolName": "Wwwc", "button": "left" },
  { "toolName": "Pan", "button": "right" },
  { "toolName": "StackScrollMouseWheel", "button": "wheel" }
]
```

**Note:** There is no config property to make crosshairs visible by default on load —
this requires a viewer code change.

### toolbar

Trim available tools by category. Use `only` to allowlist or `except` to denylist.

```json
"toolbar": {
  "hideNavPanel": true,
  "Annotate": { "only": ["Length", "FreehandRoi"] },
  "Segment": { "only": [] },
  "Download": { "except": ["Download"] }
}
```

Categories: `Zoom`, `Annotate`, `Segment`, `Segmentation`, `Download`, `CINE`,
`Protocols`, `2D MPR`. Labels are case-sensitive.

---

## studyForm

The form uses a form.io-compatible schema with JSON Logic for conditionals.

```json
"studyForm": {
  "components": [ ...questions... ],
  "subForms": { ...optional named subforms... }
}
```

### Question properties

| Property | Required | Notes |
|---|---|---|
| `key` | yes | Unique ID, used in conditionals. No special chars except `-` and `_` |
| `label` | yes (except content type) | Display text |
| `type` | yes | See types below |
| `values` | yes for radio/selectboxes/info | Array of answer options |
| `validate` | no | `{ "required": true }` |
| `conditional` | no | JSON Logic object |
| `positiveAnswers` | no | Used with bSlices |
| `contourVisibility` | no | When `true`, controls contour visibility behavior when the reader switches between questions — hides contours for prior questions' annotations |

### Supported question types

| Type | Notes |
|---|---|
| `radio` | Radio buttons |
| `dropdown` | Dropdown select |
| `textarea` | Multi-line text |
| `textfield` | Single-line text (use instead of `number` — `number` type does not render) |
| `selectboxes` | Checkboxes — stores as array |
| `content` | HTML display only, use `html` key instead of `label` |
| `info` | Displays Flywheel container metadata |

### Conditional visibility (JSON Logic)

```json
"conditional": {
  "json": {
    "==": [ { "var": "some_question_key" }, "some_value" ]
  }
}
```

For OR conditions:
```json
"conditional": {
  "json": {
    "or": [
      { "==": [ { "var": "key" }, "val1" ] },
      { "==": [ { "var": "key" }, "val2" ] }
    ]
  }
}
```

`var` references another question's `key`. The value compared must match the answer
option's `value` field, not its `label`.

### Answer options (values array)

Each answer option can use either the **flat style** (simple cases) or the **instructionSet style** (multiple annotation groups per answer). Do not mix both styles on the same answer.

**Flat style properties:**

| Property | Notes |
|---|---|
| `value` | The stored answer value |
| `label` | Display text |
| `requireMeasurements` | Labels that must be annotated before this answer is valid |
| `measurementTools` | Enables specific tools when this answer is selected. All tools disabled until an answer with this property is selected. |
| `directive` | Inline instruction text shown to reader in the form panel |
| `instruction` | Help tooltip text shown when the reader hovers the info icon — use for longer guidance, distinct from `directive` |
| `subForm` | Name of a subForm to associate with each annotation drawn |

```json
"values": [
  {
    "value": "done",
    "label": "TL-01 annotated",
    "requireMeasurements": ["TL-01"],
    "measurementTools": ["Bidirectional", "FreehandRoi"],
    "directive": "Draw a bidirectional measurement on the target lesion.",
    "instruction": "The longest diameter and perpendicular short axis must both be measurable."
  }
]
```

---

## instructionSet

`instructionSet` is an advanced alternative to the flat `requireMeasurements`/`measurementTools` pattern. Use it when a single answer requires **multiple independent annotation groups**, each with its own labels, tools, and instructions — for example, "annotate a target lesion AND a reference organ separately."

Define `instructionSet` on an answer `value` object instead of (not alongside) flat `requireMeasurements`/`measurementTools`:

```json
"values": [
  {
    "value": "annotate",
    "label": "Annotate lesion and organ",
    "instructionSet": [
      {
        "requireMeasurements": ["TL-01"],
        "measurementTools": ["Bidirectional"],
        "directive": "Draw a bidirectional on the target lesion.",
        "instruction": "Measure along the longest axis."
      },
      {
        "requireMeasurements": ["REF-ORGAN"],
        "measurementTools": ["Length"],
        "directive": "Draw a length measurement on the reference organ."
      }
    ]
  }
]
```

### instructionSet item properties

| Property | Required | Notes |
|---|---|---|
| `requireMeasurements` | yes | Array of label values that must be annotated for this instruction |
| `measurementTools` | yes | Tools enabled for this instruction group |
| `directive` | no | Inline instruction text shown in the annotation row |
| `instruction` | no | Help tooltip text shown via the info icon |
| `exact` | no | Require exactly N annotations per label (e.g., `"exact": 2`) |
| `min` | no | Require at least N annotations per label |
| `max` | no | Allow at most N annotations per label |

### Range constraints (`exact`, `min`, `max`)

When `exact` or `max` is set, the viewer renders placeholder slots in the annotation list — readers fill them by drawing annotations. An "Add" button appears if `min`/`max` allows more than the default count.

- `exact: N` — reader must draw exactly N annotations per label
- `min: N` — reader must draw at least N; "Add" button appears up to the max
- `max: N` — upper bound; "Add" button is disabled once reached
- If none are set, the label's `limit` in the root `labels` array governs the cap

```json
{
  "requireMeasurements": ["TL-01", "TL-02"],
  "measurementTools": ["Bidirectional"],
  "directive": "Annotate both target lesions.",
  "exact": 1
}
```

This requires exactly 1 annotation per label (`TL-01` and `TL-02`).

### subForms

SubForms display additional questions for each individual annotation drawn when a specific answer is selected. They appear automatically in the Viewer Form panel when an annotation is created.

Define `subForms` as a sibling of `components` inside `studyForm`:

```json
"studyForm": {
  "components": [
    {
      "label": "Annotate lesions",
      "key": "meas_lesions",
      "type": "radio",
      "values": [
        {
          "value": "done",
          "label": "Start annotating",
          "requireMeasurements": ["TL"],
          "measurementTools": ["FreehandRoi"],
          "subForm": "lesion_details"
        }
      ]
    }
  ],
  "subForms": {
    "lesion_details": {
      "label": "Lesion details",
      "components": [
        {
          "label": "Side",
          "key": "side",
          "type": "radio",
          "values": [
            { "value": "left", "label": "Left" },
            { "value": "right", "label": "Right" }
          ]
        }
      ]
    }
  }
}
```

**subForm rules:**
- `subForms` is a key inside `studyForm`, not at root
- The `subForm` value on an answer must exactly match a key in `subForms`
- Each subForm definition **must** have a `"label"` field — omitting it prevents the subForm from rendering
- `studyFormWorkflow: "Form"` must be set (at root of the study form JSON file) for subForms to work
- SubForm components support the same question types as the main form, including conditionals
- The `requireMeasurements` value must match the `value` field of a label in the `labels` array (not the `label` field)

**Known limitation:** As of June 2026 on `sse-latest-azure`, subForms are confirmed to load correctly via the API but do not render in the viewer panel. This appears to be a viewer rendering bug — file with the Flywheel viewer engineering team if encountered.

**Critical:** When `measurementTools` is defined on any answer in the form, ALL annotation
tools are disabled by default. Tools only activate when the reader selects that answer.
Annotation questions must have at least one answer with `measurementTools` defined,
or no tools will be accessible.

### Supported measurementTools values

`Length`, `Parallel`, `ArrowAnnotate`, `Angle`, `Bidirectional`, `RectangleRoi`,
`CircleRoi`, `EllipticalRoi`, `FreehandRoi`, `OpenFreehandRoi`, `ContourRoi`

### Multiple annotations per label

To allow multiple annotations under a single label:
1. Define the label in the root `labels` array **without** a `limit` property
2. Use `requireMeasurements` with that label — it only validates that at least one exists

If annotations are capped unexpectedly, check whether the label has `"limit"` set in
the `labels` array — remove it to allow unlimited annotations.

---

## bSlices

Enables separate form responses per image slice. Not applicable when multiple series are open.

```json
"bSlices": {
  "settings": {
    "3": { "hiddenQuestions": ["q1"], "measurementTools": { "q2": ["Length"] } },
    "5": {}
  },
  "required": {
    "all": ["q1"],
    "any": ["q2"],
    "one": ["q3"],
    "specific": { "3": ["q4"] }
  }
}
```

---

## NIfTI Layouts

For NIfTI files, use `SeriesDescription` (not `ProtocolName`) to match series in viewports.
Omit the `selector` block — it uses DICOM modality tags that don't apply to NIfTI.
Use `type: "nifti"` (not `type: "2D"`) for all viewport type values — this ensures the
hanging protocol uses NIfTI-specific `orientation` matching instead of DICOM-style matching,
which avoids the "DICOM image could not be indexed" error.

**How series matching works for NIfTI:** The viewer registers an `orientation` custom attribute
for NIfTI files that maps directly to each file's `SeriesDescription` value. HP matching uses a
**contains** check — `"T1w"` would match a file whose SeriesDescription is `"T1w_MPR_axial"`.
If a viewport isn't matching when you expect it to, verify the actual SeriesDescription value
in the file matches (or is contained by) the string you specified.

**Default viewport layout (no `layouts` config):** When no `layouts` key is present, the
viewer automatically sets up `min(3, displaySets.length)` viewports for NIfTI files based
on how many display sets are loaded — not from any config value. A NIfTI file with 3 display
sets will render 3 viewports by default.

**ITK MetaImage files** (`.mha`/`.mhd`) are supported with the same layout rules as NIfTI.
Use `type: "metaimage"` for viewport type instead of `type: "nifti"`.

```json
"layouts": [
  {
    "name": "NIfTI Two Viewport",
    "type": "asymmetric",
    "viewports": [
      {
        "position": { "x": 0, "y": 0 },
        "size": { "width": 0.5, "height": 1 },
        "type": "nifti",
        "SeriesDescription": "T1w_MPR"
      },
      {
        "position": { "x": 0.5, "y": 0 },
        "size": { "width": 0.5, "height": 1 },
        "type": "nifti",
        "SeriesDescription": "T2w_SPC",
        "readOnly": true
      }
    ]
  }
]
```

For DICOM, use `ProtocolName` instead of `SeriesDescription`, and include a `selector`
block to match on modality tag `00080060`.

**Known limitation — NIfTI layouts in reader task context:** NIfTI side-by-side layouts
are non-functional in V2 reader tasks. The viewer redirects to only the first matched file
on open. The mechanism that would load the second file (`loadMissingStudies`) requires
previously saved `displayProperties` in the session — but those can only be written after a
successful open, which never happens because the error fires first. The result is an
unrecoverable error loop:

1. Task opens → "DICOM image could not be indexed" error → nothing is saved
2. Task re-opens → still no saved state → same error

Using `type: "nifti"` viewports (vs. `type: "2D"`) is still required to avoid a different
class of error, but does not fix the underlying issue. This requires a viewer-side fix:
`loadMissingStudies` (or equivalent) must be called during initial HP application for NIfTI
layouts, not only on session restore. File a bug with the Flywheel viewer engineering team
with this description if side-by-side NIfTI layouts are required.

---

## Scale Indicator

Configures the scale bar displayed in viewports.

```json
"scaleIndicator": [
  {
    "scaleIndicator": {
      "type": "percent",
      "division": 25,
      "subdivision": 5,
      "showEndLinesValue": true
    }
  }
]
```

**This feature is V2-only** — V3 does not support `scaleIndicator` configuration.

---

## Common Mistakes

- **Empty `values: []`** on an annotation question — tools won't activate, nothing works
- **Using `number` type** — does not render; use `textfield` instead
- **Defining `hotkeys` partially** — hotkeys replace all defaults; include everything needed
- **Label not in `labels` array** — readers cannot annotate with undefined labels
- **`limit` on a label when unlimited annotations needed** — remove `limit` to uncap
- **Using `questions` key instead of `studyForm`** — `questions` is V1 and deprecated
- **Using `ProtocolName` for NIfTI** — use `SeriesDescription` instead
- **Using `type: "2D"` for NIfTI layout viewports** — use `type: "nifti"` instead; `type: "2D"` uses DICOM-style matching and can cause "DICOM image could not be indexed" errors
- **Merging viewer config and study form into one file** — V2 reader tasks require two separate files; never combine them
- **Missing `"label"` on a subForm definition** — subForm will not render without it
- **Missing `studyFormWorkflow: "Form"`** — required for subForms to activate
- **`subForms` at root instead of inside `studyForm`** — must be nested inside `studyForm`
- **Mixing flat and instructionSet styles on the same answer** — use one or the other; combining them produces undefined behavior
- **Setting `exact`/`min`/`max` without `instructionSet`** — range constraints only apply inside `instructionSet` items
- **Malformed JSON** — always validate after editing:
  `python3 -c "import json; json.load(open('file.json'))"`

---

## Task Reference

### Task ID format

V2 tasks use a batch-based naming convention: `R-[BatchID]-[TaskNumber]`
(e.g., `R-1-01`, `R-1-02`, `R-2-01`). This differs from V3 which uses system-generated hex IDs.

### Batch limit

Up to 1,000 tasks per batch (`POST /api/readertasks/batch`). Split larger workloads into multiple batch calls.
