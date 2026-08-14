---
name: fw-condor
description: >
  Expert on Flywheel engines and condor: how gear jobs get executed, how engine VMs are
  deployed and scaled, every setting in the condor helm values.yaml, how secrets reach
  engines and gears (sops secrets.yaml, engineGearEnvironment), and job-to-engine routing
  (ENGINE_MATCH, compute providers). Use for any question about engine configuration,
  condor profiles, or why a job isn't being picked up. MANDATORY TRIGGERS: condor, engine,
  engine VM, static engine, dynamic engine, engineMatch, ENGINE_MATCH, compute provider,
  compute engine, condor profile, engineGearEnvironment, secrets.yaml, maxCompute,
  engineWorkers, queueThreshold, drone secret, zombie engine, gear not picked up,
  scale engines, engine workers, values.yaml (in a site/deployment repo context)
tags:
  - flywheel
  - condor
  - engine
  - infrastructure
  - helm
---

# fw-condor

## Overview — the mental model

**Condor is not the engine.** Condor is a small homegrown Python control-loop pod running
in a Flywheel site's k8s cluster. The **engine** is a Go binary that actually pulls and
runs gear jobs. Condor watches the job queue and imperatively creates cloud VMs (EC2 /
GCE / Azure VM) that boot the engine via cloud-init. Engines are **not** k8s workloads.

The chain: site GitOps repo `values.yaml` (`condor:` namespace) + sops-encrypted
`secrets.yaml` → helm chart renders one k8s Deployment + ConfigMap/Secret **per condor
profile** → condor pod env → cloud-init user-data → `/etc/environment` on the engine VM →
engine process → gear container.

One condor profile = one independent scaling pool with its own `engineMatch` (job
filter), machine type, and `maxCompute`. Typical site: `static-engine` (always-on,
utility gears), `static-overflow`, `analysis` (dynamic, everything else), sometimes
`gpu`.

## Key concepts (always true)

1. **Job routing is two-stage.** Core assigns every job a `compute_provider_id` at
   creation (project → group → site provider fallback). Engines then filter the queue
   with `ENGINE_MATCH` (`gear-name`/`tag`/`group`/`compute-provider`, whitelist `$in` /
   blacklist `$nin`, blacklist wins, multiple keys AND). Both stages must match.
2. **Capacity = maxCompute × engineWorkers.** `maxCompute` caps VMs per profile;
   `engineWorkers` caps concurrent jobs per VM (default = VM's CPU count, not 1 in
   practice — the helm default is "1" but only if rendered).
3. **Condor changes don't touch running engines.** Config applies only to newly created
   VMs. Static engines re-read config only when their VM is replaced (every
   `engineMaxLifespan`, e.g. 24h) — force it by deleting the VM.
4. **Static vs dynamic is one flag** (`isStaticEngine: "True"`): static = 1 always-on VM
   (queueThreshold 1, maxCompute 1, doesn't exit when idle, 24h default lifespan).
5. **Secrets ride the same values tree.** `flywheel.condor.profiles.<id>.engineGearEnvironment`
   in sops `secrets.yaml` merges over values.yaml and ends up as env vars inside gear
   containers — quote every value, and delete pods AND engines to apply.
6. **Multiprovider mode changes everything**: condor builds scalers from provider records
   in mongo (not helm values) for every non-static compute provider, and
   `configFromProvider` decides whether helm values or the provider record wins for
   machine sizing. Center gears always route to the site provider.
7. Engine VMs are named `{cloud.prefix}-{nonce}` and tagged with the profile's
   `CONDOR_ID` — that's how you tie a VM back to its condor.

## Reference guides

| Guide | Load when |
|---|---|
| [references/lingo.md](references/lingo.md) | Defining terms precisely: compute provider, engine, worker, static engine, drone, zombie — or any "what exactly is X" question |
| [references/values-yaml.md](references/values-yaml.md) | Reading or editing a condor profile / values.yaml key; what a setting does, its default, its env var; chart sharp edges |
| [references/secrets.md](references/secrets.md) | secrets.yaml, sops, engineGearEnvironment, drone secret, cloud credentials, rotation procedures |
| [references/deployment-and-scaling.md](references/deployment-and-scaling.md) | How condor/engines deploy, the scaling algorithm, engine VM boot lifecycle, static vs dynamic, multiprovider, GPU |
| [references/operations.md](references/operations.md) | Runbook tasks: restart a static engine, scale down, find engine logs, zombie hunts, "job not picked up" debugging, Central tenant quirks |

## Quality standards

- **Cite the source, not memory.** Facts here were derived 2026-07-24 from condor@master
  (`6906af48`), core-api, engine, and internal-documentation. The chart moves — for any
  load-bearing detail (defaults, env var names, template behavior), verify against
  https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/values.yaml
  before telling someone to merge a change.
- Site configs live in per-site GitOps repos (`flywheel-io/infrastructure/deployments/...`,
  `flywheel-io/customers/...`, Central: `flywheel-io/central/tenants`). Always look at the
  actual site's values.yaml when answering a site-specific question.
- Engine match changes are sharp: check every other profile for overlap/undercut before
  adding or editing one, and remember blacklist beats whitelist.
- When answering "why isn't my job running", walk both routing stages in order:
  compute_provider_id first, ENGINE_MATCH second, then capacity/zombies.
