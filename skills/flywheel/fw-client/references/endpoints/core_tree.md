# Flywheel Core API (/api/) — tree

Service: `core`  |  Tag: `tree`  |  Generated from OpenAPI spec.

## `POST /api/tree`

**Query a portion of the flywheel hierarchy, returning only the requested fields.**

This is a build-your-own request endpoint that can fetch from anywhere in the hierarchy,
returning just the fields that you care about.

# Fields
Each fetch-level described must include a list of fields to return. These fields
can be anything on the container (except info), and will be included in the response
if they are present in the container.

# Joins
Children or parents can be joined as part of this request, by specifying an additional
subdocument of the given name. Check /tree/graph for a ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

**Request Body** *(required)*
`application/json`: object(groups: TreeContainerRequestSpec, projects: TreeContainerRequestSpec, subjects: TreeContainerRequestSpec, sessions: TreeContainerRequestSpec, acquisitions: TreeContainerRequestSpec, ...)

---

## `GET /api/tree/graph`

**Get a description of the flywheel hiearchy**

---
