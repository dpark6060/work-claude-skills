---
type: Endpoint Index
title: Core API Endpoints Index
description: One-line-per-endpoint routing index for all Flywheel Core API (/api/) endpoints across 48 tags.
tags: [flywheel, core-api, index]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — Endpoints Index

One line per endpoint. For full parameter details, read `endpoints/core_<tag>.md`.

| Method | Path | Tag | Summary |
|---|---|---|---|
| `GET` | `/api/acquisitions` | acquisitions | Get a list of acquisitions |
| `POST` | `/api/acquisitions` | acquisitions | Create a new acquisition |
| `DELETE` | `/api/acquisitions` | acquisitions | Delete multiple acquisitions by ID list |
| `GET` | `/api/acquisitions/{acquisition_id}` | acquisitions | Get a single acquisition |
| `PUT` | `/api/acquisitions/{acquisition_id}` | acquisitions | Update an acquisition |
| `DELETE` | `/api/acquisitions/{acquisition_id}` | acquisitions | Delete a acquisition |
| `POST` | `/api/acquisitions/{acquisition_id}/copy` | acquisitions | Smart copy an acquisition |
| `GET` | `/api/acquisitions/{cid}/analyses` | acquisitions | Get analyses for a(n) acquisition. |
| `POST` | `/api/acquisitions/{cid}/analyses` | acquisitions | Create an analysis and upload files. |
| `GET` | `/api/acquisitions/{cid}/analyses/{analysis_id}` | acquisitions | Get an analysis. |
| `PUT` | `/api/acquisitions/{cid}/analyses/{analysis_id}` | acquisitions | Modify an analysis. |
| `DELETE` | `/api/acquisitions/{cid}/analyses/{analysis_id}` | acquisitions | Delete an analysis |
| `POST` | `/api/acquisitions/{cid}/analyses/{analysis_id}/files` | acquisitions | Upload an output file to an analysis. *(deprecated)* |
| `GET` | `/api/acquisitions/{cid}/analyses/{analysis_id}/files/{filename}` | acquisitions | Download analysis outputs with filter. *(deprecated)* |
| `GET` | `/api/acquisitions/{cid}/analyses/{analysis_id}/files/{filename}/info` | acquisitions | Get file info from a(n) acquisition *(deprecated)* |
| `GET` | `/api/acquisitions/{cid}/analyses/{analysis_id}/inputs/{filename}` | acquisitions | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/acquisitions/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | acquisitions | Get file info from a(n) acquisition *(deprecated)* |
| `DELETE` | `/api/acquisitions/{cid}/analyses/{analysis_id}/notes/{note_id}` | acquisitions | Remove a note from a(n) acquisition analysis. |
| `PUT` | `/api/acquisitions/{cid}/files/{filename}` | acquisitions | Modify a file's attributes |
| `DELETE` | `/api/acquisitions/{cid}/files/{filename}` | acquisitions | Delete a file |
| `PATCH` | `/api/acquisitions/{cid}/files/{filename}/classification` | acquisitions | Update classification for a particular file. |
| `GET` | `/api/acquisitions/{cid}/files/{filename}/info` | acquisitions | Get info for a particular file. |
| `PATCH` | `/api/acquisitions/{cid}/files/{filename}/info` | acquisitions | Update info for a particular file. |
| `PATCH` | `/api/acquisitions/{cid}/info` | acquisitions | Update or replace info for a(n) acquisition. |
| `GET` | `/api/acquisitions/{cid}/inputs/{filename}/info` | acquisitions | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/acquisitions/{cid}/notes/{note_id}` | acquisitions | Get a note of a(n) acquisition. |
| `PUT` | `/api/acquisitions/{cid}/notes/{note_id}` | acquisitions | Update a note of a(n) acquisition. |
| `DELETE` | `/api/acquisitions/{cid}/notes/{note_id}` | acquisitions | Remove a note from a(n) acquisition |
| `POST` | `/api/acquisitions/{cid}/tags` | acquisitions | Add a tag to a(n) acquisition. |
| `PATCH` | `/api/acquisitions/{cid}/tags` | acquisitions | Add multiple tags to a(n) acquisition |
| `DELETE` | `/api/acquisitions/{cid}/tags` | acquisitions | Delete multiple tags from a(n) acquisition |
| `GET` | `/api/acquisitions/{cid}/tags/{value}` | acquisitions | Get the value of a tag, by name. |
| `PUT` | `/api/acquisitions/{cid}/tags/{value}` | acquisitions | Rename a tag. |
| `DELETE` | `/api/acquisitions/{cid}/tags/{value}` | acquisitions | Delete a tag |
| `GET` | `/api/acquisitions/{cid}/{sub_cname}/analyses` | acquisitions | Get nested analyses from acquisitions |
| `POST` | `/api/acquisitions/{container_id}/analyses/{analysis_id}/notes` | acquisitions | Add a note to a(n) acquisition analysis. |
| `POST` | `/api/acquisitions/{container_id}/files` | acquisitions | Upload a file to a(n) acquisition. |
| `GET` | `/api/acquisitions/{container_id}/files/{file_name}` | acquisitions | Download a file. |
| `POST` | `/api/acquisitions/{container_id}/notes` | acquisitions | Add a note to a(n) acquisition. |
| `GET` | `/api/analyses` | analyses | Find all analyses |
| `DELETE` | `/api/analyses` | analyses | Delete multiple analyses by ID list |
| `GET` | `/api/analyses/{analysis_id}` | analyses | Get an analysis. |
| `PUT` | `/api/analyses/{analysis_id}` | analyses | Modify an analysis. |
| `DELETE` | `/api/analyses/{analysis_id}` | analyses | Delete an analysis |
| `GET` | `/api/analyses/{cid}/files/{filename}` | analyses | Download output file from analysis |
| `PUT` | `/api/analyses/{cid}/files/{filename}` | analyses | Modify a file's attributes |
| `DELETE` | `/api/analyses/{cid}/files/{filename}` | analyses | Delete a file |
| `PATCH` | `/api/analyses/{cid}/files/{filename}/classification` | analyses | Update classification for a particular file. |
| `GET` | `/api/analyses/{cid}/files/{filename}/info` | analyses | Get metadata for an output file of an analysis. |
| `PATCH` | `/api/analyses/{cid}/files/{filename}/info` | analyses | Update info for a particular file. |
| `PATCH` | `/api/analyses/{cid}/info` | analyses | Update or replace info for a(n) analysis. |
| `GET` | `/api/analyses/{cid}/inputs/{filename}` | analyses | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/analyses/{cid}/inputs/{filename}/info` | analyses | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/analyses/{cid}/notes/{note_id}` | analyses | Get a note of a(n) analysis. |
| `PUT` | `/api/analyses/{cid}/notes/{note_id}` | analyses | Update a note of a(n) analysis. |
| `DELETE` | `/api/analyses/{cid}/notes/{note_id}` | analyses | Remove a note from a(n) analysis |
| `POST` | `/api/analyses/{cid}/tags` | analyses | Add a tag to a(n) analysis. |
| `GET` | `/api/analyses/{cid}/tags/{value}` | analyses | Get the value of a tag, by name. |
| `PUT` | `/api/analyses/{cid}/tags/{value}` | analyses | Rename a tag. |
| `DELETE` | `/api/analyses/{cid}/tags/{value}` | analyses | Delete a tag |
| `POST` | `/api/analyses/{container_id}/files` | analyses | Upload an output file to an analysis. |
| `GET` | `/api/analyses/{container_id}/files/{file_name}` | analyses | Download a file. |
| `GET` | `/api/analyses/{container_id}/info` | analyses | Get Info |
| `GET` | `/api/analyses/{container_id}/input_files/{filename}/info` | analyses | Get metadata for input file(s) for an analysis. |
| `GET` | `/api/analyses/{container_id}/inputs/{filename}/info` | analyses | Get metadata for an input file of an analysis. *(deprecated)* |
| `POST` | `/api/analyses/{container_id}/notes` | analyses | Add a note to a(n) analysis. |
| `GET` | `/api/annotations` | annotations | Get all annotations associated with a file |
| `POST` | `/api/annotations` | annotations | Add an annotation |
| `GET` | `/api/annotations/counts` | annotations | Get annotation count |
| `GET` | `/api/annotations/{annotation_id}` | annotations | Get annotation by ID |
| `PUT` | `/api/annotations/{annotation_id}` | annotations | Modify an annotation |
| `DELETE` | `/api/annotations/{annotation_id}` | annotations | Delete an annotation |
| `GET` | `/api/v3/annotations` | annotations | Get all annotations |
| `POST` | `/api/v3/annotations` | annotations | Create a new Annotation |
| `POST` | `/api/v3/annotations/count` | annotations | Count annotations |
| `GET` | `/api/v3/annotations/delete_reasons` | annotations | Get Delete Reasons |
| `GET` | `/api/v3/annotations/{annotation_id}` | annotations | Get By Id |
| `POST` | `/api/v3/annotations/{annotation_id}` | annotations | Create a new version of an Annotation |
| `PUT` | `/api/v3/annotations/{annotation_id}` | annotations | Modify |
| `DELETE` | `/api/v3/annotations/{annotation_id}` | annotations | Delete |
| `GET` | `/api/v3/annotations/{annotation_id}/file` | annotations | Get File By Annotation Id |
| `GET` | `/api/v3/annotations/{annotation_id}/versions` | annotations | Get All Versions |
| `GET` | `/api/v3/annotations/{annotation_id}/versions/{version}` | annotations | Get Version |
| `DELETE` | `/api/v3/annotations/{annotation_id}/versions/{version}` | annotations | Delete Version |
| `GET` | `/api/v3/annotations/{annotation_id}/versions/{version}/file` | annotations | Get File Version |
| `POST` | `/api/v3/annotations/{annotation_id}/versions/{version}/restore` | annotations | Restore Version |
| `GET` | `/api/audit-trail/reports` | audit_trail | List Audit Trail Reports |
| `POST` | `/api/audit-trail/reports` | audit_trail | Starts generation of an Audit Trail Report |
| `PATCH` | `/api/audit-trail/reports/{report_id}` | audit_trail | Modify an Audit Trail Report |
| `DELETE` | `/api/audit-trail/reports/{report_id}` | audit_trail | Deletes an Audit Trail Report |
| `GET` | `/api/audit-trail/reports/{report_id}/csv` | audit_trail | Download Audit Trail Report |
| `GET` | `/api/auth/status` | auth | Get Login status |
| `POST` | `/api/login` | auth | Login |
| `GET` | `/api/login/auth0` | auth | Record Auth0 login and return the current user record |
| `POST` | `/api/login/basic` | auth | Login Basic |
| `POST` | `/api/logout` | auth | Logout |
| `GET` | `/api/batch` | batch | Get a list of batch jobs the user has created. |
| `POST` | `/api/batch` | batch | Create a batch job proposal and insert it as 'pending'. |
| `POST` | `/api/batch/jobs` | batch | Create a batch job proposal from preconstructed jobs and insert it as 'pending'. |
| `GET` | `/api/batch/{batch_id}` | batch | Get batch job details. |
| `POST` | `/api/batch/{batch_id}/cancel` | batch | Cancel a Job |
| `POST` | `/api/batch/{batch_id}/run` | batch | Launch a job. |
| `POST` | `/api/bulk/add/tags` | bulk | Add Tags |
| `POST` | `/api/bulk/copy/{cname}` | bulk | Copy *(deprecated)* |
| `POST` | `/api/bulk/delete/readertasks` | bulk | Delete Reader Task Bulk |
| `POST` | `/api/bulk/delete/{cname}` | bulk | Delete *(deprecated)* |
| `POST` | `/api/bulk/move/acquisitions` | bulk | Move Acquisitions |
| `POST` | `/api/bulk/move/sessions` | bulk | Perform a bulk move of sessions to either a subject or project |
| `POST` | `/api/bulk/move/subjects` | bulk | Move Subjects *(deprecated)* |
| `POST` | `/api/bulk/remove/tags` | bulk | Remove Tags |
| `GET` | `/api/changes/{container_type}/{container_id}` | change_log | Get Change Log |
| `GET` | `/api/changes/{container_type}/{container_id}/fields/{field}` | change_log | Get change logs by specific field, in reverse chronological order |
| `GET` | `/api/collections` | collections | List all collections. |
| `POST` | `/api/collections` | collections | Create a collection |
| `DELETE` | `/api/collections` | collections | Delete multiple collections by ID list |
| `GET` | `/api/collections/curators` | collections | List all curators of collections |
| `GET` | `/api/collections/{cid}/analyses/{analysis_id}/files/{filename}/info` | collections | Get file info from a(n) collection *(deprecated)* |
| `GET` | `/api/collections/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | collections | Get file info from a(n) collection *(deprecated)* |
| `PUT` | `/api/collections/{cid}/files/{filename}` | collections | Modify a file's attributes |
| `DELETE` | `/api/collections/{cid}/files/{filename}` | collections | Delete a file |
| `PATCH` | `/api/collections/{cid}/files/{filename}/classification` | collections | Update classification for a particular file. |
| `GET` | `/api/collections/{cid}/files/{filename}/info` | collections | Get info for a particular file. |
| `PATCH` | `/api/collections/{cid}/files/{filename}/info` | collections | Update info for a particular file. |
| `PATCH` | `/api/collections/{cid}/info` | collections | Update or replace info for a(n) collection. |
| `GET` | `/api/collections/{cid}/inputs/{filename}/info` | collections | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/collections/{cid}/notes/{note_id}` | collections | Get a note of a(n) collection. |
| `PUT` | `/api/collections/{cid}/notes/{note_id}` | collections | Update a note of a(n) collection. |
| `DELETE` | `/api/collections/{cid}/notes/{note_id}` | collections | Remove a note from a(n) collection |
| `POST` | `/api/collections/{cid}/tags` | collections | Add a tag to a(n) collection. |
| `PATCH` | `/api/collections/{cid}/tags` | collections | Add multiple tags to a(n) collection |
| `DELETE` | `/api/collections/{cid}/tags` | collections | Delete multiple tags from a(n) collection |
| `GET` | `/api/collections/{cid}/tags/{value}` | collections | Get the value of a tag, by name. |
| `PUT` | `/api/collections/{cid}/tags/{value}` | collections | Rename a tag. |
| `DELETE` | `/api/collections/{cid}/tags/{value}` | collections | Delete a tag |
| `GET` | `/api/collections/{collection_id}` | collections | Retrieve a single collection |
| `PUT` | `/api/collections/{collection_id}` | collections | Update a collection and its contents |
| `DELETE` | `/api/collections/{collection_id}` | collections | Delete a collection |
| `GET` | `/api/collections/{collection_id}/acquisitions` | collections | List acquisitions in a collection |
| `POST` | `/api/collections/{collection_id}/permissions` | collections | Add a permission |
| `GET` | `/api/collections/{collection_id}/permissions/{user_id}` | collections | List a user's permissions for this group. |
| `PUT` | `/api/collections/{collection_id}/permissions/{user_id}` | collections | Update a user's permission for this group. |
| `DELETE` | `/api/collections/{collection_id}/permissions/{user_id}` | collections | Delete a permission |
| `GET` | `/api/collections/{collection_id}/sessions` | collections | List sessions in a collection |
| `POST` | `/api/collections/{container_id}/files` | collections | Upload a file to a(n) collection. |
| `GET` | `/api/collections/{container_id}/files/{file_name}` | collections | Download a file. |
| `POST` | `/api/collections/{container_id}/notes` | collections | Add a note to a(n) collection. |
| `GET` | `/api/config` | config | Get public configuration |
| `GET` | `/api/config.js` | config | Return public Scitran configuration information in javascript format. |
| `GET` | `/api/config/delete_reasons` | config | Get all delete reasons for a container |
| `GET` | `/api/config/file_types` | config | Get all file types |
| `GET` | `/api/config/project-sharing-options` | config | Get all available filter categories for shared projects |
| `GET` | `/api/config/project_locking_reasons` | config | Get all reasons for locking a project |
| `GET` | `/api/version` | config | Get server and database schema version info |
| `GET` | `/api/containers` | containers | Find all containers |
| `POST` | `/api/containers` | containers | Create container |
| `GET` | `/api/containers/{cid}/analyses` | containers | Get analyses for a(n) container. |
| `POST` | `/api/containers/{cid}/analyses` | containers | Create an analysis and upload files. |
| `GET` | `/api/containers/{cid}/analyses/{analysis_id}` | containers | Get an analysis. |
| `PUT` | `/api/containers/{cid}/analyses/{analysis_id}` | containers | Modify an analysis. |
| `DELETE` | `/api/containers/{cid}/analyses/{analysis_id}` | containers | Delete an analysis |
| `POST` | `/api/containers/{cid}/analyses/{analysis_id}/files` | containers | Upload an output file to an analysis. *(deprecated)* |
| `GET` | `/api/containers/{cid}/analyses/{analysis_id}/files/{filename}` | containers | Download analysis outputs with filter. *(deprecated)* |
| `GET` | `/api/containers/{cid}/analyses/{analysis_id}/files/{filename}/info` | containers | Get file info from a(n) container *(deprecated)* |
| `GET` | `/api/containers/{cid}/analyses/{analysis_id}/inputs/{filename}` | containers | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/containers/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | containers | Get file info from a(n) container *(deprecated)* |
| `DELETE` | `/api/containers/{cid}/analyses/{analysis_id}/notes/{note_id}` | containers | Remove a note from a(n) container analysis. |
| `PUT` | `/api/containers/{cid}/files/{filename}` | containers | Modify a file's attributes |
| `DELETE` | `/api/containers/{cid}/files/{filename}` | containers | Delete a file |
| `PATCH` | `/api/containers/{cid}/files/{filename}/classification` | containers | Update classification for a particular file. |
| `GET` | `/api/containers/{cid}/files/{filename}/info` | containers | Get info for a particular file. |
| `PATCH` | `/api/containers/{cid}/files/{filename}/info` | containers | Update info for a particular file. |
| `PATCH` | `/api/containers/{cid}/info` | containers | Update or replace info for a(n) container. |
| `GET` | `/api/containers/{cid}/inputs/{filename}/info` | containers | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/containers/{cid}/notes/{note_id}` | containers | Get a note of a(n) container. |
| `PUT` | `/api/containers/{cid}/notes/{note_id}` | containers | Update a note of a(n) container. |
| `DELETE` | `/api/containers/{cid}/notes/{note_id}` | containers | Remove a note from a(n) container |
| `POST` | `/api/containers/{cid}/tags` | containers | Add a tag to a(n) container. |
| `PATCH` | `/api/containers/{cid}/tags` | containers | Add multiple tags to a(n) container |
| `DELETE` | `/api/containers/{cid}/tags` | containers | Delete multiple tags from a(n) container |
| `GET` | `/api/containers/{cid}/tags/{value}` | containers | Get the value of a tag, by name. |
| `PUT` | `/api/containers/{cid}/tags/{value}` | containers | Rename a tag. |
| `DELETE` | `/api/containers/{cid}/tags/{value}` | containers | Delete a tag |
| `GET` | `/api/containers/{cid}/{sub_cname}/analyses` | containers | Get nested analyses from containers |
| `GET` | `/api/containers/{container_id}` | containers | Retrieve a single container |
| `PUT` | `/api/containers/{container_id}` | containers | Update a container and its contents |
| `DELETE` | `/api/containers/{container_id}` | containers | Delete a container |
| `POST` | `/api/containers/{container_id}/analyses/{analysis_id}/notes` | containers | Add a note to a(n) container analysis. |
| `POST` | `/api/containers/{container_id}/files` | containers | Upload a file to a(n) container. |
| `GET` | `/api/containers/{container_id}/files/{file_name}` | containers | Download a file. |
| `POST` | `/api/containers/{container_id}/notes` | containers | Add a note to a(n) container. |
| `GET` | `/api/containers/{container_id}/views` | containers | Return a list of all views belonging to container |
| `POST` | `/api/containers/{container_id}/views` | containers | Add a new data view |
| `GET` | `/api/custom_filters` | custom_filters | Get all custom filters for user |
| `POST` | `/api/custom_filters` | custom_filters | Create a custom filter for user |
| `PUT` | `/api/custom_filters/{custom_filter_id}` | custom_filters | Update a custom filter for user |
| `DELETE` | `/api/custom_filters/{custom_filter_id}` | custom_filters | Delete a custom filter for user |
| `GET` | `/api/cvat/export-formats` | cvat | Get CVAT export formats |
| `GET` | `/api/cvat/export-formats/{cvat_project_id}` | cvat | Get CVAT export formats for a project |
| `POST` | `/api/cvat/file-access/{file_id}` | cvat | Record cvat file access |
| `GET` | `/api/data_view_executions` | data_view_executions | Get a list of data_view_executions |
| `GET` | `/api/data_view_executions/{data_view_execution_id}` | data_view_executions | Get a single data_view_execution |
| `GET` | `/api/data_view_executions/{data_view_execution_id}/data` | data_view_executions | Get the data from a data_view_execution |
| `GET` | `/api/data_view_executions/{data_view_execution_id}/data/columns` | data_view_executions | Get Data Columns |
| `POST` | `/api/data_view_executions/{data_view_execution_id}/delete` | data_view_executions | Delete a data_view_execution |
| `POST` | `/api/data_view_executions/{data_view_execution_id}/save` | data_view_executions | Save a data_view_execution to a project |
| `POST` | `/api/data_view_executions/{data_view_execution_id}/ticket` | data_view_executions | Get Ticket Stub |
| `POST` | `/api/dataexplorer/facets` | dataexplorer | Get Facets |
| `POST` | `/api/dataexplorer/index/fields` | dataexplorer | Index Fields *(deprecated)* |
| `GET` | `/api/dataexplorer/mapped_fields` | dataexplorer | Get fields mapped for search |
| `GET` | `/api/dataexplorer/queries` | dataexplorer | Get Queries |
| `POST` | `/api/dataexplorer/queries` | dataexplorer | Save a search query |
| `DELETE` | `/api/dataexplorer/queries/{search_id}` | dataexplorer | Delete a saved search |
| `GET` | `/api/dataexplorer/queries/{sid}` | dataexplorer | Return a saved search query |
| `PUT` | `/api/dataexplorer/queries/{sid}` | dataexplorer | Replace a search query |
| `POST` | `/api/dataexplorer/search` | dataexplorer | Perform a search query |
| `DELETE` | `/api/dataexplorer/search` | dataexplorer | Delete containers by a search query |
| `POST` | `/api/dataexplorer/search/fields` | dataexplorer | Search Fields *(deprecated)* |
| `POST` | `/api/dataexplorer/search/fields/aggregate` | dataexplorer | Aggregate Fields |
| `POST` | `/api/dataexplorer/search/nodes` | dataexplorer | Get Nodes |
| `POST` | `/api/dataexplorer/search/parse` | dataexplorer | Parse a structured search query |
| `GET` | `/api/dataexplorer/search/status` | dataexplorer | Get the status of search (Mongo Connector) |
| `POST` | `/api/dataexplorer/search/suggest` | dataexplorer | Get suggestions for a structured search query |
| `POST` | `/api/dataexplorer/search/training` | dataexplorer | Save Training Set |
| `GET` | `/api/devices` | devices | List all devices. |
| `POST` | `/api/devices` | devices | Create a new device. |
| `GET` | `/api/devices/self` | devices | Get current device. |
| `PUT` | `/api/devices/self` | devices | Modify a device's type, name, interval, info or set errors. |
| `GET` | `/api/devices/status` | devices | Get status for all known devices. |
| `GET` | `/api/devices/{device_id}` | devices | Get device details |
| `PUT` | `/api/devices/{device_id}` | devices | Update a device |
| `DELETE` | `/api/devices/{device_id}` | devices | Delete a device |
| `POST` | `/api/devices/{device_id}/key` | devices | Generate device API key |
| `DELETE` | `/api/devices/{device_id}/key/{key_id}` | devices | Delete Device Key |
| `GET` | `/api/dimse/projects` | dimse | List all DIMSE project AETs |
| `POST` | `/api/dimse/projects` | dimse | Create a new DIMSE project AET |
| `GET` | `/api/dimse/projects/{project_aet}` | dimse | Get DIMSE project AET |
| `DELETE` | `/api/dimse/projects/{project_aet}` | dimse | Delete a DIMSE project AET |
| `GET` | `/api/dimse/services` | dimse | List all DIMSE services AETs |
| `POST` | `/api/dimse/services` | dimse | Create a new DIMSE service AET |
| `GET` | `/api/dimse/services/{service_aet}` | dimse | Get DIMSE service by AET or id |
| `DELETE` | `/api/dimse/services/{service_aet}` | dimse | Delete a DIMSE service AET |
| `GET` | `/api/download` | download | Download files listed in the given ticket. |
| `POST` | `/api/download` | download | Create a download ticket |
| `POST` | `/api/download/summary` | download | Download summary |
| `POST` | `/api/download/targets` | download | Download targets |
| `POST` | `/api/engine` | engine | Upload a list of file fields. |
| `GET` | `/api/files` | files | Return all files |
| `POST` | `/api/files` | files | Upsert a File |
| `DELETE` | `/api/files` | files | Delete multiple files by ID list |
| `DELETE` | `/api/files/` | files | Delete Many *(deprecated)* |
| `GET` | `/api/files/{file_id}` | files | Get File |
| `PUT` | `/api/files/{file_id}` | files | Modify |
| `DELETE` | `/api/files/{file_id}` | files | Delete a File |
| `PUT` | `/api/files/{file_id}/classification` | files | Modify Classification |
| `GET` | `/api/files/{file_id}/download` | files | Download |
| `GET` | `/api/files/{file_id}/info` | files | Get Info |
| `PUT` | `/api/files/{file_id}/info` | files | Replace Info |
| `PATCH` | `/api/files/{file_id}/info` | files | Modify Info |
| `POST` | `/api/files/{file_id}/move` | files | Move and/or rename a file |
| `POST` | `/api/files/{file_id}/restore` | files | Restore a File |
| `GET` | `/api/files/{file_id}/signed_url` | files | Get Signed Url |
| `GET` | `/api/files/{file_id}/tags` | files | Return a file tags, from any version |
| `PUT` | `/api/files/{file_id}/tags` | files | Set list of tags on a file. |
| `PATCH` | `/api/files/{file_id}/tags` | files | Add list of tags on a file. |
| `DELETE` | `/api/files/{file_id}/tags` | files | Remove the specified tags from most recent file version |
| `POST` | `/api/files/{file_id}/ticket` | files | Get Ticket Stub |
| `GET` | `/api/files/{file_id}/ticket/{ticket_id}/validate` | files | Validate Ticket |
| `GET` | `/api/files/{file_id}/version/{version}/download/{filename}` | files | Engine Download |
| `GET` | `/api/files/{file_id}/versions` | files | Get Versions |
| `GET` | `/api/files/{file_id}/zip_info` | files | Get Zip Info |
| `GET` | `/api/files/{file_id}/zip_member/{member}` | files | Get Zip Member |
| `GET` | `/api/formresponses` | form_responses | Find all form responses |
| `POST` | `/api/formresponses` | form_responses | Add a form response |
| `GET` | `/api/formresponses/{form_response_id}` | form_responses | Get a form response |
| `PUT` | `/api/formresponses/{form_response_id}` | form_responses | Modify a form response |
| `DELETE` | `/api/formresponses/{form_response_id}` | form_responses | Delete a form response |
| `GET` | `/api/forms` | forms | Get all forms |
| `POST` | `/api/forms` | forms | Create |
| `GET` | `/api/forms/{form_id}` | forms | Get By Id |
| `PUT` | `/api/forms/{form_id}` | forms | Modify |
| `DELETE` | `/api/forms/{form_id}` | forms | Delete |
| `GET` | `/api/forms/{form_id}/responses` | forms | Find All Responses By Form Id |
| `GET` | `/api/gears` | gears | List all gears |
| `GET` | `/api/gears/my-tickets` | gears | Retrieve all gear tickets for the current user |
| `POST` | `/api/gears/prepare-add` | gears | Prepare a gear upload |
| `POST` | `/api/gears/save` | gears | Report the result of a gear upload and save the ticket |
| `GET` | `/api/gears/temp/{gear_id}` | gears | Download |
| `GET` | `/api/gears/ticket/{ticket_id}` | gears | Retrieve a specific gear ticket |
| `GET` | `/api/gears/{gear_id}` | gears | Retrieve details about a specific gear |
| `DELETE` | `/api/gears/{gear_id}` | gears | Delete a gear (not recommended) *(deprecated)* |
| `GET` | `/api/gears/{gear_id}/context/{container_name}/{container_id}` | gears | Get context values for the given gear and container. |
| `POST` | `/api/gears/{gear_id}/disable` | gears | Disable |
| `POST` | `/api/gears/{gear_id}/enable` | gears | Enable |
| `GET` | `/api/gears/{gear_id}/invocation` | gears | Get a schema for invoking a gear |
| `GET` | `/api/gears/{gear_id}/suggest/{container_name}/{container_id}` | gears | Get files with input suggestions, parent containers, and child containers for the given container. |
| `POST` | `/api/gears/{gear_name}` | gears | Create or update a gear. |
| `PUT` | `/api/gears/{gear_name}/permissions` | gears | Replace permissions for the given gear |
| `DELETE` | `/api/gears/{gear_name}/permissions` | gears | Delete permissions of the given gear |
| `PUT` | `/api/gears/{gear_name}/permissions/{permission_type}` | gears | Add an individual permission to the given gear |
| `DELETE` | `/api/gears/{gear_name}/permissions/{permission_type}/{permission_id}` | gears | Delete an individual permission of the given gear |
| `GET` | `/api/gears/{gear_name}/series` | gears | Get gear series. |
| `PUT` | `/api/gears/{gear_name}/series` | gears | Update a gear series |
| `GET` | `/api/groups` | groups | List all groups |
| `POST` | `/api/groups` | groups | Add a group |
| `DELETE` | `/api/groups` | groups | Delete multiple groups by ID list |
| `GET` | `/api/groups/{cid}/settings/deid_profile` | groups | Get deid_profile for group |
| `POST` | `/api/groups/{cid}/tags` | groups | Add a tag to a(n) group. |
| `PATCH` | `/api/groups/{cid}/tags` | groups | Add multiple tags to a(n) group |
| `DELETE` | `/api/groups/{cid}/tags` | groups | Delete multiple tags from a(n) group |
| `GET` | `/api/groups/{cid}/tags/{value}` | groups | Get the value of a tag, by name. |
| `PUT` | `/api/groups/{cid}/tags/{value}` | groups | Rename a tag. |
| `DELETE` | `/api/groups/{cid}/tags/{value}` | groups | Delete a tag |
| `GET` | `/api/groups/{cid}/{sub_cname}/analyses` | groups | Get nested analyses from groups |
| `GET` | `/api/groups/{container_id}/settings` | groups | Get a(n) group settings |
| `PUT` | `/api/groups/{container_id}/settings` | groups | Modify a(n) group settings |
| `GET` | `/api/groups/{group_id}` | groups | Get group info |
| `PUT` | `/api/groups/{group_id}` | groups | Update group |
| `DELETE` | `/api/groups/{group_id}` | groups | Delete group |
| `POST` | `/api/groups/{group_id}/permissions` | groups | Add a permission |
| `POST` | `/api/groups/{group_id}/permissions/templates` | groups | Add a permission template |
| `GET` | `/api/groups/{group_id}/permissions/templates/{user_id}` | groups | List a user's permissions for this group. |
| `PUT` | `/api/groups/{group_id}/permissions/templates/{user_id}` | groups | Update a user's permission for this group. |
| `DELETE` | `/api/groups/{group_id}/permissions/templates/{user_id}` | groups | Delete a permission |
| `GET` | `/api/groups/{group_id}/permissions/{user_id}` | groups | List a user's permissions for this group. |
| `PUT` | `/api/groups/{group_id}/permissions/{user_id}` | groups | Update a user's permission for this group. |
| `DELETE` | `/api/groups/{group_id}/permissions/{user_id}` | groups | Delete a permission |
| `GET` | `/api/groups/{group_id}/projects` | groups | Get all projects in a group |
| `GET` | `/api/groups/{group_id}/roles` | groups | Get list of group roles |
| `POST` | `/api/groups/{group_id}/roles` | groups | Add a role to the pool of roles in a group |
| `GET` | `/api/groups/{group_id}/roles/{role_id}` | groups | Return the role identified by the RoleId |
| `DELETE` | `/api/groups/{group_id}/roles/{role_id}` | groups | Remove the role from the group |
| `GET` | `/api/jobs` | jobs | Return all jobs |
| `POST` | `/api/jobs/add` | jobs | Add a job |
| `POST` | `/api/jobs/ask` | jobs | Ask the queue a question |
| `POST` | `/api/jobs/ask/{job_state}` | jobs | Ask job count by state |
| `PUT` | `/api/jobs/cancel/bulk` | jobs | Cancel Jobs |
| `POST` | `/api/jobs/determine_provider` | jobs | Determine the effective compute provider for a proposed job. |
| `GET` | `/api/jobs/next` | jobs | Get the next job in the queue |
| `PUT` | `/api/jobs/priority` | jobs | Update a job priority. |
| `POST` | `/api/jobs/reap` | jobs | Reap stale jobs |
| `PUT` | `/api/jobs/retry/bulk` | jobs | Retry Jobs |
| `GET` | `/api/jobs/stats` | jobs | Get stats about all current jobs |
| `GET` | `/api/jobs/{job_id}` | jobs | Get job details |
| `PUT` | `/api/jobs/{job_id}` | jobs | Update a job. |
| `POST` | `/api/jobs/{job_id}/complete` | jobs | Complete a job, with information |
| `PUT` | `/api/jobs/{job_id}/complete` | jobs | Complete a job, with information. |
| `GET` | `/api/jobs/{job_id}/config.json` | jobs | Get a job's config |
| `GET` | `/api/jobs/{job_id}/detail` | jobs | Get job container details |
| `PUT` | `/api/jobs/{job_id}/heartbeat` | jobs | Heartbeat a running job to update its modified timestamp. |
| `GET` | `/api/jobs/{job_id}/logs` | jobs | Get job logs |
| `POST` | `/api/jobs/{job_id}/logs` | jobs | Add logs to a job. |
| `GET` | `/api/jobs/{job_id}/logs/html` | jobs | Get Logs Html |
| `GET` | `/api/jobs/{job_id}/logs/text` | jobs | Get Logs Text |
| `POST` | `/api/jobs/{job_id}/prepare-complete` | jobs | Create a ticket for completing a job, with id and status. |
| `PUT` | `/api/jobs/{job_id}/prepare-complete` | jobs | Create a ticket for completing a job, with id and status. |
| `PUT` | `/api/jobs/{job_id}/profile` | jobs | Update profile information on a job. (e.g. machine type, etc) |
| `POST` | `/api/jobs/{job_id}/retry` | jobs | Retry a job. |
| `GET` | `/api/jupyterlab_servers` | jupyterlab_servers | Find All |
| `POST` | `/api/jupyterlab_servers` | jupyterlab_servers | Create Jupyterlab Server |
| `GET` | `/api/jupyterlab_servers/server_options` | jupyterlab_servers | Get Server Options |
| `POST` | `/api/jupyterlab_servers/server_options` | jupyterlab_servers | Create Server Options |
| `GET` | `/api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}` | jupyterlab_servers | Get Server Option By Id |
| `PUT` | `/api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}` | jupyterlab_servers | Modify Server Options |
| `DELETE` | `/api/jupyterlab_servers/server_options/{jupyterlab_server_option_id}` | jupyterlab_servers | Delete Server Options |
| `GET` | `/api/jupyterlab_servers/status` | jupyterlab_servers | Get Status By Ids |
| `GET` | `/api/jupyterlab_servers/{jupyterlab_server_id}` | jupyterlab_servers | Get jupyterlab server |
| `PUT` | `/api/jupyterlab_servers/{jupyterlab_server_id}` | jupyterlab_servers | Update a jupyterlab server |
| `DELETE` | `/api/jupyterlab_servers/{jupyterlab_server_id}` | jupyterlab_servers | Delete |
| `GET` | `/api/jupyterlab_servers/{jupyterlab_server_id}/data` | jupyterlab_servers | Download Jupyterlab Server Data |
| `POST` | `/api/jupyterlab_servers/{jupyterlab_server_id}/data` | jupyterlab_servers | Upload Jupyterlab Server Data |
| `GET` | `/api/jupyterlab_servers/{jupyterlab_server_id}/data/ticket` | jupyterlab_servers | Get Jupyterlab Server Download Ticket |
| `PUT` | `/api/jupyterlab_servers/{jupyterlab_server_id}/start` | jupyterlab_servers | Start By Id |
| `PUT` | `/api/jupyterlab_servers/{jupyterlab_server_id}/stop` | jupyterlab_servers | Stop By Id |
| `GET` | `/api/jupyterlab_servers/{jupyterlab_server_id}/users/{user_id}/system` | jupyterlab_servers | Get Server System Info |
| `GET` | `/api/metrics` | metrics | Get all metrics. |
| `GET` | `/api/modalities` | modalities | List all modalities. |
| `POST` | `/api/modalities` | modalities | Create a new modality. |
| `GET` | `/api/modalities/{modalityId}` | modalities | Get a modality's classification specification |
| `PUT` | `/api/modalities/{modalityId}` | modalities | Replace modality |
| `DELETE` | `/api/modalities/{modalityId}` | modalities | Delete a modality |
| `POST` | `/api/clean-packfiles` | packfiles | Clean up expired upload tokens and invalid token directories. |
| `PUT` | `/api/permissions/check` | permissions | Check Actions |
| `GET` | `/api/permissions/check/{action}` | permissions | Check Single Action |
| `GET` | `/api/permissions/self` | permissions | Get User Permissions |
| `GET` | `/api/projects` | projects | Get a list of projects |
| `POST` | `/api/projects` | projects | Create a new project |
| `DELETE` | `/api/projects` | projects | Delete multiple projects by ID list |
| `GET` | `/api/projects/catalog-list` | projects | Catalog List |
| `GET` | `/api/projects/catalog-list-filter-options` | projects | Get all filter options for sharing a project |
| `GET` | `/api/projects/groups` | projects | List all groups which have a project in them |
| `GET` | `/api/projects/labels` | projects | Get a list of projects labels |
| `POST` | `/api/projects/recalc` | projects | Recalculate all sessions against their project templates. |
| `GET` | `/api/projects/{cid}/analyses` | projects | Get analyses for a(n) project. |
| `POST` | `/api/projects/{cid}/analyses` | projects | Create an analysis and upload files. |
| `GET` | `/api/projects/{cid}/analyses/{analysis_id}` | projects | Get an analysis. |
| `PUT` | `/api/projects/{cid}/analyses/{analysis_id}` | projects | Modify an analysis. |
| `DELETE` | `/api/projects/{cid}/analyses/{analysis_id}` | projects | Delete an analysis |
| `POST` | `/api/projects/{cid}/analyses/{analysis_id}/files` | projects | Upload an output file to an analysis. *(deprecated)* |
| `GET` | `/api/projects/{cid}/analyses/{analysis_id}/files/{filename}` | projects | Download analysis outputs with filter. *(deprecated)* |
| `GET` | `/api/projects/{cid}/analyses/{analysis_id}/files/{filename}/info` | projects | Get file info from a(n) project *(deprecated)* |
| `GET` | `/api/projects/{cid}/analyses/{analysis_id}/inputs/{filename}` | projects | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/projects/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | projects | Get file info from a(n) project *(deprecated)* |
| `DELETE` | `/api/projects/{cid}/analyses/{analysis_id}/notes/{note_id}` | projects | Remove a note from a(n) project analysis. |
| `PUT` | `/api/projects/{cid}/files/{filename}` | projects | Modify a file's attributes |
| `DELETE` | `/api/projects/{cid}/files/{filename}` | projects | Delete a file |
| `PATCH` | `/api/projects/{cid}/files/{filename}/classification` | projects | Update classification for a particular file. |
| `GET` | `/api/projects/{cid}/files/{filename}/info` | projects | Get info for a particular file. |
| `PATCH` | `/api/projects/{cid}/files/{filename}/info` | projects | Update info for a particular file. |
| `PATCH` | `/api/projects/{cid}/info` | projects | Update or replace info for a(n) project. |
| `GET` | `/api/projects/{cid}/inputs/{filename}/info` | projects | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/projects/{cid}/notes/{note_id}` | projects | Get a note of a(n) project. |
| `PUT` | `/api/projects/{cid}/notes/{note_id}` | projects | Update a note of a(n) project. |
| `DELETE` | `/api/projects/{cid}/notes/{note_id}` | projects | Remove a note from a(n) project |
| `GET` | `/api/projects/{cid}/settings/deid_profile` | projects | Get deid_profile for project |
| `POST` | `/api/projects/{cid}/tags` | projects | Add a tag to a(n) project. |
| `PATCH` | `/api/projects/{cid}/tags` | projects | Add multiple tags to a(n) project |
| `DELETE` | `/api/projects/{cid}/tags` | projects | Delete multiple tags from a(n) project |
| `GET` | `/api/projects/{cid}/tags/{value}` | projects | Get the value of a tag, by name. |
| `PUT` | `/api/projects/{cid}/tags/{value}` | projects | Rename a tag. |
| `DELETE` | `/api/projects/{cid}/tags/{value}` | projects | Delete a tag |
| `GET` | `/api/projects/{cid}/{sub_cname}/analyses` | projects | Get nested analyses from projects |
| `POST` | `/api/projects/{container_id}/analyses/{analysis_id}/notes` | projects | Add a note to a(n) project analysis. |
| `POST` | `/api/projects/{container_id}/files` | projects | Upload a file to a(n) project. |
| `GET` | `/api/projects/{container_id}/files/{file_name}` | projects | Download a file. |
| `POST` | `/api/projects/{container_id}/notes` | projects | Add a note to a(n) project. |
| `GET` | `/api/projects/{container_id}/settings` | projects | Get a(n) project settings |
| `PUT` | `/api/projects/{container_id}/settings` | projects | Modify a(n) project settings |
| `GET` | `/api/projects/{project_id}` | projects | Get a single project |
| `PUT` | `/api/projects/{project_id}` | projects | Update a project |
| `DELETE` | `/api/projects/{project_id}` | projects | Delete a project |
| `GET` | `/api/projects/{project_id}/acquisitions` | projects | List all acquisitions for the given project. |
| `GET` | `/api/projects/{project_id}/copies` | projects | Copy By Reference List |
| `POST` | `/api/projects/{project_id}/copy` | projects | Copy By Reference |
| `GET` | `/api/projects/{project_id}/copy/{snapshot_id}/status` | projects | Copy By Reference Status |
| `GET` | `/api/projects/{project_id}/delete-status` | projects | Get project deletion status |
| `GET` | `/api/projects/{project_id}/jobs` | projects | Find Jobs |
| `POST` | `/api/projects/{project_id}/ldap-sync` | projects | Sync Permissions |
| `POST` | `/api/projects/{project_id}/lock` | projects | Project Lock |
| `GET` | `/api/projects/{project_id}/packfile-end` | projects | End a packfile upload |
| `POST` | `/api/projects/{project_id}/packfile-end` | projects | Post Packfile End |
| `POST` | `/api/projects/{project_id}/packfile-start` | projects | Start a packfile upload to project |
| `POST` | `/api/projects/{project_id}/permissions` | projects | Add a permission |
| `GET` | `/api/projects/{project_id}/permissions/{uid}` | projects | List a user's permissions for this project. |
| `PUT` | `/api/projects/{project_id}/permissions/{uid}` | projects | Update a user's permission for this project. |
| `DELETE` | `/api/projects/{project_id}/permissions/{uid}` | projects | Delete a permission |
| `POST` | `/api/projects/{project_id}/recalc` | projects | Currently does nothing--will eventually calculate if sessions in the project satisfy the template. |
| `GET` | `/api/projects/{project_id}/rules` | projects | List all rules for a project. |
| `POST` | `/api/projects/{project_id}/rules` | projects | Create a new rule for a project. |
| `GET` | `/api/projects/{project_id}/rules/{rule_id}` | projects | Get a project rule. |
| `PUT` | `/api/projects/{project_id}/rules/{rule_id}` | projects | Update a rule on a project. |
| `DELETE` | `/api/projects/{project_id}/rules/{rule_id}` | projects | Remove a project rule. |
| `GET` | `/api/projects/{project_id}/sessions` | projects | List all sessions for the given project. |
| `GET` | `/api/projects/{project_id}/subjects` | projects | List all subjects for the given project. |
| `POST` | `/api/projects/{project_id}/template` | projects | Set the session template for a project. |
| `DELETE` | `/api/projects/{project_id}/template` | projects | Remove the session template for a project. |
| `POST` | `/api/projects/{project_id}/unlock` | projects | Project Unlock |
| `POST` | `/api/projects/{project_id}/upsert-file` | projects | Upsert File |
| `POST` | `/api/projects/{project_id}/upsert-hierarchy` | projects | Create or update subject, session and acquisition containers in the project. |
| `GET` | `/api/read_task_protocols` | read_task_protocols | Find All Protocols |
| `POST` | `/api/read_task_protocols` | read_task_protocols | Create |
| `GET` | `/api/read_task_protocols/{protocol_id}` | read_task_protocols | Get By Id |
| `PUT` | `/api/read_task_protocols/{protocol_id}` | read_task_protocols | Modify |
| `DELETE` | `/api/read_task_protocols/{protocol_id}` | read_task_protocols | Delete |
| `GET` | `/api/read_task_protocols/{protocol_id}/dry_run_delete` | read_task_protocols | Dry Run Delete |
| `GET` | `/api/readertasks` | reader_tasks | Find All Tasks |
| `POST` | `/api/readertasks` | reader_tasks | Create |
| `POST` | `/api/readertasks/batch` | reader_tasks | Create_batch |
| `POST` | `/api/readertasks/batch/clone` | reader_tasks | Create batch of clone tasks |
| `POST` | `/api/readertasks/batch/dryrun` | reader_tasks | Get details about a dry run of a given batch input |
| `POST` | `/api/readertasks/batch/duplicates` | reader_tasks | Return a list of potential duplicates of the provided batch of tasks |
| `POST` | `/api/readertasks/batch/parents` | reader_tasks | Count containers that match the provided filter |
| `GET` | `/api/readertasks/project/{project_id}` | reader_tasks | Find All |
| `GET` | `/api/readertasks/task_types` | reader_tasks | Get Reader Task Types |
| `GET` | `/api/readertasks/{task_id}` | reader_tasks | Get By Id |
| `PUT` | `/api/readertasks/{task_id}` | reader_tasks | Modify |
| `DELETE` | `/api/readertasks/{task_id}` | reader_tasks | Delete |
| `GET` | `/api/readertasks/{task_id}/annotations` | reader_tasks | Get all annotations for a reader task |
| `GET` | `/api/readertasks/{task_id}/details` | reader_tasks | Get Reader Task Details |
| `GET` | `/api/readertasks/{task_id}/launch_viewer` | reader_tasks | Get Task Viewer Context |
| `GET` | `/api/report/accesslog` | reports | Get a report of access log entries for the given parameters |
| `GET` | `/api/report/accesslog/types` | reports | Get the list of types of access log entries |
| `GET` | `/api/report/daily-usage` | reports | Get a daily usage report for the given month. |
| `GET` | `/api/report/daily-usage-range` | reports | DEPRECATED - Use /reports/usage-summary instead *(deprecated)* |
| `GET` | `/api/report/legacy-usage` | reports | Get a usage report for the site grouped by month or project *(deprecated)* |
| `GET` | `/api/report/project` | reports | Get project report |
| `GET` | `/api/report/site` | reports | Get the site report |
| `GET` | `/api/report/usage` | reports | Get a usage report for the given month. |
| `GET` | `/api/report/usage-summary` | reports | Get aggregated usage data |
| `GET` | `/api/report/usage/availability` | reports | Get year/month combinations where report data is available. |
| `GET` | `/api/report/usage/collect` | reports | Collect daily usage statistics. |
| `POST` | `/api/lookup` | resolve | Perform path based lookup of a single node in the Flywheel hierarchy |
| `POST` | `/api/resolve` | resolve | Perform path based lookup of nodes in the Flywheel hierarchy |
| `GET` | `/api/roles` | roles | Get list of all roles |
| `POST` | `/api/roles` | roles | Add a new role |
| `GET` | `/api/roles/actions` | roles | Get Actions |
| `GET` | `/api/roles/{role_id}` | roles | Return the role identified by the RoleId |
| `PUT` | `/api/roles/{role_id}` | roles | Update the role identified by RoleId |
| `DELETE` | `/api/roles/{role_id}` | roles | Delete the role |
| `GET` | `/api/sessions` | sessions | Get a list of sessions |
| `POST` | `/api/sessions` | sessions | Create a new session |
| `DELETE` | `/api/sessions` | sessions | Delete multiple sessions by ID list |
| `GET` | `/api/sessions/{cid}/analyses` | sessions | Get analyses for a(n) session. |
| `POST` | `/api/sessions/{cid}/analyses` | sessions | Create an analysis and upload files. |
| `GET` | `/api/sessions/{cid}/analyses/{analysis_id}` | sessions | Get an analysis. |
| `PUT` | `/api/sessions/{cid}/analyses/{analysis_id}` | sessions | Modify an analysis. |
| `DELETE` | `/api/sessions/{cid}/analyses/{analysis_id}` | sessions | Delete an analysis |
| `POST` | `/api/sessions/{cid}/analyses/{analysis_id}/files` | sessions | Upload an output file to an analysis. *(deprecated)* |
| `GET` | `/api/sessions/{cid}/analyses/{analysis_id}/files/{filename}` | sessions | Download analysis outputs with filter. *(deprecated)* |
| `GET` | `/api/sessions/{cid}/analyses/{analysis_id}/files/{filename}/info` | sessions | Get file info from a(n) session *(deprecated)* |
| `GET` | `/api/sessions/{cid}/analyses/{analysis_id}/inputs/{filename}` | sessions | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/sessions/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | sessions | Get file info from a(n) session *(deprecated)* |
| `DELETE` | `/api/sessions/{cid}/analyses/{analysis_id}/notes/{note_id}` | sessions | Remove a note from a(n) session analysis. |
| `PUT` | `/api/sessions/{cid}/files/{filename}` | sessions | Modify a file's attributes |
| `DELETE` | `/api/sessions/{cid}/files/{filename}` | sessions | Delete a file |
| `PATCH` | `/api/sessions/{cid}/files/{filename}/classification` | sessions | Update classification for a particular file. |
| `GET` | `/api/sessions/{cid}/files/{filename}/info` | sessions | Get info for a particular file. |
| `PATCH` | `/api/sessions/{cid}/files/{filename}/info` | sessions | Update info for a particular file. |
| `PATCH` | `/api/sessions/{cid}/info` | sessions | Update or replace info for a(n) session. |
| `GET` | `/api/sessions/{cid}/inputs/{filename}/info` | sessions | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/sessions/{cid}/notes/{note_id}` | sessions | Get a note of a(n) session. |
| `PUT` | `/api/sessions/{cid}/notes/{note_id}` | sessions | Update a note of a(n) session. |
| `DELETE` | `/api/sessions/{cid}/notes/{note_id}` | sessions | Remove a note from a(n) session |
| `POST` | `/api/sessions/{cid}/tags` | sessions | Add a tag to a(n) session. |
| `PATCH` | `/api/sessions/{cid}/tags` | sessions | Add multiple tags to a(n) session |
| `DELETE` | `/api/sessions/{cid}/tags` | sessions | Delete multiple tags from a(n) session |
| `GET` | `/api/sessions/{cid}/tags/{value}` | sessions | Get the value of a tag, by name. |
| `PUT` | `/api/sessions/{cid}/tags/{value}` | sessions | Rename a tag. |
| `DELETE` | `/api/sessions/{cid}/tags/{value}` | sessions | Delete a tag |
| `GET` | `/api/sessions/{cid}/{sub_cname}/analyses` | sessions | Get nested analyses from sessions |
| `POST` | `/api/sessions/{container_id}/analyses/{analysis_id}/notes` | sessions | Add a note to a(n) session analysis. |
| `POST` | `/api/sessions/{container_id}/files` | sessions | Upload a file to a(n) session. |
| `GET` | `/api/sessions/{container_id}/files/{file_name}` | sessions | Download a file. |
| `POST` | `/api/sessions/{container_id}/notes` | sessions | Add a note to a(n) session. |
| `GET` | `/api/sessions/{session_id}` | sessions | Get a single session |
| `PUT` | `/api/sessions/{session_id}` | sessions | Update a session |
| `DELETE` | `/api/sessions/{session_id}` | sessions | Delete a session |
| `GET` | `/api/sessions/{session_id}/acquisitions` | sessions | List acquisitions in a session |
| `POST` | `/api/sessions/{session_id}/copy` | sessions | Smart copy a session |
| `GET` | `/api/sessions/{session_id}/jobs` | sessions | Return any jobs that use inputs from this session |
| `GET` | `/api/sessions/{session_id}/subject` | sessions | Get subject |
| `POST` | `/api/sessions/{session_id}/subject/info` | sessions | Modify subject info *(deprecated)* |
| `PATCH` | `/api/sessions/{session_id}/subject/info` | sessions | Modify subject info |
| `GET` | `/api/site/bookmark-list` | site | Get Bookmark List |
| `PUT` | `/api/site/bookmark-list` | site | Modify Bookmark List |
| `GET` | `/api/site/providers` | site | Return a list of all providers on the site |
| `POST` | `/api/site/providers` | site | Add a new provider |
| `GET` | `/api/site/providers/{provider_id}` | site | Return the provider identified by ProviderId |
| `PUT` | `/api/site/providers/{provider_id}` | site | Update the provider identified by ProviderId |
| `DELETE` | `/api/site/providers/{provider_id}` | site | Delete the provider identified by ProviderId |
| `GET` | `/api/site/providers/{provider_id}/config` | site | Return the configuration for provider identified by ProviderId |
| `GET` | `/api/site/rules` | site | List all site rules. |
| `POST` | `/api/site/rules` | site | Create a new site rule. |
| `GET` | `/api/site/rules/{rule_id}` | site | Get a site rule. |
| `PUT` | `/api/site/rules/{rule_id}` | site | Update a site rule. |
| `DELETE` | `/api/site/rules/{rule_id}` | site | Remove a site rule. |
| `GET` | `/api/site/settings` | site | Return administrative site settings |
| `PUT` | `/api/site/settings` | site | Update administrative site settings |
| `POST` | `/api/storage/files` | storage | Upload a file directly to storage |
| `GET` | `/api/storage/files/{storage_file_id}` | storage | Download a file from storage |
| `DELETE` | `/api/storage/files/{storage_file_id}` | storage | Delete a file from storage |
| `POST` | `/api/storage/files/{storage_file_id}/ticket` | storage | Create a ticket for unauthenticated download |
| `GET` | `/api/subjects` | subjects | Get a list of subjects |
| `POST` | `/api/subjects` | subjects | Create a new subject |
| `DELETE` | `/api/subjects` | subjects | Delete multiple subjects by ID list |
| `POST` | `/api/subjects/master-code` | subjects | Request a master subject code for the given patient |
| `GET` | `/api/subjects/master-code/{code}` | subjects | Verify that the given master subject code exists or not |
| `GET` | `/api/subjects/{cid}/analyses` | subjects | Get analyses for a(n) subject. |
| `POST` | `/api/subjects/{cid}/analyses` | subjects | Create an analysis and upload files. |
| `GET` | `/api/subjects/{cid}/analyses/{analysis_id}` | subjects | Get an analysis. |
| `PUT` | `/api/subjects/{cid}/analyses/{analysis_id}` | subjects | Modify an analysis. |
| `DELETE` | `/api/subjects/{cid}/analyses/{analysis_id}` | subjects | Delete an analysis |
| `POST` | `/api/subjects/{cid}/analyses/{analysis_id}/files` | subjects | Upload an output file to an analysis. *(deprecated)* |
| `GET` | `/api/subjects/{cid}/analyses/{analysis_id}/files/{filename}` | subjects | Download analysis outputs with filter. *(deprecated)* |
| `GET` | `/api/subjects/{cid}/analyses/{analysis_id}/files/{filename}/info` | subjects | Get file info from a(n) subject *(deprecated)* |
| `GET` | `/api/subjects/{cid}/analyses/{analysis_id}/inputs/{filename}` | subjects | Download analysis inputs with filter. *(deprecated)* |
| `GET` | `/api/subjects/{cid}/analyses/{analysis_id}/inputs/{filename}/info` | subjects | Get file info from a(n) subject *(deprecated)* |
| `DELETE` | `/api/subjects/{cid}/analyses/{analysis_id}/notes/{note_id}` | subjects | Remove a note from a(n) subject analysis. |
| `PUT` | `/api/subjects/{cid}/files/{filename}` | subjects | Modify a file's attributes |
| `DELETE` | `/api/subjects/{cid}/files/{filename}` | subjects | Delete a file |
| `PATCH` | `/api/subjects/{cid}/files/{filename}/classification` | subjects | Update classification for a particular file. |
| `GET` | `/api/subjects/{cid}/files/{filename}/info` | subjects | Get info for a particular file. |
| `PATCH` | `/api/subjects/{cid}/files/{filename}/info` | subjects | Update info for a particular file. |
| `PATCH` | `/api/subjects/{cid}/info` | subjects | Update or replace info for a(n) subject. |
| `GET` | `/api/subjects/{cid}/inputs/{filename}/info` | subjects | Get info for a particular file. *(deprecated)* |
| `GET` | `/api/subjects/{cid}/notes/{note_id}` | subjects | Get a note of a(n) subject. |
| `PUT` | `/api/subjects/{cid}/notes/{note_id}` | subjects | Update a note of a(n) subject. |
| `DELETE` | `/api/subjects/{cid}/notes/{note_id}` | subjects | Remove a note from a(n) subject |
| `POST` | `/api/subjects/{cid}/tags` | subjects | Add a tag to a(n) subject. |
| `PATCH` | `/api/subjects/{cid}/tags` | subjects | Add multiple tags to a(n) subject |
| `DELETE` | `/api/subjects/{cid}/tags` | subjects | Delete multiple tags from a(n) subject |
| `GET` | `/api/subjects/{cid}/tags/{value}` | subjects | Get the value of a tag, by name. |
| `PUT` | `/api/subjects/{cid}/tags/{value}` | subjects | Rename a tag. |
| `DELETE` | `/api/subjects/{cid}/tags/{value}` | subjects | Delete a tag |
| `GET` | `/api/subjects/{cid}/{sub_cname}/analyses` | subjects | Get nested analyses from subjects |
| `POST` | `/api/subjects/{container_id}/analyses/{analysis_id}/notes` | subjects | Add a note to a(n) subject analysis. |
| `POST` | `/api/subjects/{container_id}/files` | subjects | Upload a file to a(n) subject. |
| `GET` | `/api/subjects/{container_id}/files/{file_name}` | subjects | Download a file. |
| `POST` | `/api/subjects/{container_id}/notes` | subjects | Add a note to a(n) subject. |
| `GET` | `/api/subjects/{subject_id}` | subjects | Get a single subject |
| `PUT` | `/api/subjects/{subject_id}` | subjects | Update a subject |
| `DELETE` | `/api/subjects/{subject_id}` | subjects | Delete a subject |
| `POST` | `/api/subjects/{subject_id}/copy` | subjects | Smart copy a subject |
| `GET` | `/api/subjects/{subject_id}/sessions` | subjects | List sessions of a subject |
| `GET` | `/api/system` | system | Get all |
| `GET` | `/api/system/ready` | system | Get ready |
| `POST` | `/api/tree` | tree | Query a portion of the flywheel hierarchy, returning only the requested fields. |
| `GET` | `/api/tree/graph` | tree | Get a description of the flywheel hiearchy |
| `POST` | `/api/uids` | uids | Check for existence of UIDs system-wide |
| `POST` | `/api/uids/projects` | uids | Check uids with projects |
| `POST` | `/api/upload/complete-azure-multipart` | upload | Complete Azure Multipart Upload |
| `POST` | `/api/upload/complete-s3-multipart` | upload | Complete S3 multipart signed url upload |
| `PUT` | `/api/upload/fs-file` | upload | Upload file to local filesystem storage provider |
| `POST` | `/api/upload/label` | upload | Multipart form upload with N file fields, each with their desired filename. |
| `POST` | `/api/upload/reaper` | upload | Bottom-up UID matching of Multipart form upload with N file fields, each with their desired filename. |
| `POST` | `/api/upload/signed-url` | upload | Create new signed upload URL |
| `POST` | `/api/upload/signed-url/cleanup` | upload | Cleanup unused file blob previously uploaded using signed URL |
| `POST` | `/api/upload/uid` | upload | Multipart form upload with N file fields, each with their desired filename. |
| `GET` | `/api/users` | users | Return a list of all users |
| `POST` | `/api/users` | users | Add a new user |
| `GET` | `/api/users/self` | users | Get information about the current user |
| `GET` | `/api/users/self/avatar` | users | Get the avatar of the current user |
| `GET` | `/api/users/self/info` | users | Get info of the current user |
| `POST` | `/api/users/self/info` | users | Update or replace info for the current user. *(deprecated)* |
| `PATCH` | `/api/users/self/info` | users | Update or replace info for the current user. |
| `GET` | `/api/users/self/jobs` | users | Return list of jobs created by the current user |
| `POST` | `/api/users/self/key` | users | Generates user api key |
| `DELETE` | `/api/users/self/key/{id_}` | users | Delete User Api Key |
| `GET` | `/api/users/self/mfa-setups` | users | Get Mfa Setups |
| `POST` | `/api/users/self/mfa-setups` | users | Create Mfa Setup |
| `PATCH` | `/api/users/self/mfa-setups` | users | Update Mfa Setup |
| `DELETE` | `/api/users/self/mfa-setups` | users | Delete Mfa Setup |
| `POST` | `/api/users/self/mfa-verifications` | users | Create Mfa Verification |
| `PUT` | `/api/users/self/preferences` | users | Change user preferences |
| `POST` | `/api/users/self/visited_projects/{project_id}` | users | Add project id to list of users recently visited projects |
| `PUT` | `/api/users/sync/{cid}` | users | Sync a center user to enterprise (Sync service use ONLY) |
| `DELETE` | `/api/users/{UserId}` | users | Delete a user |
| `PUT` | `/api/users/{uid}` | users | Update the specified user |
| `GET` | `/api/users/{uid}/acquisitions` | users | Get all acquisitions that belong to the given user. |
| `GET` | `/api/users/{uid}/groups` | users | List all groups the specified user is a member of |
| `GET` | `/api/users/{uid}/projects` | users | Get all projects that belong to the given user. |
| `POST` | `/api/users/{uid}/reset-registration` | users | Reset User Registration *(deprecated)* |
| `GET` | `/api/users/{uid}/sessions` | users | Get all sessions that belong to the given user. |
| `GET` | `/api/users/{uid}/{cname}` | users | Get All For User *(deprecated)* |
| `GET` | `/api/users/{user_id}` | users | Get information about the specified user |
| `GET` | `/api/users/{user_id}/avatar` | users | Get the avatar of the specified user |
| `GET` | `/api/users/{user_id}/collections` | users | Get all collections that belong to the given user. |
| `GET` | `/api/viewerconfigs` | viewer_configs | Find all viewer configs |
| `POST` | `/api/viewerconfigs` | viewer_configs | Create viewer config |
| `GET` | `/api/viewerconfigs/{viewer_config_id}` | viewer_configs | Get viewer config |
| `PUT` | `/api/viewerconfigs/{viewer_config_id}` | viewer_configs | Modify viewer config |
| `DELETE` | `/api/viewerconfigs/{viewer_config_id}` | viewer_configs | Delete viewer config |
| `GET` | `/api/viewerconfigs/{viewer_config_id}/config` | viewer_configs | Get raw config of viewer_config |
| `GET` | `/api/views/columns` | views | Return a list of all known column aliases for use in data views |
| `POST` | `/api/views/data` | views | Execute an ad-hoc view, returning data in the preferred format. |
| `POST` | `/api/views/queue` | views | Execute an ad-hoc view, returning a reference to the created data view execution. |
| `POST` | `/api/views/save` | views | Execute a view, saving data to the target container / file |
| `GET` | `/api/views/{view_id}` | views | Return the view identified by ViewId |
| `PUT` | `/api/views/{view_id}` | views | Update the view identified by ViewId |
| `DELETE` | `/api/views/{view_id}` | views | Delete a data view |
| `GET` | `/api/views/{view_id}/data` | views | Execute a view, returning data in the preferred format. *(deprecated)* |
| `POST` | `/api/views/{view_id}/queue` | views | Execute a view, returning a reference to the created data view execution. |
| `PATCH` | `/api/{container_type}/info/cleanup/{path}` | {container_type} | Remove a custom field from all applicable containers |
