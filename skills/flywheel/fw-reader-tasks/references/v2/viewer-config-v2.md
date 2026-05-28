# V2 Viewer Configuration Reference (Legacy OHIF Viewer)

The V2 viewer config is a **separate JSON file** uploaded alongside the form when creating
a Viewer Protocol. It controls the OHIF (V2) image viewer's appearance and behavior.

---

## Creating via UI

1. Project Settings → Viewer Protocols → Create a New Viewer Protocol
2. Upload "Viewer Form File" (the `studyForm` JSON)
3. Upload "Viewer Configuration" (this config JSON)
4. Enter protocol name and description
5. Save

## Creating via API

```python
vc = fw.post("/api/viewerconfigs", json={
    "name": "pet-read-viewer",
    "viewer": "OHIF",       # Note: "OHIF" not "OHIF_V3"
    "config": { ... }
})
viewer_config_id = vc._id
```

---

## Full Configuration Structure

```json
{
  "showStudyList": false,
  "evaluatePerformance": true,
  "enableSegmentationPanel": false,
  "allowDraft": true,
  "timerOn": true,
  "timerVisible": true,

  "toolbar": {
    "Annotate": { "except": ["Annotate"] },
    "ROI": { "except": ["EllipticalRoi", "RectangleRoi", "FreehandRoi"] },
    "Measure": { "except": ["Length", "Bidirectional", "Angle"] },
    "CINE": { "only": [] },
    "Protocols": { "only": [] },
    "2D MPR": { "only": [] },
    "Segment": { "only": [] },
    "Segmentation": { "only": [] },
    "Download": { "only": [] }
  },

  "hotkeys": [
    { "commandName": "incrementActiveViewport", "label": "Next Viewport", "keys": ["right"] },
    { "commandName": "decrementActiveViewport", "label": "Previous Viewport", "keys": ["left"] },
    { "commandName": "nextImage", "label": "Next Image", "keys": ["down"] },
    { "commandName": "previousImage", "label": "Previous Image", "keys": ["up"] }
  ],

  "mouseActions": [
    { "toolName": "Zoom", "button": "middle" },
    { "toolName": "Pan", "button": "right" },
    { "toolName": "Wwwc", "button": "left" },
    { "toolName": "StackScrollMouseWheel", "button": "wheel" }
  ],

  "labels": [
    { "label": "Frontal", "value": "Frontal", "color": "rgba(255,0,0,0.5)" },
    { "label": "Parietal", "value": "Parietal", "color": "rgba(0,255,222,0.5)" },
    { "label": "Post Cingulate/Precuneus", "value": "Post Cingulate/Precuneus", "color": "rgba(0,0,255,0.5)" },
    { "label": "Temporal", "value": "Temporal", "color": "rgba(255,255,0,0.5)" },
    { "label": "Occipital", "value": "Occipital", "color": "rgba(255,0,255,0.5)" },
    { "label": "Lesion", "value": "Lesion", "color": "rgba(255,128,0,0.5)" }
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
      "viewports": [
        { "series": 0, "plane": "axial" },
        { "series": 0, "plane": "sagittal" },
        { "series": 0, "plane": "coronal" },
        { "series": 1, "plane": "axial" }
      ]
    }
  ],

  "scaleIndicator": [
    {
      "scaleIndicator": {
        "type": "percent",
        "division": 25,
        "subdivision": 5,
        "showEndLinesValue": true
      }
    }
  ],

  "smartCTRanges": {
    "Lung": { "min": -1000, "max": -500, "color": "rgba(0,255,0,0.3)" },
    "Tumor": { "min": 20, "max": 80, "color": "rgba(255,0,0,0.3)" },
    "Malignant Lymphnode": { "min": 10, "max": 40, "color": "rgba(255,255,0,0.3)" }
  }
}
```

---

## Section Details

### Toolbar

Controls which viewer tools are available. Use `"except"` to hide specific tools, or
`"only": []` to hide an entire tool group.

```json
"toolbar": {
  "Annotate": { "except": ["Annotate"] },     // hide annotation tool
  "Measure": { "except": ["Length"] },          // hide length measurement
  "2D MPR": { "only": [] }                      // hide entire MPR section
}
```

### Hotkeys

Map keyboard shortcuts to viewer commands:

```json
"hotkeys": [
  { "commandName": "incrementActiveViewport", "label": "Next Viewport", "keys": ["right"] },
  { "commandName": "nextImage", "label": "Next Image", "keys": ["down"] }
]
```

### Mouse Actions

Map mouse buttons to viewer tools:

```json
"mouseActions": [
  { "toolName": "Zoom", "button": "middle" },
  { "toolName": "Pan", "button": "right" },
  { "toolName": "Wwwc", "button": "left" },
  { "toolName": "StackScrollMouseWheel", "button": "wheel" }
]
```

### Annotation Labels

Define custom labels for annotations. These appear in the label picker when drawing ROIs:

```json
"labels": [
  { "label": "Frontal", "value": "Frontal", "color": "rgba(255,0,0,0.5)" }
]
```

### Viewport Overlays (V2 only)

Text overlays in the four corners of each viewport. Uses DICOM tag placeholders:

```json
"overlay": {
  "topLeft": ["WL: {windowCenter:required} WW: {windowWidth:required}"],
  "topRight": ["{patientId}", "{patientName}"],
  "bottomLeft": ["Zoom: {zoomPercentage:required}%"],
  "bottomRight": ["{acquisitionDate}"]
}
```

**This feature is V2-only** — V3 does not support custom overlay text.

### Hanging Protocols / Layouts (V2 only)

Define viewport arrangements and series assignments:

```json
"layouts": [
  {
    "name": "2x2 Orthogonal Layout",
    "selector": { "tag": "00080060", "match": "^M.*" },
    "type": "grid",
    "viewports": [
      { "series": 0, "plane": "axial" },
      { "series": 0, "plane": "sagittal" },
      { "series": 0, "plane": "coronal" },
      { "series": 1, "plane": "axial" }
    ]
  }
]
```

The `selector` uses DICOM tags to auto-match series. The `match` field is a regex.

### Scale Indicator (V2 only)

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

---

## V2-Only Features (Not Available in V3)

- `overlay` — custom text overlays in viewport corners
- `layouts` — hanging protocol / viewport arrangement definitions
- `scaleIndicator` — scale bar configuration
- `hotkeys` — custom keyboard shortcuts (V3 has different hotkey handling)
- `evaluatePerformance` — performance monitoring toggle

## Features Available in Both V2 and V3

- `mouseActions` — mouse button to tool mapping
- `labels` — annotation label definitions with colors
- `smartCTRanges` — predefined windowing presets
- `showStudyList`, `allowDraft`, `timerOn` — general settings
