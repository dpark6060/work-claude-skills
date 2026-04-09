# Flywheel Core API (/api/) — dataexplorer

Service: `core`  |  Tag: `dataexplorer`  |  Generated from OpenAPI spec.

## `POST /api/dataexplorer/facets`

**Get Facets**

handlers.dataexplorerhander.DataExplorerHandler.get_facets)

**Request Body**
`application/json`: object(return_type: enum(file | acquisition | session | analysis | project | subject), structured_query: string, search_string: string, filters: array[object], all_data: boolean, ...)

---

## `POST /api/dataexplorer/index/fields` *(deprecated)*

**Index Fields**

handlers.dataexplorerhander.DataExplorerHandler.index_field_names)

---

## `GET /api/dataexplorer/mapped_fields`

**Get fields mapped for search**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `path` | query | no | `string` | Dot-separated subfield to drill down to |

---

## `GET /api/dataexplorer/queries`

**Get Queries**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `exhaustive` | query | no | `boolean` | Return all queries, Admin only |
| `filter` | query | no | `string` | Comma separated filters to apply. Commas not used as separators must be escaped with backslash '\'. (e.g. label=my-label |
| `sort` | query | no | `string` | The sort fields and order. (e.g. label:asc,created:desc) |
| `limit` | query | no | `integer` | The maximum number of entries to return. |
| `skip` | query | no | `integer` | The number of entries to skip. |
| `page` | query | no | `integer` | The page number (i.e. skip limit*page entries) |
| `after_id` | query | no | `string` | Paginate after the given id. (Cannot be used with sort, page or skip) |
| `x-accept-feature` | header | no | `array[string]` |  |

---

## `POST /api/dataexplorer/queries`

**Save a search query**

**Request Body** *(required)*
`application/json`: object(label: string, search: object, parent: object)

---

## `DELETE /api/dataexplorer/queries/{search_id}`

**Delete a saved search**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `search_id` | path | yes | `string` |  |

---

## `GET /api/dataexplorer/queries/{sid}`

**Return a saved search query**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `sid` | path | yes | `string` |  |

---

## `PUT /api/dataexplorer/queries/{sid}`

**Replace a search query**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `sid` | path | yes | `string` |  |

**Request Body** *(required)*
`application/json`: object(label: string, search: object)

---

## `DELETE /api/dataexplorer/search`

**Delete containers by a search query**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `delete_reason` | query | no | `enum(duplicate_data | data_is_not_part_of_study | data_incomplete_or_corrupt | data_structured_incorrectly | data_has_been_exported_or_moved | container_is_empty | analysis_or_processing_failed_or_cancelled | compliance_consent_withdrawn | ...)` |  |

**Request Body** *(required)*
`application/json`: object(return_type: enum(file | acquisition | session | analysis | project | subject), structured_query: string, search_string: string, filters: array[object])

---

## `POST /api/dataexplorer/search`

**Perform a search query**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `simple` | query | no | `boolean` | Unwrap result documents into a list. |
| `size` | query | no | `integer` | The maximum number of results to return. DEPRECATED: use body parameter instead. |
| `facets` | query | no | `boolean` | Include additional statistics about the search results. Internal use only. |
| `csv` | query | no | `boolean` | Format the response as a CSV file |

**Request Body** *(required)*
`application/json`: object(return_type: enum(file | acquisition | session | analysis | project | subject), structured_query: string, search_string: string, filters: array[object], all_data: boolean, ...)

---

## `POST /api/dataexplorer/search/fields` *(deprecated)*

**Search Fields**

This endpoint is deprecated and will be removed in a future release. Use the `get_search_query_suggestions` endpoint instead.

**Request Body** *(required)*
`application/json`: object(field: string)

---

## `POST /api/dataexplorer/search/fields/aggregate`

**Aggregate Fields**

handlers.dataexplorerhander.DataExplorerHandler.aggregate_field_values)

**Request Body** *(required)*
`application/json`: object(field_name: string, search_string: string)

---

## `POST /api/dataexplorer/search/nodes`

**Get Nodes**

handlers.dataexplorerhander.DataExplorerHandler.get_nodes)

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `size` | query | no | `any` |  |

**Request Body** *(required)*
`application/json`: object(return_type: enum(file | acquisition | session | analysis | project | subject), structured_query: string, search_string: string, filters: array[object], all_data: boolean, ...)

---

## `POST /api/dataexplorer/search/parse`

**Parse a structured search query**

Validates a search query, returning any parse errors that were encountered. In the future, this endpoint may return the abstract syntax tree or evaluated query.

**Request Body** *(required)*
`application/json`: object(structured_query: string)

---

## `GET /api/dataexplorer/search/status`

**Get the status of search (Mongo Connector)**

---

## `POST /api/dataexplorer/search/suggest`

**Get suggestions for a structured search query**

Send the search query from the start of the string, and get a set of suggested replacements back. When utilizing a suggestion, the caller should replace the contents from the "from" field to the end of the string with the provided "value".

**Request Body** *(required)*
`application/json`: object(structured_query: string)

---

## `POST /api/dataexplorer/search/training`

**Save Training Set**

handlers.dataexplorerhander.DataExplorerHandler.save_training_set)

**Request Body** *(required)*
`application/json`: object(output: object, search_query: object, files: array[object], filename: string, description: string, ...)

---
