---
type: Config Reference
title: bSlices Reference
description: The bSlices config that enables separate form responses per image slice in single-series DICOM V2 reader tasks, plus its limitations.
tags: [reader-tasks, v2, bslices, dicom]
timestamp: 2026-07-15T00:00:00Z
---

# bSlices Reference

> **Before generating any bSlices config, confirm: is this a single-series DICOM task?**
> If the answer is no — NIfTI, MHD, multi-series DICOM, or unknown — state clearly that
> bSlices will not work and explain why before proceeding.

bSlices enables separate form responses per image slice. Instead of one answer set for the
whole study, the reader answers questions independently for each configured slice as they
scroll through the series.

**Only applicable to single-series DICOM tasks.** bSlices is silently disabled (no error,
no warning — the form simply shows on every slice) when:
- The file is NIfTI or ITK MetaImage (non-DICOM)
- More than one display set is loaded (multi-series DICOM or multi-plane NIfTI)

## settings

The `settings` object defines which slices are active. **Keys are slice numbers as strings.**
Only slices listed here show the form — all other slices render no questions at all. The set
of keys in `settings` is also the authoritative slice list used by all `required` validation.

Each slice entry can have:

| Property | Type | Notes |
|---|---|---|
| `hiddenQuestions` | array of strings | Question keys to suppress on this slice only |
| `measurementTools` | object | Per-question tool overrides for this slice: `{ "question_key": ["FreehandRoi"] }` |

An empty object `{}` for a slice entry is valid — it makes that slice active with no overrides
(all questions shown, tools from the form definition).

## required

Controls submit-time validation across slices. All four modes can be combined.

| Mode | Behavior |
|---|---|
| `all` | Question must be answered on **every** configured slice |
| `any` | Question must be answered on **at least one** slice |
| `one` | Question must be answered on **exactly one** slice; once answered on any slice, it is hidden on all others |
| `specific` | Question required only on the listed slice numbers: `{ "3": ["q_key"] }` |

## positiveAnswers

A property on a **question** (not inside `bSlices`), listing which answer values count as
"answered" for bSlices required validation. If absent, any answered value satisfies
`all`/`any`/`one`. If present, only those specific values count — all other answers are
treated as unanswered for validation purposes.

```json
{
  "key": "finding",
  "type": "radio",
  "label": "Finding",
  "positiveAnswers": ["abnormal", "indeterminate"],
  "values": [
    { "value": "normal", "label": "Normal" },
    { "value": "abnormal", "label": "Abnormal" },
    { "value": "indeterminate", "label": "Indeterminate" }
  ]
}
```

In this example, a reader who answers "Normal" on a slice does not satisfy `required.all` —
only "Abnormal" or "Indeterminate" count.

## Full example

```json
"bSlices": {
  "settings": {
    "3": {
      "hiddenQuestions": ["severity"],
      "measurementTools": { "finding": ["FreehandRoi"] }
    },
    "7": {},
    "12": {
      "hiddenQuestions": []
    }
  },
  "required": {
    "all": ["finding"],
    "any": ["severity"],
    "one": ["global_note"],
    "specific": { "7": ["extra_q"] }
  }
}
```

Slices 3, 7, and 12 are active. `finding` must be answered on all three. `severity` must be
answered on at least one. `global_note` must be answered on exactly one (hidden elsewhere once
answered). `extra_q` is only required on slice 7. On slice 3, `severity` is hidden and
`FreehandRoi` is the only tool for the `finding` question.
