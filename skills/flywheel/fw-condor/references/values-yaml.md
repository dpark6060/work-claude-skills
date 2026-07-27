---
type: Config Reference
title: Condor values.yaml Reference
description: Every key in the condor helm chart values.yaml — what it controls, its env var, its real default (helm vs code), plus known chart sharp edges.
tags: [condor, helm, values.yaml, configuration]
timestamp: 2026-07-24T00:00:00Z
---

# Condor values.yaml Reference

Chart: `helm/condor` in `flywheel-io/product/backend/condor` (facts as of master
`6906af48`, 2026-07-24). Sites set these under the `condor:` namespace of their GitOps
repo values.yaml. The chart's generated `helm/condor/README.md` has the same content as
tables plus configuration examples.

**Two layers of defaults**: helm values.yaml documents keys but many defaults actually
live in `scalers/config/builder.py` (pydantic `ScalerConfig`) — a key absent from the
ConfigMap falls back to the code default, noted below as "code default".

## Profiles — `condor.profiles.<condor_id>`

The map key is the `CONDOR_ID` (required); it names the Deployment
(`<release>-condor-<condor_id>`) and tags every engine VM. `engineMatch` is required per
profile.

### Scaling knobs (`cloud.*` per profile)

| key | env var | default | meaning |
|---|---|---|---|
| `prefix` | `CLOUD_PREFIX` | — | VM name prefix (+ random nonce). Must match `[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?` |
| `machineType` | `CLOUD_MACHINE_TYPE` | **required** | e.g. `n1-standard-4`, `m5a.large`, `Standard_D4as_v5` |
| `queueThreshold` | `CLOUD_QUEUE_THRESHOLD` | code 10 | min pending matching jobs before another VM is created |
| `maxCompute` | `CLOUD_MAX_COMPUTE` | code 2 | max VMs this profile will create |
| `diskSize` | `CLOUD_DISK_SIZE` | code 200 | GB |
| `swapSize` | `CLOUD_SWAP_SIZE` | code 30G | must match `^[1-9]+\d*[KGMT]$` |
| `pollDelay` | `CLOUD_POLL_DELAY` | code 180 (static 360) | seconds between scaling loops |
| `securityNames` | `CLOUD_SECURITY_NAMES` | top-level `cloud.securityNames` | comma-separated security groups / network tags |

### Engine behavior (per profile)

| key | env var | default | meaning |
|---|---|---|---|
| `engineMatch` | `ENGINE_MATCH` | **required** | whitelist/blacklist job filter (see lingo.md), YAML→JSON |
| `engineWorkers` | `ENGINE_WORKERS` | helm "1"; **unset → NumCPU** | concurrent jobs per VM |
| `engineVersion` | `ENGINE_VERSION` | code `22.2.0` | engine binary version pulled from flywheel-dist |
| `engineExitWhenDone` | `ENGINE_EXIT_WHEN_DONE` | True | dynamic engines exit when queue drains |
| `engineExitIdleTime` | `ENGINE_EXIT_IDLE_TIME` | 0 | idle-exit timer, resets on new work |
| `engineMaxLifespan` | `ENGINE_MAX_LIFESPAN` | none (static "24h") | VM drains and is replaced after this |
| `engineGearEnvironment` | `FW_ENGINE_GEAR_ENVIRONMENT` (Secret) | — | JSON env map injected into gear containers — see secrets.md |
| `engineModule` | `ENGINE_MODULE` | runc | `runc` \| `podman` \| `hold` (HPC) |
| `engineHeartbeatPeriodSeconds` | `ENGINE_HEARTBEAT_PERIOD_SECONDS` | 30 | |
| `isStaticEngine` | `IS_STATIC_ENGINE` | false | switches to StaticScalerConfig (see deployment-and-scaling.md) |
| `gpuEnabled` | `GPU_ENABLED` | false | nvidia toolkit + driver-install-and-reboot boot path |
| `logDnsRequests` | `LOG_DNS_REQUESTS` | false | tcpdump port 53 on the VM, dumped to serial console — for customer firewall requests |
| `podman.sharedMemorySize` | `PODMAN_SHARED_MEMORY_SIZE` | code 65536k | podman shm (bump for gears that need >64MB) |
| `extraEnv` | (literal) | — | map rendered directly as env on the condor container |
| `imageTag` | — | `image.tag` | per-profile condor image override |

### Per-profile cloud-specific blocks

- `amazon`: `amiId`, `amiNameTemplate` (code default ubuntu-noble-24.04), `diskType`
  (code gp3), `backupMachineTypes`. Profile `amazon.amiId` overrides top-level
  `amazon.ami_id` (confirmed pattern for GPU-only AMIs).
- `google`: `acceleratorConfig` (JSON — this is what actually attaches GPUs on GCP),
  `machineImage` (code default ubuntu-minimal-2404), `machineImageFamily`, `diskType`
  (code pd-ssd), `shieldedVm`.
- `azure`: `imageId` (`AZURE_GOLDEN_IMAGE_ID`), marketplace image overrides
  (`vmImagePublisher/Offer/Sku/Version` + plan fields), `diskType` (code
  StandardSSD_LRS), `subnetNames`, `availabilityZones` (JSON list, e.g. `'["1","2"]'`),
  `backupMachineTypes`. Each falls back to the top-level `azure.*` equivalent.

## Top-level keys

| key | notes |
|---|---|
| `image` | `flywheel.azurecr.io/flywheel/condor:master`; `global.imageRegistry` overrides registry; pull secret `regcred` hardcoded |
| `replicas` | 1, applied to every profile's Deployment. Do not raise: two condors with the same CONDOR_ID double-scale |
| `resources` | condor pod only (128Mi/0.1cpu req, 512Mi limit, deliberately no CPU limit). Engines are VMs — sizing is `machineType` |
| `global.droneSecret` / `global.droneSecretName` | drone credential inline vs existing-k8s-secret; one is required |
| `global.domain` | external core domain — becomes `SCITRAN_RUNTIME_URL` baked into engine VMs (condor itself uses the internal service name) |
| `cloud.{project,region,zone,scaler,resourceTags,securityNames}` | cluster-wide cloud identity; `scaler` = `google`\|`amazon`\|`azure` (aliases gc/gcp/gcs/aws accepted) |
| `amazon.{keyId,accessKey,ami_id,publicIP,instanceProfile}` | AWS creds + defaults; also undocumented `key_name`, `vpc_subnet_id_list`/`vpc_subnet_id` |
| `google.serviceAuth.credentials` | base64 SA JSON, mounted at `/service_auth/service-auth.json` |
| `azure.*` | tenantId, subscriptionId, resourceGroupName, vnet/subnet, workloadIdentity, generateSSHKey, publicSSHKey (PEM), logStorage, marketplace defaults (Canonical ubuntu-24_04-lts). Auth precedence: managed identity (nothing set) → service principal (`clientId`+`clientSecret`, base64) → workload identity (`workloadIdentity: true`, clientId NOT base64) |
| `signedUrls` | true → `ENGINE_SIGNED_URLS=true` |
| `configFromProvider` | false. When false condor strips `{disk_size, machine_type, max_compute, preemptible, queue_threshold, swap_size}` from provider-supplied config and uses env/helm values instead — the switch deciding whether helm or the Flywheel provider record wins on multiprovider sites |
| `coreLocalAddress` | adds hostAlias on the pod AND /etc/hosts on engine VMs |
| `customCACertificate` | installed in condor pod (init container) AND passed to engine VMs |
| `config.redis.*` / `config.engineZombieScan.*` | perimeter redis (heartbeats); zombie timeouts: 600s heartbeat, 3600s cloud-init |
| `monitoring.*` | vector logging/metrics; remote write to metrics.v3.ops.flywheel.io; normally populated by terraform |
| `metrics.enabled` | ONLY toggles prometheus scrape annotations — monitoring secrets are required regardless |
| `argoVaultPlugin.enabled` | skips creating the vector-monitoring secret (Argo injects it); the Deployment still references it |
| `wiz.*` | Wiz sensor creds forwarded into engine VMs |

## Chart sharp edges (verified in templates, master 2026-07)

1. **`profiles.<id>.amazon.diskType` never renders** — template bug (`if` doesn't rebind
   context); `AMAZON_DISK_TYPE` always falls back to code default gp3.
2. **`google.shieldedVm` and top-level `amazon.ami_name_template` fallback never render**
   — case/style mismatches between values.yaml and the template (`shieldedVM`,
   `amiNameTemplate`).
3. **A profile with exactly one key renders no ConfigMap at all** (templates gated on
   `len(profile) > 1`) — and the `engineMatch` required-check is inside that gate, so it
   silently deploys nothing.
4. `metrics.enabled` is misleading (annotations only).
5. `aws-credentials` and `service-auth` secrets have fixed names with no release prefix —
   two releases in one namespace collide.
6. `azure.clientId` encoding flips: base64 when used as a service-principal secret, NOT
   base64 when `workloadIdentity: true` (it becomes an SA annotation).
7. Pod annotations carry config checksums so values changes roll condor pods — but
   **running engine VMs never pick up changes** (env is baked into /etc/environment).

## Worked example (canonical 3-profile site)

```yaml
.static-gears: &static-gears
  gear-name: [curate-bids, dcm2niix, dicom-mr-classifier, parrec-mr-classifier, roi2nix]

condor:
  profiles:
    static-engine:
      isStaticEngine: "True"
      engineMaxLifespan: "24h"
      engineWorkers: 6
      cloud: {prefix: static-engine, machineType: n1-standard-2}
      engineMatch:
        whitelist: *static-gears
    static-overflow:
      engineWorkers: 12
      cloud: {prefix: static-overflow, machineType: n1-standard-4, queueThreshold: 50}
      engineMatch:
        whitelist: *static-gears
    analysis:
      cloud: {prefix: analysis, machineType: n1-highmem-4, queueThreshold: 1, maxCompute: 64}
      engineMatch:
        blacklist: *static-gears
```

Watch the anchors: some sites hard-code the list in one profile — update both when the
gear list changes.

# Citations

[1] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/values.yaml — primary source
[2] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/README.md — generated tables + config examples
[3] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/scalers/config/builder.py — code defaults (ScalerConfig/StaticScalerConfig, PROVIDER_IGNORED_FIELDS)
[4] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/templates/configmap-profiles-env.yaml — key→env-var mapping and sharp edges 1–3
[5] https://gitlab.com/flywheel-io/product/backend/condor/-/tree/master/helm/condor/test — 9 example values files
[6] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/configuration.md — profile guidance, engineMatch rules
[7] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/static-condor-migration.md — the 3-profile template
[8] AMI default/override confirmation: https://flywheel-io.slack.com/archives/C0417E9FQHZ/p1784222625671169
