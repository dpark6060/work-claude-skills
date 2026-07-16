---
type: Viewer Config Reference
title: V3 Viewer Configuration Reference (OHIF_V3)
description: The V3 viewer config controlling the OHIF_V3 image viewer, embedded in protocol JSON or created as a standalone ViewerConfig object.
tags: [reader-tasks, v3, viewer-config, ohif]
timestamp: 2026-07-15T00:00:00Z
---

# V3 Viewer Configuration Reference (OHIF_V3)

The V3 viewer config controls the OHIF_V3 image viewer appearance and behavior. It can be
embedded in the protocol JSON as `viewer_config`, or created as a standalone ViewerConfig
object via `/api/viewerconfigs`.

---

## Embedding in Protocol JSON

When creating a protocol via the Tasks Manager UI, the viewer config is part of the
protocol JSON:

```json
{
  "form": { ... },
  "esignature_config": null,
  "viewer_config": {
    "labels": [ ... ],
    "fileBrowser": { "enabled": true, "scope": "session" }
  }
}
```

## Creating as a Standalone Object

```python
vc = fw.post("/api/viewerconfigs", json={
    "name": "pet-read-viewer",
    "viewer": "OHIF_V3",
    "config": { ... }
})
viewer_config_id = vc._id
```

---

## Configuration Options

### Measurement Labels

Custom annotation labels with colors, used for ROI and measurement tools:

```json
"labels": [
  { "label": "Frontal", "value": "Frontal", "color": "rgba(255,0,0,0.5)" },
  { "label": "Parietal", "value": "Parietal", "color": "rgba(0,255,222,0.5)" },
  { "label": "Temporal", "value": "Temporal", "color": "rgba(0,0,255,0.5)" }
]
```

### File Browser

Controls whether readers can browse beyond the assigned container:

```json
"fileBrowser": {
  "enabled": true,
  "scope": "session"    // "session" or "subject"
}
```

### General Settings

```json
{
  "showStudyList": false,
  "allowDraft": true,
  "timerOn": false
}
```

### Mouse Actions

```json
"mouseActions": [
  { "toolName": "Zoom", "button": "middle" },
  { "toolName": "Pan", "button": "right" },
  { "toolName": "Wwwc", "button": "left" },
  { "toolName": "StackScrollMouseWheel", "button": "wheel" }
]
```

### Smart CT Ranges

Predefined windowing presets with color overlays:

```json
"smartCTRanges": {
  "Lung": { "min": -1000, "max": -500, "color": "rgba(0,255,0,0.3)" },
  "Tumor": { "min": 20, "max": 80, "color": "rgba(255,0,0,0.3)" }
}
```

---

## Key Differences from V2 Viewer Config

- V3 supports `fileBrowser` scope (session/subject) — V2 does not
- V3 measurement labels use the same JSON shape but are rendered differently in OHIF_V3
- V3 does not support `overlay` customization (top-left/top-right/bottom-left/bottom-right text) — this was a V2 feature
- V3 does not support `scaleIndicator` configuration
- V3 does not support `hotkeys` in the same format as V2
- V3 hanging protocol / layout configuration differs from V2's `layouts` array

---

## V3 Viewer Capabilities

The OHIF_V3 viewer is a significant rewrite of the V2 viewer with:

- Multi-planar reconstruction (MPR)
- Length, area, angle, and ROI measurement tools
- Windowing and zoom controls
- Protocol-driven viewer configuration
- Annotation persistence linked to tasks
- Better series navigation and display
