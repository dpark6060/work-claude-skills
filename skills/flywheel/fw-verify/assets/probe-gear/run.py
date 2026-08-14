"""fw-verify probe gear entrypoint.

Fixed plumbing: echoes run-id, config, inputs, and environment to the job log,
runs the injected payload, then exits with the configured exit_code. The
fw-verify skill injects test code between the FWV-PAYLOAD markers.
"""

import json
import os
import sys

CONFIG_PATH = "/flywheel/v0/config.json"


def main() -> int:
    """Echo the gear runtime state, run the payload, exit with configured code."""
    with open(CONFIG_PATH) as fp:
        raw = json.load(fp)
    config = raw.get("config", {})
    print(f"[fwv-probe] run_id={config.get('run_id', 'unset')}")
    print(f"[fwv-probe] config={json.dumps(config, default=str)}")
    print(f"[fwv-probe] inputs={json.dumps(raw.get('inputs', {}), default=str)}")
    print(f"[fwv-probe] destination={json.dumps(raw.get('destination', {}), default=str)}")
    if config.get("debug"):
        print(f"[fwv-probe] env={json.dumps(dict(os.environ))}")

    # >>> FWV-PAYLOAD-START  (fw-verify injects test code below this line)
    # <<< FWV-PAYLOAD-END

    exit_code = int(config.get("exit_code", 0))
    print(f"[fwv-probe] exiting with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
