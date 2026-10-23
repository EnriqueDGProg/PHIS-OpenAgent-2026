# PHIS Open Agent 2026

Evidence-backed investigation of a fictional 84-day energy and sleep record for the [Open Agent Hackathon 2026](https://hackathon.genai.works/event/open-agent-hackathon-2026). Every observation is synthetic. This public repository contains competition-window code, not private PHIS source or real health data.

## Release candidate

This independent draft RC combines the PR #11 UX lineage, PR #10 live Zetaris adapter, PR #12 pinned official Meterless World Model Engine, and the adversarial suite. The [final integration report](docs/FINAL_INTEGRATION_RC_2026-10-23.md) records provenance, native HTTP/Chrome evidence, and PASS/FAIL/BLOCKED gates. No branch was merged or deployed.

The Python agent selects deterministic coverage, trend, and comparison tools. Zetaris live mode reads and validates all 156 fictional source rows before analysis; a failed query abstains without substituting the local fixture. The official World Model Engine persists synthetic decision events, reopens its log in a fresh process, and changes the follow-up tool choice. Each sponsor proof has its own trace ID. Meterless Runtime/Power and NVIDIA inference remain separate and disconnected.

## Run locally

Requires Python 3.11+ and Node.js 24. The core and Engine require no Python or npm packages, external account, or paid service.

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. The default `SYNTHETIC_LOCAL_ONLY` mode uses only fictional local rows. Engine state is under ignored `.local-state/.world/`. `PHIS_SYNTHETIC_STATE_FILE` chooses a different private local namespace. `GET /api/health` reports process health, not sponsor verification.

For a previously authorized local Zetaris instance containing the 156-row fictional table, set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS`, `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, and `ZETARIS_API_KEY` only in the API process environment. Use the documented direct `/api/v1.0` endpoint. Keep credentials and the local Compose bundle outside this repository. The API calls datasource listing, `SELECT 1`, and the bounded synthetic query on each investigation. See [Zetaris activation](docs/ZETARIS_REST_ACTIVATION.md) and [frontend instructions](frontend/README.md).

## Verify

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
python -m unittest tests.evaluation.test_adversarial_battery -q
python -m tests.evaluation.run_eval
node --test frontend/tests/*.test.mjs
$env:WORLD_MODEL_IMPL=(Resolve-Path vendor/meterless-world-model/src/index.ts).Path
node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts
python scripts/meterless_engine_trace.py
```

For native localhost checks against a running API, use `python scripts/native_http_smoke.py` in local mode or `python scripts/native_live_zetaris_smoke.py` in live mode. Installed Chrome plus an existing Playwright module can run `frontend/tests/e2e_native_chrome.mjs` with `PHIS_PLAYWRIGHT_MODULE` set to its absolute `index.mjs` path. No installation is performed by that script.

The `investigation.v1` contract is in [contracts/investigation.v1.schema.json](contracts/investigation.v1.schema.json). Comparisons are descriptive; the 14-observation threshold is an operational completeness rule. The agent gives no diagnosis, treatment, causal finding, or unsupported statistical claim.
