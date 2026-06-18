# Flywheel Core API (/api/) — auth

Service: `core`  |  Tag: `auth`  |  Generated from OpenAPI spec.

## `GET /api/auth/status`

**Get Login status**

Get the current login status of the requestor

---

## `POST /api/login`

**Login**

**Request Body** *(required)*
`application/json`: object(auth_type: string, code: string)

---

## `GET /api/login/auth0`

**Record Auth0 login and return the current user record**

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `authorization` | header | no | `string` |  |

---

## `POST /api/login/basic`

**Login Basic**

**Request Body** *(required)*
`application/json`: object(auth_type: string, email: string, password: string)

---

## `POST /api/logout`

**Logout**

Log out

**Parameters**

| Name | In | Required | Type | Description |
|---|---|---|---|---|
| `refresh_only` | query | no | `boolean` |  |

---
