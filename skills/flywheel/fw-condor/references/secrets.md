---
type: Operations Guide
title: Secrets Delivery to Condor and Engines
description: How secrets reach condor, engine VMs, and gear containers — sops secrets.yaml, engineGearEnvironment, drone secret, cloud credentials, and rotation procedures.
tags: [condor, secrets, sops, secrets.yaml, engineGearEnvironment]
timestamp: 2026-07-24T00:00:00Z
---

# Secrets Delivery to Condor and Engines

## secrets.yaml — where it lives and how to edit it

`secrets.yaml` is a **sops-encrypted values overlay in each site's GitOps repo** (it is
NOT part of the condor chart repo). It merges over values.yaml at deploy time — same key
paths, under the `flywheel:` root. Keys are held by cloud KMS; you need cloud auth
(`gcloud auth application-default login` etc.) to decrypt.

```bash
sops secrets.yaml                                                # edit (re-encrypts on save)
sops -d --extract '["global"]["droneSecret"]' secrets.yaml        # read one value
sops -d --extract '["<site>"]["global"]["droneSecret"]' secrets.yaml   # multi-site repos
sops --set "['flywheel']['some']['key'] \"$NEW_VALUE\"" secrets.yaml    # set
```

Bootstrap-generated secrets are base64-encoded (pipe through `base64 -d`). MR pipelines
run `plan:validate_secrets`; bypass temporarily with `VALIDATE_SECRETS: false` in
`.gitlab-ci.yml` (remove it after). Send secret values to customers only via YoPass
(https://yp.flywheel.io).

## Gear secrets: engineGearEnvironment

The supported way to hand credentials to gears. JSON env map set per profile; the engine
exposes the key-value pairs as environment variables inside every gear container that
profile's engines run (pair with a gear-name whitelist to scope it).

```yaml
# secrets.yaml (sops)
flywheel:
    condor:
        profiles:
            my-profile:                       # must match the profile key in values.yaml
                engineGearEnvironment:
                    DSI_USERNAME: "flywheel"
                    DSI_PASSWORD: "Password123"
```

Three rules from the chart README, all load-bearing:

1. **Quote every value, even numerics** — unquoted values make the engine VM fail to start.
2. **Delete the condor pod(s)** for that profile after the pipeline succeeds.
3. **Delete the profile's existing engine VMs** — they have the old env baked in and
   will never pick up the change.

Real-world example: NACC sandbox passes `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` /
`AWS_DEFAULT_REGION` to an S3-using gear this way.

**Central (tenant) sites cannot do this** — engineGearEnvironment secrets don't work
there and there is no workaround as of 2026-07 (tickets PLT-6142, FLYW-39753).

## The full delivery chain (and its security implication)

```
secrets.yaml (sops) ─merge→ helm value profiles.<id>.engineGearEnvironment
  → k8s Secret <release>-condor-<id>-secret-env  (key FW_ENGINE_GEAR_ENVIRONMENT)
  → envFrom → condor pod env
  → cloud-init user-data
  → /etc/environment on the engine VM (plaintext, mode 0755)
  → engine process → gear container env
```

Cloud-init user-data is readable by anything on the instance and often by anyone with
instance-describe permissions in the cloud account. The same hop also carries
`SCITRAN_CORE_DRONE_SECRET`, stackdriver credentials, and Wiz API creds. Don't put
anything in `engineGearEnvironment` you wouldn't put on the VM's disk in plaintext.

## Secrets the chart itself renders (k8s objects)

| Values key | k8s object | Delivery |
|---|---|---|
| `profiles.<id>.engineGearEnvironment` | Secret `<fullname>-secret-env` per profile | envFrom on condor |
| `global.droneSecret` (or existing secret via `global.droneSecretName`) | inline env / envFrom | `SCITRAN_CORE_DRONE_SECRET` |
| `amazon.keyId`/`accessKey` | Secret `aws-credentials` (fixed name!) — literal `[default]` aws credentials file | mounted at `/root/.aws` |
| `google.serviceAuth.credentials` (already base64) | Secret `service-auth` (fixed name!) | mounted at `/service_auth`, `GOOGLE_APPLICATION_CREDENTIALS` |
| `azure.clientId`+`clientSecret` (both base64) | Secret `<fullname>-azure-secret` | envFrom, only when NOT workloadIdentity |
| `azure.generateSSHKey` | Secret `<fullname>-azure-engine-ssh-key` (generated at render!) | mounted /keys; init container derives pubkey |
| `monitoring.metrics.remoteWriteUser/Password` | Secret `<fullname>-vector-monitoring-secret-env` — required unless argoVaultPlugin | envFrom always |
| stackdriver creds | Secret `<fullname>-logging-sink-gcp-secret` | envFrom when enabled |

Azure auth precedence: nothing set → managed identity; `clientId`+`clientSecret` (base64)
→ service principal; `workloadIdentity: true` → workload identity, where `clientId` is
NOT base64 (it becomes a ServiceAccount annotation). The clientSecret comment in
values.yaml says it plainly: "DON'T place in values.yaml! base64" — it goes in
secrets.yaml.

## Rotation procedures

**Drone secret** — preferred: run the site pipeline with variable
`ROTATE_DRONE_SECRET=true`. Manual: generate
(`openssl rand -base64 50 | tr -dc 'a-zA-Z0-9' | head -c 42`), set
`flywheel.global.droneSecret` in secrets.yaml, merge, then
`kubectl rollout restart deployment,statefulset -l app.kubernetes.io/instance=flywheel`.
Legacy V2 engines: edit `/opt/flywheel/prod-override.yml` on the box and restart the
engine container. HPC clients need the new secret too (send via YoPass).

**Azure service principal (condor)** — customer sends new Client Secret Value →
`echo -n "<secret>" | base64` → `sops secrets.yaml` →
`flywheel.condor.azure.clientSecret` (clientId unchanged) → MR.

**Multiprovider credentials** live in mongo, not secrets.yaml:
`db.providers.findOne({_id: ObjectId("<provider_id>")})` → `creds` section. See
MULTIPROVIDER_ROTATE_CREDS.md for rotation.

# Citations

[1] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/helm/condor/README.md — "Condor Profile Secret Env example" (the three warnings)
[2] https://gitlab.com/flywheel-io/product/backend/condor/-/blob/master/ops/cloud-init.yml.j2 — the /etc/environment export block
[3] https://gitlab.com/flywheel-io/product/backend/condor/-/tree/master/helm/condor/templates — secrets-profiles-env.yaml, amazon-secret.yaml, google-secret.yaml, azure-secrets.yaml, secret-vector-monitoring-env.yaml
[4] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/infrastructure/sops-secrets.md
[5] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/infrastructure/rotate-drone-secret.md
[6] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/infrastructure/update_condor_service_principal.md
[7] https://gitlab.com/flywheel-io/product/internal-documentation/-/blob/main/docs/operations/configuration/condor/static-engine.md — FW_ENGINE_GEAR_ENVIRONMENT on V2 engines
[8] Central limitation thread: https://flywheel-io.slack.com/archives/GPFLK2FA6/p1783526145859069 (PLT-6142, FLYW-39753)
[9] installer3 secret generation: https://gitlab.com/flywheel-io/docker/installer3/-/tree/master/scripts/fwsecrets
