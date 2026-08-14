# Condor Reference Guides

* [Condor Deployment and Engine Scaling](deployment-and-scaling.md) - How condor and engine VMs are deployed — the k8s shape, the scaling algorithm, engine VM boot lifecycle, static vs dynamic engines, multiprovider mode, and GPU engines.
* [Condor / Engine Lingo](lingo.md) - Concrete, code-grounded definitions of the terms used around Flywheel job execution — compute provider, engine, worker, condor, profile, static engine, drone, perimeter, zombie.
* [Condor values.yaml Reference](values-yaml.md) - Every key in the condor helm chart values.yaml — what it controls, its env var, its real default (helm vs code), plus known chart sharp edges.
* [Engine Operations and Troubleshooting](operations.md) - Day-to-day engine ops — restarting static engines, scaling down, finding engine logs, zombie hunts, debugging "job not picked up", Central tenant quirks, legacy V2 engines.
* [Secrets Delivery to Condor and Engines](secrets.md) - How secrets reach condor, engine VMs, and gear containers — sops secrets.yaml, engineGearEnvironment, drone secret, cloud credentials, and rotation procedures.
