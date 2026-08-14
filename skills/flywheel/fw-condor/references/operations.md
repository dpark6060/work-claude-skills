---
type: Runbook Digest
title: Engine Operations and Troubleshooting
description: Day-to-day engine ops — restarting static engines, scaling down, finding engine logs, zombie hunts, debugging "job not picked up", Central tenant quirks, legacy V2 engines.
tags: [condor, engine, operations, troubleshooting, runbook]
timestamp: 2026-07-24T00:00:00Z
---

# Engine Operations and Troubleshooting

## Debugging "my job isn't being picked up"

Walk the two routing stages, then capacity:

1. **Compute provider**: does the job's `compute_provider_id` point where you think?
   Center gears are forced to the site provider (a lab/tag profile will never see them).
   On multiproject sites a job whose provider only resolves at site level is rejected
   outright.
2. **ENGINE_MATCH**: check every profile for overlap — another profile's whitelist may
   be grabbing it (check the job's executor name to see who took it), or a blacklist may
   be excluding it (blacklist beats whitelist; multiple keys AND). See the applied match
   in three places: `kubectl get cm <release>-condor-<profile>-env -o yaml`, condor's
   startup log ("Initial match value from environment"), or `/etc/environment` on the
   VM. One field-reported oddity: a gear matched via `gear-name` after failing to match
   via `tag` — when a tag whitelist mysteriously doesn't work, try gear-name.
3. **Capacity/zombies**: `pending >= queueThreshold`? `num_nodes < maxCompute`? A
   zombie VM sitting idle counts against maxCompute and blocks new VMs — delete it.
4. Static engines only re-read engineMatch when their VM is replaced — restart it
   (below) after match changes.

Condor's own logs are the fastest source of truth: mode line
(`running in single provider mode` / `multiprovider main loop`), scaler creation, per-loop
pending/node counts, and (multiprovider) the provider ObjectId on every line.

## Forcing a static engine to restart

Delete the VM; condor recreates it with current config. Find the `prefix` from the
profile, then from the site's gitlab runner:

```bash
# AWS
aws ec2 describe-instances --filters "Name=tag:Name,Values=<prefix>*" \
  --query 'Reservations[*].Instances[*].InstanceId' --output text \
  | xargs -I {} aws ec2 terminate-instances --instance-ids {}
# GCP
gcloud compute instances list --filter="name~'<prefix>' AND status='RUNNING'"
gcloud compute instances delete <instance> --zone <zone> --quiet
# Azure
az vm list | jq '.[].id' | grep <prefix>
az vm delete --ids <instance-id>
```

Static engines drain gracefully at end of `engineMaxLifespan` (finish running jobs, take
no new ones) — deleting the VM mid-job kills the job, so check first.

## Scaling down / quitting engines

Lowering `maxCompute` only stops NEW VM creation; running engines work until the queue
drains. To force immediate exit, use the SRE runbook:
https://gitlab.com/flywheel-io/infrastructure/sre/-/blob/master/runbooks/MAINTENANCE/MANUALLY_QUIT_ENGINES.md

## Finding engine logs

- **Centralized** (when GCP logging enabled): GCP project `flywheel-logs` → Logs
  Explorer. Dynamic engines are NOT k8s containers — query with
  `jsonPayload.cluster_name="<cluster>"`, `jsonPayload.engine_type="dynamic"`,
  `logName:"<condor_id>"`, `jsonPayload.job="<job_id>"`.
- **Serial console**: `aws ec2 get-console-output --latest --instance-id <id> | jq -r .Output`.
- **Azure** (no centralized logging): ssh in (key in 1Password), `tail /var/log/syslog
  /var/log/cloud-init.log /log.json`.
- Condor pod logs: `kubectl get pods | grep condor`, then normal kubectl logs.

Healthy engine log: `jobs-ask` / `download` / `complete-job` / "Job complete" lines.
Unhealthy: heartbeats only, or silence. Also check CPU (flatlined ≈ dead), a `runc`
process tree (present ≈ gear running), and disk (full disk wedges jobs — bump `diskSize`).

## Zombie/runaway engine hunt (periodic check)

1. Grafana Application dashboard: engine VM count should be ≤ running jobs.
2. Cloud console: VMs named `{condor_id}-{nonce}`; check launch dates are recent.
3. Spot-check the oldest VMs' logs (above).
4. Forensics guide: https://gitlab.com/flywheel-io/product/backend/engine/-/blob/master/doc/debugging.md
5. Only when certain it's doing no work: terminate the VM, note job IDs still
   heartbeating, verify they retry.

Known failure pattern: a failed job leaves its VM up doing nothing; condor sees "a VM
exists with few jobs" and won't add more, so the queue stalls behind the zombie.

## Multiprovider troubleshooting

Provider ObjectId is on every condor log line. Creds live in mongo:
`db.providers.findOne({_id: ObjectId("<id>")})` → save `creds` to creds.json →
`gcloud auth activate-service-account <client_email> --key-file=creds.json` → then
`gcloud compute instances list/ssh/delete` in the external project.

## Central (tenant) sites

- Tenant condor overrides go in `releases/<env>/<tenant>/flywheel.yaml` in
  `flywheel-io/central/tenants`, layered onto defaults by ArgoCD.
- A tenant profile with the same name **combines with** (does not replace) the _default
  profile — whitelists/blacklists merge. Name tenant-specific profiles distinctly.
- Condor changes on auto-upgrade tenants are staged at merge, applied at sync or
  maintenance window.
- engineGearEnvironment gear secrets do NOT work on Central (PLT-6142, FLYW-39753).

## HPC hold engines

For HPC-client sites: a profile (or V2 engine) with `ENGINE_MODULE: hold`,
`ENGINE_WORKERS: 5000`, `ENGINE_REMOTE: true` and a `tag: [hpc]` whitelist grabs matching
jobs and parks them in Hold status for the HPC client to pick up. Add `hpc` to every
other profile's blacklist. Drone secret changes must be propagated to the HPC client.

## Legacy V2 engines

Hand-installed docker-compose engines on customer VMs, configured via
`/opt/flywheel/prod-override.yml` (ENGINE_MATCH, ENGINE_WORKERS, drone secret,
FW_ENGINE_GEAR_ENVIRONMENT as compose `environment:` entries). Managed with
`/opt/flywheel/flywheel.sh {start,stop,reset-containers,logs}`. Inventory:
https://gitlab.com/flywheel-io/tools/legacy/v2-engine-inventory (customer-V2engine.yml).
Upgrades pin a skopeo version (check `transport/file.go` in the engine tag). Prefer
migrating to a static condor profile (>=15.8.5, non-multiprovider) — see
static-condor-migration.md.

# Citations

[1] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/check-dynamic-engines.md
[2] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/configuration.md — restart-static-engine commands, scale-down warning
[3] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/support/logs/collecting-engine-logs.md
[4] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/multiprovider-condor-troubleshooting.md
[5] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/adding-hpc-hold-engine.md
[6] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/static-engine.md and static-condor-migration.md — V2 engines
[7] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/engineering/teams/ml-analytics/runbooks/condor.md
[8] SRE component doc (called "the best doc we have" on engineMatch): https://gitlab.com/flywheel-io/infrastructure/sre/-/blob/master/components/condor.md
[9] Slack threads: center-gear routing https://flywheel-io.slack.com/archives/C02PYE3K7RU/p1722974052611439 ; Central secrets limitation https://flywheel-io.slack.com/archives/GPFLK2FA6/p1783526145859069 ; profile collision / executor name https://flywheel-io.slack.com/archives/GPFLK2FA6/p1754518021743609 ; tenant profile merging (Pablo Velasco, #scientific-solutions-team 2024-05-22); tag-vs-gear-name oddity (Luis Torres, #solutions 2025-09-03)
