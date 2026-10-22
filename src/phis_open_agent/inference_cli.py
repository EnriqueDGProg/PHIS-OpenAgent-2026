"""Read-only synthetic sponsor probes; emits no prompt, answer or credential."""

import json
import sys

from .inference import InferenceBlocked, MeterlessClient, MeterlessConfig, NvidiaClient, NvidiaConfig


def main(argv=None, environ=None):
    args = sys.argv[1:] if argv is None else argv
    if args not in (["meterless"], ["nvidia"]):
        print("Usage: python -m phis_open_agent.inference_cli meterless|nvidia", file=sys.stderr)
        return 2
    try:
        result = (MeterlessClient(MeterlessConfig.from_env(environ)).probe() if args == ["meterless"]
                  else NvidiaClient(NvidiaConfig.from_env(environ)).probe())
    except InferenceBlocked as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
