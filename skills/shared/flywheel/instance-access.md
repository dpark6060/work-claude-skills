---
type: Reference
title: Flywheel Instance Access
description: The one place that says how to reach a live Flywheel instance — the ~/.fw/config.yml profile inventory, how to pick a profile for a site, and how to build an SDK / FWClient / raw-HTTP client from it.
tags: [flywheel, auth, api-key, profiles, instance-access]
timestamp: 2026-08-13T00:00:00Z
---

# Flywheel Instance Access

Authority for "which instances can I reach, and how do I build a client for one."
Consumers (`fw-instance-inspector`, `fw-quest`, `flyw-cli`, `fw-client`, `fw-verify`,
`fw-gear-debugger`) point here instead of restating it.

## Rule zero — check `~/.fw/config.yml` first

**Never declare "there is no API key for instance X" without reading
`~/.fw/config.yml` `profiles:`.** A 2026-07-29 sweep concluded no GE HealthCare key
existed; two profiles (`ge`, `fwge`) pointed at `gehealthcare.flywheel.io` the whole
time. Asking the user which env var holds a key is a *fallback*, not the first move.

**Never copy an API key value into a doc, ticket, comment, log, or script.** Reference
the file path and the profile name. Same rule as `access_key`/`client_secret` in
`/xfer/storages` output: redact before writing anywhere.

## The file

`~/.fw/config.yml` is the Flywheel CLI's config and credential store; `flyw auth login`
writes it, and exiting the shell does not log you out. Override the directory with
`FW_CLI_CONFIG_DIR`.

`profiles:` is a YAML **list** (not a map). Each record:

```yaml
default_profile: default
profiles:
- api_key: <host>:<KEY>        # host and key in one string — the form both clients want
  name: <profile name>         # what you pass to --profile
  id: <user id>
  is_admin: true
  is_drone: false
  compat: {...}                # cached version-compat info
```

So the profile's *identity* is its `name:` field and its *host* is the part of
`api_key` before the first `:`.

### Reading it without PyYAML

PyYAML is not installed in system `python3`. Either string-split the file or go
through the CLI (`flyw auth status --all` lists every saved profile). To enumerate
name → host without ever touching a key value:

```bash
rg -o '^  name: .*' ~/.fw/config.yml            # profile names
rg -o '^- api_key: [^:]+' ~/.fw/config.yml      # hosts only, key truncated at the ':'
```

## Profile inventory (verified 2026-08-13)

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

The table is a snapshot — the file is authoritative, so re-read it rather than trusting
this list when a profile is missing or a host looks wrong.

### Picking one

1. Start from the host in the Flywheel URL you were given and match it in the table
   (or in the file). Site name → host is not always guessable: NACC production is
   `flywheel.naccdata.org` while the sandbox is `naccdata.flywheel.io`, and tenant
   sites are opaque (`qftcmj.prod.ten.flywheel.io`).
2. Several hosts have two profiles. Same host + same rights (`ge`/`fwge`,
   `ucsf`/`uscf`, `default`/`alatest`) means either works. Same host + different
   rights (`latest` admin vs `Newbie` non-admin) is deliberate — pick `Newbie` when the
   point is to observe what a normal user sees.
3. Most profiles are admin. Don't assume admin on `Newbie`, `fassandbox`, or `temp`.
4. No profile for the host: before giving up, check whether another tenant on the
   **same platform version** answers the question read-only (`/api/config`,
   `/api/openapi.json`) — that proxy trick is `fw-quest`'s
   `references/where-things-live.md`.

## Building a client

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
