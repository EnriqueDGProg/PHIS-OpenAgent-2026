# PHIS-OpenAgent-2026
Evidence-first personal health intelligence agent | Open Agent Hackathon 2026 | AI Venture Studio

## English-first integrated demo

This public release candidate contains a **synthetic-only, local agent demo**. Its English-first interface queries a Python agent that selects deterministic tools, records evidence lineage, persists World Model decisions for follow-up, and abstains when a question is outside scope or evidence is weak. It imports no private PHIS code. See the [dated build-window audit](docs/BUILD_WINDOW_AUDIT_2026-10-22.md) for historical rules and evidence.

Run the demo with Python 3.11+:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. Node.js 20+ is only needed for the optional `npm start` launcher and frontend tests. The dataset and outputs are fictional. Descriptive comparisons do not establish a cause, clinical conclusion, or statistical association. Zetaris, Meterless, and Nemotron are disconnected in the local demo.

The [execution gate](docs/EXECUTION_GATE_2026-10-22.md) separates real page reads and local tests from blocked sponsor calls. The local run-state prototype follows selected [Meterless World Model](https://github.com/Meterless/Meterless/tree/main/engines/world-model) ideas (append-only events, stable IDs, provenance and a read surface), but is not Nightshift or a complete engine conformance claim. The proposed backend/frontend contract is in [contracts/investigation.v1.schema.json](contracts/investigation.v1.schema.json) with a matching TypeScript declaration.

## Contract and verification

This branch builds on the validated integration release candidate. The frontend does not calculate observations, coverage, or comparison means; those come from the Python core through `investigation.v1`. See [frontend instructions](frontend/README.md) for execution, synthetic evaluation scenarios, tests, visual evidence, and the socketless Chrome verification limit.

This remains a bounded, deterministic local demo, not a deployed agent or a sponsor-compliant submission. Sponsor statuses remain explicitly `NOT_CONNECTED`, and no private PHIS code or health data is included.
