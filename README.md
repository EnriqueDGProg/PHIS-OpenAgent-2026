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

## Independent integration branch

This branch combines the unmerged frontend PR #2 and Python core PR #3, then adds a same-origin synthetic API. To run the integrated workspace, use `cd frontend; npm start` and open `http://127.0.0.1:4173`. Node.js 20+ starts Python 3.11+; no package installation is needed. See [frontend instructions](frontend/README.md) for scenarios and tests. The frontend no longer calculates observations, coverage or comparison means: these come from the Python core through `investigation.v1`.

This remains a bounded, deterministic demo, not a deployed agent or a sponsor-compliant submission. Sponsor statuses remain explicitly `NOT_CONNECTED`, and no private PHIS code or health data is included.
