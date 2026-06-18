# Flywheel Core API (/api/) — resolve

Service: `core`  |  Tag: `resolve`  |  Generated from OpenAPI spec.

## `POST /api/lookup`

**Perform path based lookup of a single node in the Flywheel hierarchy**

This will perform a deep lookup of a node. See /resolve for more details.

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `full_tree` | query | no | `boolean` |  |
| `exhaustive` | query | no | `boolean` |  |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |

**Request Body** *(required)*
`application/json`: object(path: array[string])

---

## `POST /api/resolve`

**Perform path based lookup of nodes in the Flywheel hierarchy**

This will perform a deep lookup of a node (i.e. group/project/session/acquisition) and its children,
including any files. The query path is an array of strings in the following order (by default):

  * group id
  * project label
  * session label
  * acquisition label

Additionally, analyses for project/session/acquisition nodes can be resolved by inserting the literal
string `"analyses"`. e.g. `['scitran', 'MyProject', 'analyses']`.

Files for projects, sessions, acquisitions and analyses can b ...

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `full_tree` | query | no | `boolean` | Parse full download style paths (e.g. group/PROJECTS/project_label/SUBJECTS/...) |
| `minattr` | query | no | `boolean` | Return only minimal attributes |
| `exhaustive` | query | no | `boolean` | Set to return a complete list regardless of permissions |
| `include_all_info` | query | no | `boolean` | Include all info in returned objects |

**Request Body** *(required)*
`application/json`: object(path: array[string])

---
