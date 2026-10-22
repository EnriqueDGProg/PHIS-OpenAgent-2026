# PHIS Open Agent · English-first integrated release candidate

The English-first demo calls `POST /api/investigations`. This route runs the Python `SyntheticAgent`, which chooses deterministic tools based on the question, coverage, and persisted World Model state. Two explicit modes are available: local synthetic fixtures and live reads of **synthetic** rows from Zetaris. A live result is shown only when Zetaris returns verified rows and matching query proof. All participant records are fictional. Meterless and Nemotron remain disconnected.

## Run

Requires Python 3.11+ and Node.js 20+. The local mode needs no package installation or external service.

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. Alternatively, run `npm start` from `frontend/`; the launcher starts the same Python server. Synthetic state is stored in Git-ignored `.local-state/agent-events.jsonl`. Set `PHIS_SYNTHETIC_STATE_FILE` to choose another local path. Keep this file across restarts so follow-up investigations can recover previous decisions. The browser stores only the synthetic ID of the last comparable run.

For live Zetaris, start the already provisioned local Zetaris service with the published synthetic CSV loaded. Set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS`, `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, and `ZETARIS_API_KEY` in the **PHIS API process environment** before starting the server. See [Zetaris activation](../docs/ZETARIS_REST_ACTIVATION.md) and [live orchestration](../docs/LIVE_ZETARIS_ORCHESTRATION_2026-10-22.md). Do not put real values in Git, browser URLs, test output, or screenshots. The current consolidation environment has no Zetaris configuration or reachable local endpoint; live success must be verified in a provisioned environment.

`GET /api/health` reports the selected mode, not sponsor verification. The POST accepts `question`, optional `parent_run_id`, and `scenario`. The `insufficient` and `tool_error` scenarios are local-only evaluation controls at `/?scenario=insufficient` and `/?scenario=tool_error`; live mode rejects them. Missing configuration, failed HTTP, or invalid rows in live mode produce `source_error` and abstention with no local fixture fallback.

## Tests and visual evidence

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
```

`tests/test_integration_api.py` exercises the actual handler in process, including source failure without fallback. `tests/test_english_copy.py` checks static UI text and agent copy across success, follow-up, and abstention. The PR #8 adversarial suite runs within the Python discovery command; its standalone builder checks should not be mistaken for live Zetaris proof. Node tests validate `investigation.v1`, source IDs, and matching Zetaris query proof.

If Playwright is already available, capture real Chrome desktop and mobile rendering without installing dependencies:

```powershell
$env:PHIS_PLAYWRIGHT_MODULE='ABSOLUTE_PATH_TO_PLAYWRIGHT/index.mjs'
node frontend/tests/e2e_chrome.mjs
```

The `e2e_chrome.mjs` test uses a socketless bridge to the actual Python API handler and covers keyboard evidence access and all local states. Its captures are `docs/evidence/en-*.png`.

For **native HTTP** from Chrome to the Python server, run in an environment permitting loopback sockets:

```powershell
$env:PYTHONPATH='src'
python tests/native_http_e2e.py
$env:PHIS_PLAYWRIGHT_MODULE='ABSOLUTE_PATH_TO_PLAYWRIGHT/index.mjs'
node frontend/tests/e2e_http_chrome.mjs
```

The native tests cover desktop/mobile, follow-up after an API restart, and live-mode source failure without fallback. `node frontend/tests/e2e_http_chrome.mjs --live` additionally requires a real, preconfigured Zetaris service and asserts a `VERIFIED` proof; it was **not run successfully in this environment**. Native HTTP captures are `docs/evidence/consolidated-http-*.png`.

## Contract and limits

`investigation.v1` adds optional query metadata fields and a distinct `LIVE_SYNTHETIC_ZETARIS` mode without changing the local response shape. The UI renders only tools present in the persisted trace; chart values and missing days come from Python. Comparisons are descriptive. The gate of 14 observed days per period is an operational completeness rule, not statistical significance. The demo makes no causal, clinical, or medical advice claim. Zetaris proof is per-run; Meterless and Nemotron are not connected.
