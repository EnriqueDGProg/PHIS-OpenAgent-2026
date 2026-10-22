# PHIS Open Agent · synthetic local release candidate

The English-first demo calls `POST /api/investigations`. This route runs the Python `SyntheticAgent`, which chooses deterministic tools based on the question, coverage, and persisted World Model state. The optional adapters remain available in the repository, but this demo does not call sponsors or claim sponsor verification. All participant records are fictional.

## Run locally

Requires Python 3.11+ and Node.js 20+. No package installation is needed for the local demo.

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. Alternatively, run `npm start` from `frontend/`; the launcher starts the same Python server. Synthetic state is stored in Git-ignored `.local-state/agent-events.jsonl`. Set `PHIS_SYNTHETIC_STATE_FILE` to choose another local path. Keep this file across restarts so follow-up investigations can recover previous decisions. The browser stores only the synthetic ID of the last comparable run.

`GET /api/health` reports synthetic mode and disconnected sponsors. The POST accepts `question`, optional `parent_run_id`, and `scenario`: `normal`, `insufficient`, or `tool_error`. The latter two are explicitly synthetic evaluation controls, available in the UI at `/?scenario=insufficient` and `/?scenario=tool_error`.

## Tests and visual evidence

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
```

`tests/test_integration_api.py` exercises the actual HTTP handler in process. It verifies that the agent runs, the response reflects core measurements, the trace records real phases, weak coverage and tool errors cause abstention, and a new server instance recovers persisted World Model state. `tests/test_english_copy.py` checks static UI text and returned agent copy across success, follow-up, and abstention states. Node tests validate `investigation.v1` provenance and disconnected sponsor status.

If Playwright is already available, capture real Chrome desktop and mobile rendering without installing dependencies:

```powershell
$env:PHIS_PLAYWRIGHT_MODULE='ABSOLUTE_PATH_TO_PLAYWRIGHT/index.mjs'
node frontend/tests/e2e_chrome.mjs
```

This test uses the checkout's real frontend files and runs the Python API handler for every POST through a socketless bridge. Each POST starts a new Python process, so the follow-up checks disk persistence. The bridge intercepts transport because this sandbox blocks connections to `127.0.0.1`; **the test does not establish that Chrome reached the HTTP server over a real socket**. It checks English copy, desktop/mobile layout, keyboard access to source records, response states, and horizontal overflow. Screenshots are saved as `docs/evidence/en-*.png`.

## Contract and limits

`investigation.v1` remains unchanged. The UI renders only tools present in the persisted trace; chart values and missing days come from Python. Comparisons are descriptive. The gate of 14 observed days per period is an operational completeness rule, not statistical significance. The demo makes no causal, clinical, or medical advice claim, and there is no official Meterless, Nemotron, or Zetaris integration.
