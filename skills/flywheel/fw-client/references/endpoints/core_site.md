---
type: API Endpoint Schema
title: Core API — Site
description: Flywheel Core API (/api/) endpoint schemas covering site-level settings and storage/compute providers.
tags: [flywheel, core-api, site]
timestamp: 2026-07-15T00:00:00Z
---

# Flywheel Core API (/api/) — site

Service: `core`  |  Tag: `site`  |  Generated from OpenAPI spec.

## `GET /api/site/bookmark-list`

**Get Bookmark List**

---

## `PUT /api/site/bookmark-list`

**Modify Bookmark List**

**Request Body** *(required)*
`application/json`: array[object]

---

## `GET /api/site/providers`

**Return a list of all providers on the site**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `class` | query | no | `enum(compute | storage)` | Limit the response to the given provider class |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |

---

## `POST /api/site/providers`

**Add a new provider**

**Request Body** *(required)*
`application/json`: object(label: string, provider_class: enum(compute | storage), provider_type: enum(local | static | aws | azure | gc | s3_compat | exchange), creds: object, config: object, ...)

---

## `DELETE /api/site/providers/{provider_id}`

**Delete the provider identified by ProviderId**

Returns an empty 204 response if successful. The provider will be deleted asynchronously; if it is a storage provider, any files on the provider that have been deleted but not yet cleaned up will be hard deleted. Use the `get_provider` operation to check the deletion status.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `provider_id` | path | yes | `string` | The ID of the provider |

---

## `GET /api/site/providers/{provider_id}`

**Return the provider identified by ProviderId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `provider_id` | path | yes | `string` | The ID of the provider |

---

## `PUT /api/site/providers/{provider_id}`

**Update the provider identified by ProviderId**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `provider_id` | path | yes | `string` | The ID of the provider |

**Request Body** *(required)*
`application/json`: object(label: string, creds: object, config: object)

---

## `GET /api/site/providers/{provider_id}/config`

**Return the configuration for provider identified by ProviderId**

The returned configuration will be redacted, with any privileged values replaced with null.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `provider_id` | path | yes | `string` | The ID of the provider |

---

## `GET /api/site/rules`

**List all site rules.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `limit` | query | no | `integer` |  |
| `after_id` | query | no | `string` |  |
| `name` | query | no | `string` |  |

---

## `POST /api/site/rules`

**Create a new site rule.**

**Request Body** *(required)*
`application/json`: object(project_id: string, gear_id: string, role_id: string, name: string, config: object, ...)

---

## `DELETE /api/site/rules/{rule_id}`

**Remove a site rule.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_id` | path | yes | `string` |  |

---

## `GET /api/site/rules/{rule_id}`

**Get a site rule.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_id` | path | yes | `string` |  |

---

## `PUT /api/site/rules/{rule_id}`

**Update a site rule.**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `rule_id` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(gear_id: string, role_id: string, name: string, config: object, fixed_inputs: array[any], ...)

---

## `GET /api/site/settings`

**Return administrative site settings**

Returns the site settings, which includes center-pays gear list. If the site
settings have never been created, then center_gears will be null, rather than an
empty list.

---

## `PUT /api/site/settings`

**Update administrative site settings**

**Request Body** *(required)*
`application/json`: object(center_gears: array[string], providers: object, viewer_apps: array[object], deid_profile: any, mfa: object)

---
