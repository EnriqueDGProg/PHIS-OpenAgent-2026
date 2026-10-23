# PHIS evidence UI

The English UI calls the Python `POST /api/investigations` endpoint and displays only returned tool traces, source IDs, and deterministic findings. The chart keeps missing days as gaps. The evidence panel shows separate Zetaris, Meterless Engine, Meterless Runtime, and NVIDIA statuses.

Start the API from the repository root with `PYTHONPATH=src` and `python -m phis_open_agent.api`; open `http://127.0.0.1:4173`. `npm start` from this directory starts the same Python server. Node.js 24 is required for the official Engine bridge. No npm install is needed for the UI.

Default mode is `SYNTHETIC_LOCAL_ONLY`. Set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS` and the documented Zetaris process environment only when the authorized local service and 156-row fictional table are ready. Live mode refuses the local evaluation scenarios. Missing configuration, invalid credentials, incomplete rows, or transport failure produces an abstention and no local fallback. The browser stores only the last synthetic parent run ID.

Run `node --test frontend/tests/*.test.mjs` for contract tests. For native HTTP and installed Chrome, set `PHIS_PLAYWRIGHT_MODULE` to an existing Playwright `index.mjs` and run `node frontend/tests/e2e_native_chrome.mjs`. Set `PHIS_EXPECT_MODE=LIVE_SYNTHETIC_ZETARIS` for the live-mode path. The script writes new integration screenshots under `docs/evidence/`. Local mode also tests `/?scenario=insufficient` and `/?scenario=tool_error`. See the [integration report](../docs/FINAL_INTEGRATION_RC_2026-10-23.md) for observed results and the earlier socketless test boundary.
