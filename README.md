# PHIS-OpenAgent-2026
Evidence-first personal health intelligence agent | Open Agent Hackathon 2026 | AI Venture Studio

## Build-window prototype

This branch builds on the synthetic release candidate PR #6 and adds a real local **Meterless World Model Engine** integration. It remains a draft, synthetic-only demo and imports no private PHIS code. See the [Engine conformance matrix](docs/METERLESS_ENGINE_CONFORMANCE_2026-10-22.md) for the official contract, evidence and remaining gates.

Python 3.11+ and Node.js 24 are needed for the Engine-backed API and CLI:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent.agent_cli energy --run-id SYN-RUN-DEMO
$env:WORLD_MODEL_IMPL=(Resolve-Path vendor/meterless-world-model/src/index.ts).Path
node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts
python scripts/meterless_engine_trace.py
```

The emitted dataset and outputs are fictional. Descriptive comparisons do not establish a cause, clinical conclusion or statistical association. Meterless **Engine** passes its pinned official conformance runner locally (8/8); Meterless Runtime/Power, NVIDIA and Zetaris are separate and are not connected in this branch. PR #10 has independent live Zetaris work and is not part of this stack.

The earlier JSONL `SyntheticRunWorldModel` still exists for regression tests and was only inspired by [Meterless World Model](https://github.com/Meterless/Meterless/tree/main/engines/world-model). The API and agent CLI now use the pinned official reference Engine with durable readback. The [execution gate](docs/EXECUTION_GATE_2026-10-22.md) records older checks; the current Engine result is in the [conformance matrix](docs/METERLESS_ENGINE_CONFORMANCE_2026-10-22.md). The response contract is in [contracts/investigation.v1.schema.json](contracts/investigation.v1.schema.json).

## Integrated demo lineage

PR #6 combines the earlier frontend and Python core work. This branch adds the Engine-backed same-origin API. To run it, use `python -m phis_open_agent.api` and open `http://127.0.0.1:4173`. Node.js 24 is required for the Engine bridge; no npm package installation is needed. See [frontend instructions](frontend/README.md) for scenarios and tests. The frontend does not calculate observations, coverage or comparison means: these come from deterministic Python tools through `investigation.v1`.

This remains a bounded, deterministic demo, not a deployed agent or a sponsor-compliant submission. `meterless_engine` is conditionally `VERIFIED` after a successful local write and durable readback; the other sponsor statuses remain `NOT_CONNECTED`. No private PHIS code or health data is included.
