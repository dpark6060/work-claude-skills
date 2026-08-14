---
type: Architecture Guide
title: Condor Deployment and Engine Scaling
description: How condor and engine VMs are deployed — the k8s shape, the scaling algorithm, engine VM boot lifecycle, static vs dynamic engines, multiprovider mode, and GPU engines.
tags: [condor, engine, deployment, scaling, multiprovider, gpu]
timestamp: 2026-07-24T00:00:00Z
---

# Condor Deployment and Engine Scaling

## The k8s shape

The condor chart renders **one `apps/v1 Deployment` per profile** — nothing else runs
workloads. No StatefulSet, DaemonSet, Service, HPA, or PDB anywhere in the chart, and no
nodeSelector/tolerations/affinity: engine placement is a *cloud* concern (zone, subnets,
availabilityZones), not a k8s scheduling concern.

- Names: `condor.fullname` = `<Release.Name>-condor-<condor_id>` (e.g.
  `flywheel-condor-analysis-7dd98577db-72q9r` pods).
- `replicas` is global (default 1). Condor is not HA within a profile — `scaler_id =
  condor_id` preserves engine ownership across restarts; two replicas would double-scale.
- Pod annotations checksum every config source, so values changes roll condor pods
  automatically. Engine VMs do NOT roll — see "config propagation" below.
- One container, unprivileged, prometheus on :8000, exec liveness `python -m
  bin.healthcheck` (unhealthy if a loop takes more than `cloud.pollDelay` +
  `healthCheck.delayToleranceSeconds` [90s]).

## The scaling loop (scalers/abstract.py)

Every `pollDelay` seconds, per profile:

1. Ask core how many **pending** jobs match this profile's `ENGINE_MATCH`.
2. Count this profile's running VMs at the cloud provider (by CONDOR_ID tag).
3. Decide:

```python
if is_static_engine or pending >= queue_threshold:
    more_workers_than_jobs = workers * num_nodes >= pending + running
    if not is_static_engine and more_workers_than_jobs and pending > 0:
        pass          # existing capacity will absorb it (may still be cloud-initing)
    elif num_nodes < max_compute:
        add_node()
```

4. `delete_zombie_engines()` — reap VMs whose redis heartbeat
   (`engine-heartbeat*` keys, written via perimeter) is older than
   `config.engineZombieScan.engineHeartbeatTimeoutSeconds` (600) or that never finished
   cloud-init within `engineCloudInitTimeoutSeconds` (3600). Timeout 0 disables reaping.
5. `delete_orphaned_disks()`.

Scale-*down* is not condor's job: dynamic engines exit themselves when the queue drains
(`ENGINE_EXIT_WHEN_DONE`), and their VM is destroyed. Lowering `maxCompute` only stops
new VM creation — running engines keep working until their queue is exhausted. To force
immediate scale-down, tell engines to quit (SRE runbook MANUALLY_QUIT_ENGINES.md).

## Engine VM lifecycle

1. Condor calls the cloud SDK: create VM named `{prefix}-{nonce}`, tagged with
   CONDOR_ID, with rendered cloud-init user-data.
2. cloud-init `write_files`: appends `export`s (ENGINE_MATCH, SCITRAN_RUNTIME_HOST/PORT,
   drone secret, gear environment, monitoring creds…) to `/etc/environment`.
3. `runcmd`: allocate + enable swapfile; download
   `boot-engine.<boot_engine_version>.sh` from
   `storage.googleapis.com/flywheel-dist/engine-boot-scripts/` into
   `/var/lib/cloud/scripts/per-boot/`; run it.
4. boot-engine.sh: installs prereqs, downloads the engine binary
   (`flywheel-dist/engine/engine.<ENGINE_VERSION>`), node exporter, vector (logging),
   podman if `ENGINE_MODULE=podman`, then `./engine run`.
5. Engine polls `POST /api/jobs/ask`, runs up to `ENGINE_WORKERS` jobs concurrently,
   heartbeats via perimeter, and exits per its exit policy; the VM is then deleted.

**GPU path** (`gpuEnabled`): first boot purges nvidia packages, runs
`ubuntu-drivers install`, and **reboots**; the per-boot script starts the engine on boot
two, after generating the nvidia CDI. On GCP you must also set
`google.acceleratorConfig` to actually attach the GPU. AWS GPU sites typically use a
dedicated AMI via the profile's `amazon.amiId` (top-level `amazon.ami_id` is the
default for all profiles; per-profile overrides it).

## Config propagation — the #1 operational gotcha

Condor config controls only the **creation** of engine VMs. Existing VMs have their env
baked into `/etc/environment`:

- Dynamic engines: new config applies as old VMs churn out naturally.
- Static engines: config (including engineMatch) applies only when the VM is replaced —
  every `engineMaxLifespan` (24h default), or immediately if you delete the VM (condor
  recreates it).
- Central tenants on auto-upgrade: condor changes are additionally **staged at merge**
  and only applied at manual sync or the next maintenance window.

## Static vs dynamic

`isStaticEngine: "True"` swaps in `StaticScalerConfig`
(scalers/config/builder.py): `queue_threshold=1`, `max_compute=1`,
`engine_exit_when_done=False`, `engine_signed_urls=True`,
`engine_max_lifespan="24h"`, `cloud_poll_delay=360`. Static engines always run at
max_compute and skip the "enough workers already" throttle.

Use static for fast/frequent utility gears needing instant pickup
(file-metadata-importer, file-classifier, dcm2niix…) — always-on cost. Use dynamic for
heavy/long/batch analysis. Extra condor profiles themselves cost nothing (tiny pods).
Cheap batch trick: a profile with `maxCompute: 1, queueThreshold: 1` for a
heavy-docker-image gear — one VM pulls the image once and chews through the queue.

## Single-provider vs multiprovider mode

`run_condor.py` branches on site features:

- **Single-provider** (most sites): one scaler per profile, built entirely from the
  profile's env vars (helm values). Log line: `Condor ID <id> running in single provider
  mode`.
- **Multiprovider** (`multiproject` feature + `use_multiprovider`): condor polls
  `fw.get_providers()` and builds a scaler for **every compute provider whose
  provider_type is not static**, using the config and creds stored on the provider record
  in mongo. Scalers rebuild when `provider.modified` changes. Each scaler's engine match
  gets `whitelist["compute-provider"] = [provider_id]` appended automatically.
  - `configFromProvider` (default false): when false, machine sizing keys
    (`disk_size, machine_type, max_compute, preemptible, queue_threshold, swap_size`)
    from the provider record are ignored in favor of env/helm values.
  - **Static compute providers are skipped** — condor-managed static engines don't work
    on multiprovider sites (FLYW-15952); jobs routed to a static provider need
    separately-managed engines.
  - **Center gears** always get the site provider (center-pays), regardless of tags or
    group/project provider links.

## Version coupling

Condor, engine, and core-api versions are pinned together per umbrella release, and their
tags don't necessarily match (e.g. condor 20.6.5 / engine 20.6.3 / core-api 20.6.3).
`engineVersion` unset → condor's built-in default (22.2.0 at time of writing);
`boot_engine_version` defaults to `master` and is not exposed in values.yaml.

# Citations

[1] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/templates/deployment.yaml
[2] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/scalers/abstract.py — scaling decision loop, zombie/orphan cleanup
[3] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/scalers/config/builder.py — StaticScalerConfig, PROVIDER_IGNORED_FIELDS, DEF_ENGINE_VERSION
[4] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/run_condor.py and condor/condor.py — mode branch, multiprovider scaler management
[5] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/ops/cloud-init.yml.j2 and ops/boot-engine.sh — VM boot lifecycle, GPU path
[6] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/configuration.md — config propagation warnings, static vs dynamic guidance
[7] https://gitlab.com/flywheel-io/infrastructure/sre/-/blob/master/runbooks/MAINTENANCE/MANUALLY_QUIT_ENGINES.md — forced scale-down
[8] Center-gear/multiprovider-static thread: https://flywheel-io.slack.com/archives/C02PYE3K7RU/p1722974052611439 (FLYW-15952)
[9] Version pinning: Suphi Altintasli, #ml-analytics 2025-10-01 (umbrella release table)
