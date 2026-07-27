---
type: Glossary
title: Condor / Engine Lingo
description: Concrete, code-grounded definitions of the terms used around Flywheel job execution — compute provider, engine, worker, condor, profile, static engine, drone, perimeter, zombie.
tags: [condor, engine, glossary]
timestamp: 2026-07-24T00:00:00Z
---

# Condor / Engine Lingo

Every definition here is grounded in code, not folklore. Field names, enums, and
endpoints are quoted from the repos listed in Citations.

## Engine

The Flywheel job executor. A **Go binary** (repo `flywheel-io/product/backend/engine`,
whose README is literally titled "Compute — Holds the engine and perimeter"). Distributed
as a standalone binary from `https://storage.googleapis.com/flywheel-dist/engine/engine.<version>`.

What it does: polls core with `POST /api/jobs/ask` (body
`{whitelist, blacklist, capabilities, return: {jobs, peek, encoded}}`), downloads gear
inputs, runs the gear container through a runtime module (`ENGINE_MODULE`: `runc` default,
`podman`, or `hold` for HPC), streams logs and job heartbeats through perimeter, uploads
outputs, marks the job complete. Started as `./engine run` by cloud-init on a condor VM,
or as a docker-compose service on legacy V2 installs.

## Compute engine

The same thing as "engine". Internal docs say "VMs running the compute engine"; the
engine repo is named "Compute". **Not** GCP's "Compute Engine" product — that's a naming
collision. In a GCP console, "Compute Engine VM instance" just means a GCE virtual
machine.

## Engine VM (a.k.a. "Compute Engine VM instance" in GCP consoles)

A cloud VM (EC2 instance / GCE instance / Azure VM) created **imperatively** by condor
via cloud SDK calls — not a k8s workload. Named `{cloud.prefix}-{nonce}` (e.g.
`static-engine-e3f275ea`) and tagged with its profile's `CONDOR_ID`. Boot: cloud-init
writes env exports to `/etc/environment`, allocates swap, downloads `boot-engine.sh` and
the engine binary, runs one engine process.

## Worker

A **concurrency slot inside one engine process**. `ENGINE_WORKERS` (helm `engineWorkers`)
= max jobs one engine runs simultaneously. In code: `server/env.go` —
`DeCapacity = envD("ENGINE_WORKERS", runtime.NumCPU())`, exposed as CLI flag
`--capacity/-c` ("Worker limit"). **Default when unset = number of CPUs on the VM.**
So: per-VM capacity = `engineWorkers`; per-profile capacity = `maxCompute × engineWorkers`.
Condor also uses it in the scale-up throttle: if `workers × nodes ≥ pending + running`,
no new VM.

## Condor

A homegrown Python control-loop pod in the site's k8s cluster that watches the job queue
and creates/destroys engine VMs. "Condor is not the actual executor, it does not run any
jobs." Entry point `run_condor.py`; authenticates to core as a drone
(`create_drone_client(host, secret, "cloud-scale", "flywheel-utility", port)`) over the
internal `<release>-core-api:8080` service. Exposes Prometheus metrics on `:8000`.

## Condor profile / CONDOR_ID

One entry under `condor.profiles.<condor_id>` in the site values.yaml. Renders one k8s
Deployment (`<release>-condor-<condor_id>`) — an independent condor process with its own
`ENGINE_MATCH`, machine type, `maxCompute`, image, GPU flag. The map key IS the
`CONDOR_ID`, which is stamped into every engine VM's name/tags.

## Scaler

The per-cloud implementation condor uses to count/create/delete VMs
(`scalers/amazon.py`, `google.py`, `azure.py`, plus `dummy.py`, `redis.py`). In
single-provider mode there's one scaler built from env vars; in multiprovider mode condor
builds one scaler per non-static compute provider from the provider's mongo record.

## Compute / compute provider

A **provider record in core's mongo `providers` collection** (API
`/api/site/providers`). Model `core/models/providers.py: Provider`:
`provider_class` (enum `compute | storage`), `provider_type` (enum
`local | static | aws | azure | gc | s3_compat | exchange` — note GCP is the legacy
string `"gc"`), `label`, `config` (typed per class+type), `creds`
(AwsCreds/GcpCreds/AzureCreds).

- `provider_class=compute`, `provider_type=aws|gc|azure`: a cloud account condor can
  spin engines in. In multiprovider mode condor reads its config/creds straight from
  mongo and builds a scaler for it.
- `provider_type=static`: a compute provider representing engines **not** managed by
  condor's dynamic scaling. Condor explicitly skips static providers in multiprovider
  mode (`condor/condor.py`) — this is why "condor static engines don't work on
  multiprovider sites" (FLYW-15952).

## Job → provider routing

Every job gets a `compute_provider_id` at creation
(`core/services/jobs.py: _render_compute_provider`):

- Non-multiproject sites: always `site_settings.providers.compute`.
- Multiproject: if the gear is a **center gear** (center-pays), the site provider is
  forced — a lab/tag-based profile will never see that job. Otherwise
  `get_compute_provider_for_container`: `project.providers.compute` →
  `group.providers.compute` → site settings; if it only resolves at site level on a
  multiproject site, the job is **rejected** ("no valid provider").

## ENGINE_MATCH (whitelist / blacklist)

The job filter an engine sends with every `jobs/ask`. Struct
(`engine sdk/api/job.go: JobsMatch`): `group`, `gear-name`, `tag`, `compute-provider`.
Server-side (`core-api core/mappers/jobs.py: convert_config_lists_to_query`) it becomes a
mongo query: `group`→`parents.group`, `gear-name`→`gear_info.name`, `tag`→`tags`,
`compute-provider`→`compute_provider_id`; whitelist→`$in`, blacklist→`$nin` on the same
key. **Blacklist beats whitelist; multiple keys AND together.** Whitelist needs *some*
intersection, blacklist requires *no* intersection. Capabilities: the job's
`gear_info.capabilities` must be a subset of what the engine advertises. In multiprovider
mode condor auto-appends `whitelist["compute-provider"] = [provider_id]` per scaler.

## Static engine vs dynamic engine vs static compute provider

Three different things people conflate:

- **Dynamic engine**: VM condor creates when `pending ≥ queueThreshold`, exits when the
  queue drains (`engineExitWhenDone` default True).
- **Static engine (condor-managed)**: profile with `isStaticEngine: "True"` —
  `StaticScalerConfig` defaults kick in: `queue_threshold=1`, `max_compute=1`,
  `engine_exit_when_done=False`, `engine_max_lifespan="24h"`. One always-on VM, replaced
  every lifespan. There are also **legacy V2 static engines**: hand-installed
  docker-compose engines configured via `/opt/flywheel/prod-override.yml`.
- **Static compute provider**: the provider-type in core marking compute condor should
  NOT manage. Unrelated to `isStaticEngine`.

## Drone / drone secret

A drone is a trusted machine client (device) of core. The **drone secret**
(`SCITRAN_CORE_DRONE_SECRET`, `flywheel.global.droneSecret` in secrets.yaml) is the
shared credential condor and every engine use to authenticate. Condor registers as
device type `cloud-scale`/`flywheel-utility`.

## Perimeter

The websocket/WAMP sidecar service engines talk to for job logs (`add-logs`) and
heartbeats. Lives in the engine repo. Engine heartbeats land in redis under
`engine-heartbeat*` keys — which is what condor's zombie scan reads.

## Zombie engine / orphaned disk

A **zombie** is an engine VM that stopped doing useful work (no heartbeat for
`engineHeartbeatTimeoutSeconds`, default 600s, or never finished cloud-init within
3600s). Condor's loop calls `delete_zombie_engines()` and `delete_orphaned_disks()` each
iteration; setting the heartbeat timeout to 0 disables the reaping. Symptom of a zombie:
log shows only heartbeats (or nothing), CPU flatlined, no `runc` process tree.

# Citations

[1] https://gitlab.com/flywheel-io/product/backend/engine/-/blob/master/readme.md
[2] https://gitlab.com/flywheel-io/product/backend/engine/-/blob/master/sdk/api/job.go — `JobsMatch`, `JobsAsk` (POST jobs/ask)
[3] https://gitlab.com/flywheel-io/product/backend/engine/-/blob/master/server/env.go — ENGINE_WORKERS default = NumCPU
[4] https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/models/provider_types.py — ProviderClass/ProviderType enums
[5] https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/models/providers.py — Provider model
[6] https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/services/jobs.py — `_render_compute_provider`, `_get_compute_provider_id`
[7] https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/services/providers.py — `get_compute_provider_for_container`
[8] https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/mappers/jobs.py — `convert_config_lists_to_query`
[9] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/run_condor.py and condor/condor.py — drone client, multiprovider scaler management
[10] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/scalers/config/builder.py — ScalerConfig / StaticScalerConfig
[11] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/about_condor.md
[12] FLYW-15952 (condor static engines on multiprovider) — surfaced in Slack: https://flywheel-io.slack.com/archives/C02PYE3K7RU/p1722974052611439
