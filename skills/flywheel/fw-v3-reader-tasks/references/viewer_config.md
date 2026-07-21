---
type: Viewer Config Reference
title: V3 Viewer Configuration Reference
description: Reference for viewer_config in V3 reader task protocols — labels, file browser, and where the config lives for protocols versus projects.
tags: [reader-tasks, v3, viewer-config]
timestamp: 2026-07-15T00:00:00Z
---

# V3 Viewer Configuration Reference

Reference for `viewer_config` in V3 reader task protocols.

> **Note:** The V3 viewer currently supports fewer configuration options than V2. Additional options are being added over time. For missing V2 features, contact your Flywheel representative for roadmap prioritization.

---

## Where viewer_config lives

For a **task protocol**, `viewer_config` is a top-level key in the editor JSON (alongside `form`, `esignature_config`, `completion_tags`, and `workflow`). Pass an empty object `{}` if no viewer configuration is needed.

For a **project** (non-task workflows), viewer config is stored in a file named `ohif_configv3.json` attached to the project. The same configuration options apply.

---

## Configuration Options

### Labels

Property name: `labels`

Defines a list of annotation labels users can choose from when creating measurements in the viewer.

```json
"viewer_config": {
  "labels": {
    "items": [
      { "value": "finding", "label": "Finding", "color": "#ff5050" },
      { "value": "note", "label": "Note", "color": "#ffb400" },
      { "value": "reviewed", "label": "Reviewed", "color": "#50c878" }
    ],
    "labelOnMeasure": true,
    "exclusive": false
  }
}
```

| Property | Type | Description |
|---|---|---|
| `items` | array | List of label options. Each item has `value` (stored value + measurement panel display), `label` (shown in picker), and optional `color` (hex RGB). If `color` is set, the user cannot change it in the viewer. |
| `labelOnMeasure` | boolean | When `true`, the label picker is shown automatically every time the user creates an annotation. |
| `exclusive` | boolean | When `true`, users cannot enter custom labels — they must choose from `items`. |

---

### File Browser

Property name: `fileBrowser`

Controls whether users can load additional images from outside their initially loaded set into the viewer's left-side panel.

```json
"viewer_config": {
  "fileBrowser": {
    "enabled": true,
    "scope": "session"
  }
}
```

| Property | Type | Description |
|---|---|---|
| `enabled` | boolean | Set to `false` to disable the file browser entirely. Defaults to `true` when not specified. |
| `scope` | `"subject"` or `"session"` | Optional. `"subject"` (default) allows browsing all sessions for the subject. `"session"` restricts browsing to images from the same session as the currently loaded data. |

> **Task workflow note:** In task-based workflows, the file browser is **disabled by default** and must be explicitly enabled by setting `enabled: true` in the protocol's `viewer_config`. In non-task workflows, the file browser is available by default.

#### `scope` is browse-on-demand, not auto-load (verified against source, 2026-07)

Confirmed against `fw-ohif-v3`:

- Schema + defaults: `extensions/flywheel-core/src/schemas/viewerConfigSchema.ts:60-79` (`enabled` defaults `false`, default object is `{ enabled: false, scope: 'subject' }`).
- Behavior: `extensions/flywheel-ui/src/components/SubjectSessionsBrowser/SubjectSessionsBrowser.tsx:71-91` reads `viewerConfig.fileBrowser?.enabled` and `?.scope || 'subject'`, then — **only when `scope === 'session'`** — filters the session list down to the current session; otherwise it keeps all of the subject's sessions.

Two things this pins down:

- `scope: "subject"` populates an **opt-in browse dialog** with all the subject's sessions. It does **not** auto-load every session into viewports — the reader opens the file browser and pulls in what they want.
- This is the **only** property in the reader-task config with real cross-session behavior. It is independent of the task's container level (`parent_ref` at task creation) and of `protocol_config.longitudinal` (which is inert — see SKILL.md). If the goal is "let the reader see all of the subject's sessions," this is the lever: `fileBrowser: { enabled: true, scope: "subject" }`.

---

## Combining options

```json
"viewer_config": {
  "labels": {
    "items": [
      { "value": "issue", "label": "Issue", "color": "#ff5050" },
      { "value": "note", "label": "Note", "color": "#ffb400" }
    ],
    "labelOnMeasure": true,
    "exclusive": true
  },
  "fileBrowser": {
    "enabled": true,
    "scope": "session"
  }
}
```
