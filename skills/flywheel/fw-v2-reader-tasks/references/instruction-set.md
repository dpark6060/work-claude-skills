# instructionSet Reference

`instructionSet` is an advanced alternative to the flat `requireMeasurements`/`measurementTools`
pattern. Use it when a single answer requires **multiple independent annotation groups**, each
with its own labels, tools, and instructions — for example, "annotate a target lesion AND a
reference organ separately."

Define `instructionSet` on an answer `value` object instead of (not alongside) flat
`requireMeasurements`/`measurementTools`:

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

## instructionSet item properties

| Property | Required | Notes |
|---|---|---|
| `requireMeasurements` | yes | Array of label values that must be annotated for this instruction |
| `measurementTools` | yes | Tools enabled for this instruction group |
| `directive` | no | Inline instruction text shown in the annotation row |
| `instruction` | no | Help tooltip text shown via the info icon |
| `exact` | no | Require exactly N annotations per label (e.g., `"exact": 2`) |
| `min` | no | Require at least N annotations per label |
| `max` | no | Allow at most N annotations per label |

## Range constraints (`exact`, `min`, `max`)

When `exact` or `max` is set, the viewer renders placeholder slots in the annotation list —
readers fill them by drawing annotations. An "Add" button appears if `min`/`max` allows more
than the default count.

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

## subForms

SubForms display additional questions for each individual annotation drawn when a specific
answer is selected. They appear automatically in the Viewer Form panel when an annotation
is created.

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

**Known limitation:** As of June 2026 on `sse-latest-azure`, subForms are confirmed to load
correctly via the API but do not render in the viewer panel. This appears to be a viewer
rendering bug — file with the Flywheel viewer engineering team if encountered.
