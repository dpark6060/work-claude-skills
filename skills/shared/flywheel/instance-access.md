---
type: Reference
title: Flywheel Instance Access
description: Which Flywheel instances can be inspected live, where the credentials live, how to use them without handling raw keys, and the read-only proxy trick when no key exists.
tags: [flywheel, api-key, instances, credentials, fw-config]
timestamp: 2026-08-17T00:00:00Z
---

# Flywheel Instance Access

Which live instances are reachable, and how to act on one. **Check here before
declaring "there is no API key for instance X"** — a 2026-07-29 sweep wrongly assumed
no GE key existed and dropped a question it could have answered.

## Contents
- Where credentials live
- Do not read the file
- Using a profile
- No profile for the host?

---

## Where credentials live

`~/.fw/config.yml`, written and managed by the `flyw` CLI. Structure:

```yaml
default_profile: default
profiles:
- api_key: "<host>:<secret>"
  id: davidparker@flywheel.io
  is_admin: true
  is_drone: false
  name: default
  compat: {...}          # or null
```

Three things surprise people:

- **`profiles:` is a LIST, not a map.** Indexing it by name fails.
- **The host is embedded in `api_key`**, left of the first colon. There is no
  separate `host`/`url` field.
- **`name` is a nickname, not a host** — `ge`, `nacc`, `upenn`, `ucsf`, `florey`,
  `naccsb`, `unsw`, `uscdni`, `latest`, `pubdemo`. Don't infer the instance from it.

26 profiles as of 2026-08-17, spanning dev/latest, customer prod, and demo sites.

---

## Do not read the file

**Every `api_key` value is a live credential.** The harness blocks bash reads of this
file — including host-only extraction — via the auto-mode classifier
("Blocked by classifier"). That block is correct. Do not route around it with a
different tool, a python one-liner, or a redirect.

Consequences:

- Never paste a key into a report, findings file, ticket comment, or commit.
- Never enumerate the profile list into a document. If you need to know whether a
  host has a profile, try acting as it and observe success or failure.
- If a call returns credentials in its response (e.g. `access_key` / `client_secret`
  on `/xfer/storages/<id>` detail), **redact before writing anything anywhere.**

---

## Using a profile

Act *as* a profile rather than extracting its key:

- `flyw` CLI — profile-aware; see the `flyw-cli` skill.
- `fw-instance-inspector` skill — container metadata, file info, job configs and logs.
- `fw-client` skill — raw HTTP against `/api/`, `/xfer/`, `/snapshot/`.

Useful endpoint that is easy to get wrong: to check whether a bucket is registered as
an External Storage, use `GET https://<instance>/xfer/storages` (header
`Authorization: scitran-user <key>`), detail at `/xfer/storages/<id>`. **Not**
`/api/storages` (405), and **not** `/api/site/providers` — site providers are not
external storages.

---

## No profile for the host?

Don't drop the question. Use a **same-platform-version read-only proxy**: find
another tenant running the same platform version and read its `/api/openapi.json` and
`/api/config` as a schema proxy.

Known pair: no key for `pp2dg4.prod.ten.flywheel.io` (Emory REACH test), but
`vqbyjc.prod.ten.flywheel.io` runs the same version (22.1.6).

**Gotcha:** feature flags differ per tenant. `vqbyjc` has
`features.tasks_refactor=False`, so newer Tasks Manager endpoints (`/api/tasks/reader`,
`/api/protocols`) 404/405 there. Check the flag in `/api/config` before concluding an
endpoint doesn't exist — a proxy answers schema questions, not feature-availability or
UI-behavior ones. Scope those as flagged open items instead of blocking the work.
