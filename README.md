# PHIS-OpenAgent-2026
Evidence-first personal health intelligence agent | Open Agent Hackathon 2026 | AI Venture Studio

## Build-window prototype

This public branch currently contains a **synthetic-only, local descriptive core**, not a completed agent or sponsor integration. It was written after the 22 October build opening and imports no private PHIS code. See the [dated build-window audit](docs/BUILD_WINDOW_AUDIT_2026-10-22.md) for rules, dependencies, evidence and blockers.

Python 3.11+ is sufficient for this first slice:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent
```

The emitted dataset and outputs are fictional. Descriptive comparisons do not establish a cause, clinical conclusion or statistical association. Zetaris, Meterless and Cursor remain unverified in this prototype.

The [execution gate](docs/EXECUTION_GATE_2026-10-22.md) separates real page reads and local tests from blocked sponsor calls. The local run-state prototype follows selected [Meterless World Model](https://github.com/Meterless/Meterless/tree/main/engines/world-model) ideas (append-only events, stable IDs, provenance and a read surface), but is not Nightshift or a complete engine conformance claim. The proposed backend/frontend contract is in [contracts/investigation.v1.schema.json](contracts/investigation.v1.schema.json) with a matching TypeScript declaration.

The [Zetaris direct REST activation guide](docs/ZETARIS_REST_ACTIVATION.md) describes the documented routes, environment variables, fictional CSV preparation, read-only preflight, explicit file registration and bounded query. Its transport tests use a simulation. Zetaris remains **BLOCKED** until the production HTTP client receives and validates a real `SELECT 1` and synthetic query response.

The [Meterless/NVIDIA activation guide](docs/METERLESS_NVIDIA_ACTIVATION_2026-10-22.md) records the official Runtime and hosted Nemotron routes, a provenance blocker on the unsigned Windows release, and the separate synthetic inference probes. `python -m phis_open_agent.inference_cli meterless` and `... nvidia` return `BLOCKED` when credentials are absent. Simulated transport tests do not constitute real sponsor calls.
