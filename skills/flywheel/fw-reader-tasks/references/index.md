# Form Schema References

* [Form Schema Reference](form-schema.md) - JSON schema for reader task forms in both V2 (formio) and V3 (Tasks Manager) generations, how to tell them apart, and how to migrate V2 to V3.
* [V2 Form Schema Reference (Legacy)](v2/form-schema-v2.md) - JSON schema for V2 (legacy) reader task forms using the formio studyForm.components structure rendered in the OHIF V2 viewer.
* [V3 Form Schema Reference (Tasks Manager)](v3/form-schema-v3.md) - JSON schema for V3 reader task forms using the form.fields structure for the Tasks Manager and OHIF_V3 viewer.

# Viewer Configuration References

* [V2 Viewer Configuration Reference (Legacy OHIF Viewer)](v2/viewer-config-v2.md) - The separate viewer config JSON that controls the OHIF V2 image viewer's appearance and behavior for reader task viewer protocols.
* [V3 Viewer Configuration Reference (OHIF_V3)](v3/viewer-config-v3.md) - The V3 viewer config controlling the OHIF_V3 image viewer, embedded in protocol JSON or created as a standalone ViewerConfig object.

# API References

* [API Reference: Forms, Form Responses & Viewer Configs](common/api-forms.md) - REST endpoints for reader task forms, form responses, and viewer configs (/api/forms, /api/formresponses, /api/viewerconfigs).
* [API Reference: Read Task Protocols](common/api-protocols.md) - REST endpoints for read task protocols (/api/read_task_protocols), the unit that joins a form and viewer config and that tasks are created from.
* [API Reference: Reader Tasks](common/api-reader-tasks.md) - REST endpoints for reader tasks (/api/readertasks) — listing, filtering, and managing task assignments and status.
