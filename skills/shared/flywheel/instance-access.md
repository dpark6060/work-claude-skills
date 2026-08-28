---
type: Reference
title: Flywheel Instance Access
description: The one place that says how to reach a live Flywheel instance — where credentials live, why not to read the file directly, how to pick a profile for a site, and how to build an SDK / FWClient / raw-HTTP client from it.
tags: [flywheel, auth, api-key, instances, credentials, fw-config, profiles]
timestamp: 2026-08-17T00:00:00Z
---

# Flywheel Instance Access

Authority for "which instances can I reach, and how do I build a client for one."
Consumers (`fw-instance-inspector`, `fw-quest`, `flyw-cli`, `fw-client`, `fw-verify`,
`fw-gear-debugger`) point here instead of restating it.

## Contents
- Rule zero
- Where credentials live
- Do not read the file
- Picking a profile
- Building a client
- Env vars — the fallback
- No profile for the host?

---

## Rule zero — the profiles exist, check before declaring otherwise

**Never declare "there is no API key for instance X" without checking the profile
inventory.** A 2026-07-29 sweep concluded no GE HealthCare key existed; two profiles
(`ge`, `fwge`) pointed at `gehealthcare.flywheel.io` the whole time. Asking the user
which env var holds a key is a *fallback*, not the first move.

**Never copy an API key value into a doc, ticket, comment, log, or script.** Reference
the file path and the profile name. Same rule as `access_key`/`client_secret` in
`/xfer/storages` output: redact before writing anywhere.

---

## Where credentials live

`~/.fw/config.yml`, the Flywheel CLI's config and credential store. `flyw auth login`
writes it, and exiting the shell does not log you out. Override the directory with
`FW_CLI_CONFIG_DIR`. Structure:

```yaml
default_profile: default
profiles:
- api_key: "<host>:<secret>"   # host and key in one string — the form both clients want
  id: davidparker@flywheel.io
  name: default                # what you pass to --profile
  is_admin: true
  is_drone: false
  compat: {...}                # cached version-compat info, or null
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
- If you need to know whether a host has a profile, use `flyw auth status --all`
  (which lists saved profiles without exposing key values), or try acting as the
  profile and observe success or failure.
- If a call returns credentials in its response (e.g. `access_key` / `client_secret`
  on `/xfer/storages/<id>` detail), **redact before writing anything anywhere.**

---

## Picking a profile

Known profile → host mapping (snapshot, verified 2026-08-13; `flyw auth status --all`
is authoritative when a profile is missing or a host looks wrong):

| Profile | Host | Admin |
|---|---|---|
| `default`, `alatest` | sse-latest-azure.dev.flywheel.io | yes |
| `latest` | latest.sse.flywheel.io | yes |
| `Newbie` | latest.sse.flywheel.io | no |
| `validlatest` | sse-validated.flywheel.io | yes |
| `ge`, `fwge` | gehealthcare.flywheel.io | yes |
| `fwga` | ga.ce.flywheel.io | yes |
| `nacc` | flywheel.naccdata.org | yes |
| `naccsb` | naccdata.flywheel.io | yes |
| `upenn` | upenn.flywheel.io | yes |
| `uw` | uw-chn.flywheel.io | yes |
| `ucsf`, `uscf` | ucsf.flywheel.io | yes |
| `ucsfbeta` | ucsfbeta.flywheel.io | yes |
| `ucsftrack` | trackimagingdbapt.flywheel.io | yes |
| `uscdni` | uscdni.flywheel.io | yes |
| `unsw` | unsw.flywheel.io | yes |
| `florey` | fw.epilepsyproject.org.au | yes |
| `rni` | rni.flywheel.io | yes |
| `ischemia` | ischemia.flywheel.io | yes |
| `bmfg` | bmgf.flywheel.io | yes |
| `pubdemo` | public-demo.flywheel.io | yes |
| `fasdemo` | qftcmj.prod.ten.flywheel.io | yes |
| `fassandbox` | g48wp7.prod.ten.flywheel.io | no |
| `temp` | pqs6zj.prod.ten.flywheel.io | no |

1. Start from the host in the Flywheel URL you were given and match it in the table.
   Site name → host is not always guessable: NACC production is
   `flywheel.naccdata.org` while the sandbox is `naccdata.flywheel.io`, and tenant
   sites are opaque (`qftcmj.prod.ten.flywheel.io`).
2. Several hosts have two profiles. Same host + same rights (`ge`/`fwge`,
   `ucsf`/`uscf`, `default`/`alatest`) means either works. Same host + different
   rights (`latest` admin vs `Newbie` non-admin) is deliberate — pick `Newbie` when the
   point is to observe what a normal user sees.
3. Most profiles are admin. Don't assume admin on `Newbie`, `fassandbox`, or `temp`.

---

## Building a client

Act *as* a profile rather than extracting its key:

- `flyw` CLI — profile-aware; see the `flyw-cli` skill.
- `fw-instance-inspector` skill — container metadata, file info, job configs and logs.
- `fw-client` skill — raw HTTP against `/api/`, `/xfer/`, `/snapshot/`.

The `api_key` value from a profile is already in the `host:KEY` form every client
accepts, so pass it through untouched.

```python
import flywheel                       # SDK — containers, finders, files
fw = flywheel.Client(api_key)

from fw_client import FWClient        # HTTP — anything the SDK doesn't expose
fw_http = FWClient(api_key)
```

- **`flywheel.Client` (flywheel-sdk)** — container navigation, finders, file
  download/upload. Use it by default for data.
- **`FWClient` (fw-client)** — raw endpoints: jobs (`/api/jobs/<id>/config.json`,
  `/logs/text`), plus the `/xfer/` and `/snapshot/` services that have no SDK
  surface. Full instantiation options (base_url, client_name/version, timeout,
  feature headers), drone/device auth via `FW_DRONE_SECRET`, and how to recover a key
  from an existing `flywheel.Client`: the `fw-client` skill's SKILL.md.
- **Raw HTTP** — the API-key header is `Authorization: scitran-user <key>`, e.g.
  `GET https://<host>/xfer/storages`. fw-client picks the scheme by key length:
  57-char keys go out as `Bearer`, shorter ones as `scitran-user`.
- **Inside a gear** — the client comes from the gear's `api-key` input
  (`context.get_input_path("api-key")`), not from this file.

Useful endpoint that is easy to get wrong: to check whether a bucket is registered as
an External Storage, use `GET https://<instance>/xfer/storages` (header
`Authorization: scitran-user <key>`), detail at `/xfer/storages/<id>`. **Not**
`/api/storages` (405), and **not** `/api/site/providers` — site providers are not
external storages.

---

## Env vars — the fallback

Use an env var when a profile can't be used (a gear/CI context, a standalone script,
a skill whose config names one). It is secondary to the profile file, and the name is
never a convention worth guessing:

- `fw-verify` reads the var **named in its own** `cache/config.json`
  (`api_key_env`, e.g. `FW_DEV_API`) — per-site, so check the site you're probing.
- `fw-instance-inspector` scripts have historically used `NACC_API`, `FW_API_KEY`, or
  `API_KEY`. Ask which one only after the profile route is ruled out.
- `flyw job pull` **redacts** the key in the pulled `config.json`; re-inject with
  `flyw gear config -i api_key=$MY_API_KEY` or run with `-e FW_API_KEY=$MY_API_KEY`
  (see `fw-gear-debugger`).
- CLI-only vars: `FW_CLI_API_KEY` (non-interactive `auth login`), `FW_CLI_PROFILE`
  (per-command profile selection), `FW_CLI_CONFIG_DIR`. Profile mechanics —
  creating, switching, the fact that `--profile` is not sticky — are in the
  `flyw-cli` skill's `references/auth-profiles.md`.

Read keys from the environment at run time; never hardcode one in a script you save.

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
