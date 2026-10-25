# Live synthetic Zetaris orchestration — 22 October 2026

## Scope and mode boundary

This branch starts from PR #6 at `74313b4` and reuses the PR #3 direct REST adapter. Set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS` on the PHIS API process to require a real Zetaris read for every investigation. The API runs datasource listing, `SELECT 1`, and the bounded 156-row synthetic query through production HTTP transport. The complete returned rows are validated before they are passed to `SyntheticAgent`; the deterministic tools then compute coverage, series and comparison from those rows. The generator in `investigation.py` is called only in the separately selected `SYNTHETIC_LOCAL_ONLY` mode (the default).

The live mode does not accept local evaluation scenarios. Missing credentials, HTTP failure, simulated transport, malformed response or incomplete/changed CSV produces `status: ERROR`, `reason_code: source_error`, an abstention, empty coverage/series/comparison and no local fixture fallback. A configured but failing live HTTP call sets Zetaris proof `FAILED`; absent configuration or simulated transport remains `NOT_CONNECTED`. The World Model persists the source verification or source failure event without storing raw rows, token or question text.

In `investigation.v1`, a successful live response uses `mode: LIVE_SYNTHETIC_ZETARIS` and `dataset_id: PHIS-SYN-84D-v1-ZETARIS`. Its `zetaris.synthetic_query` tool trace carries the real request ID, query ID, SQL SHA-256 and all 156 fictional source IDs; the Zetaris sponsor proof is `VERIFIED` with the same request ID. Tool and finding source IDs are selected from those retrieved rows. The two SQL metadata fields are optional additions to the typed v1 trace, so existing local responses remain valid. All Meterless and NVIDIA proofs remain `NOT_CONNECTED`; this is no claim of Meterless Build, Power, Engine or World Model compliance. The browser contract accepts a live PASS only when the Zetaris proof matches a 156-source query trace.

## Reproduce without storing credentials

Keep the official local Compose running and healthy. Use a short-lived local login token and numeric organization ID from its documented UI login flow (also shown in the bundle's `verify.sh`), and set these **only in the API process environment**:

```powershell
$env:PHIS_DATA_MODE = 'LIVE_SYNTHETIC_ZETARIS'
$env:ZETARIS_REST_URL = 'http://127.0.0.1:8888/api/v1.0'
$env:ZETARIS_ORG_ID = '<numeric local organization ID>'
$env:ZETARIS_API_KEY = '<ephemeral local login token>'
$env:PYTHONPATH = 'src'
python -m phis_open_agent.api
```

Do not put the actual values in a command transcript, Git file or browser query string. `GET /api/health` reports the selected mode and process health, not sponsor verification. A successful `POST /api/investigations` supplies the proof. To return to the explicitly separate local demo, set `PHIS_DATA_MODE=SYNTHETIC_LOCAL_ONLY` and remove the Zetaris credentials from that process. The localhost Zetaris stack was not restarted for this work.

## Real HTTP evidence, sanitized

The official local Compose reported `postgres`, `driver`, `api` and `ui` **running/healthy** before testing. PHIS ran on a temporary `127.0.0.1` port, called the already running Zetaris REST service on `127.0.0.1:8888`, and served actual HTTP requests. Only fictional data was involved. No raw response, token, password or organization ID is published.

| Gate | Result | Evidence |
| --- | --- | --- |
| Energy investigation, real HTTP | **PASS** | `SYN-RUN-e054d5e86dd2`; `LIVE_SYNTHETIC_ZETARIS`; Zetaris request/proof `3fcb32f9-92ae-4fcb-b4ce-7fe41e8a7c64`; tool trace matched; 156 source IDs; comparison cited 53 source IDs; trend → coverage → comparison → sleep coverage. |
| Sleep follow-up, real HTTP | **PASS** | `SYN-RUN-4311a42d8b83`; parent ID matched; a separate Zetaris request/proof `d4efd4c7-1540-42b3-8def-347e60274ffc`; trace matched; 156 source IDs; coverage → trend. |
| Follow-up after restarting only PHIS API | **PASS** | Recovered parent decision from ignored JSONL state; fresh Zetaris request/proof `f5e02629-bd44-474d-84a7-d2fdbafb2920`; trace matched; 156 source IDs; coverage → trend. |
| Deliberately invalid test token, real HTTP | **PASS for failure control; authentication failed as intended** | `status: ERROR`, `reason_code: source_error`, Zetaris `FAILED`; abstention only, zero coverage/series, null comparison and no fixture fallback. The test token was a literal invalid placeholder, not a secret. |
| Actual live payload through frontend validator | **PASS** | The final typed payload used request `3f74af86-0728-4692-adf3-0fc937fba56a`, query `bd39b313-b76f-44cd-a1e0-b3b2d882a1b1`, SQL SHA-256 `a3c8e8b46e908b22b824076f5852857b209e138cd01e96ec74d9b71921d77e9c` and 156 sources. It passed `validateInvestigation`; top-level and trace keys fit the v1 schema, proof request ID matched the query trace, and every analysis trace/finding source ID belonged to those 156 IDs. The temporary ignored response was deleted after this check. |
| Unit/handler and frontend contract suites | **PASS** | 39 Python tests and 8 Node tests, including missing credentials, rejection of simulated transport and frontend proof checks. These suites do not count as live Zetaris evidence. |

The API server processes used for these probes were stopped after testing. The official Zetaris Docker stack was left running. The earlier PR #6 Chrome test used an intercepted transport; the HTTP calls above used actual localhost sockets and the real Zetaris driver/API.
