# PHIS Open Agent 2026

Evidence-backed investigation of a fictional **180-day, 1,080-record** energy and sleep dataset for the [Open Agent Hackathon 2026](https://hackathon.genai.works/event/open-agent-hackathon-2026). Every observation is synthetic. This standalone public repository contains no real health data. Its five original PHIS Discovery modules are expressly authorized preexisting code; see the [scoped MIT license and provenance notice](src/phis_master/NOTICE.md). The vendored Meterless World Model retains its [Apache-2.0 license](vendor/meterless-world-model/LICENSE).

The [judge guide to the fictional 180-day generator](docs/SYNTHETIC_GENERATOR_JUDGE_GUIDE_2026-10-25.md) separates known simulated mechanisms from observational associations independently reported by PHIS Discovery. The UI leads with the full recorded history and keeps the fixed 28-day comparison under **Recent changes**.

## Release candidate

The public `main` release contains the exact PR #43 application code SHA `9c871532a2debd9877483dad9c937dbb881508ad`. The release includes the 180-day scientific scenario, Zetaris adapter, official Meterless World Model Engine, bounded v4 planner, NVIDIA direct adapter and adversarial suite. Its [authenticated same-run receipt](submission/FINAL_COMBINED_RECEIPT.md) and [submission package](submission/README.md) distinguish current proof from earlier historical gates. The release and submission materials are merged into `main`. GitHub hosts source code, not a running application.

The Python agent selects deterministic coverage, trend, and Discovery tools. Zetaris live mode reads and validates all 1,080 fictional source records in six bounded pages; a failed query abstains without substituting the local fixture. The World Model Engine persists synthetic decision events, reopens its state in a fresh process, and changes follow-up decisions. Discovery alone computes scientific results. The authenticated PR #43 Chrome run genuinely combined Zetaris, NVIDIA PLAN and CRITIQUE, PHIS Discovery and Meterless Engine on one application SHA. Meterless Runtime/Power and Nightshift remain disconnected. The credential-free local mode uses only synthetic fixtures; its Zetaris and NVIDIA statuses are `NOT_CONNECTED`.

## Choose how to evaluate PHIS

1. **Quick start, no credentials:** follow [Run locally](#run-locally) to inspect the 180-day synthetic Energy/Sleep investigations, qualified evidence, clinical abstention and official Meterless World Model Engine. The browser correctly labels Zetaris and NVIDIA `NOT_CONNECTED` in this mode.
2. **Genuine NVIDIA review using your key:** after starting the same application with `NVIDIA_API_KEY` and `PHIS_INFERENCE_PROVIDER=nvidia_direct`, use `/?analysis=v4`. The source remains `SYNTHETIC_LOCAL_ONLY`, and only genuine provider receipts can verify NVIDIA; this does not require Zetaris.
3. **Full sponsor reproduction:** provision an authorized Zetaris instance, register the exact frozen 1,080-row fictional dataset, configure the documented [Zetaris adapter](#run-locally) and genuine NVIDIA API credentials, then run `/?analysis=v4` with `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS`. An API key alone is insufficient without the registered table. This more demanding setup was verified on the owner's preconfigured local stack, **not** independently from a new judge-owned Zetaris environment. Review the [authenticated combined-run receipt](submission/FINAL_COMBINED_RECEIPT.md), [desktop/mobile evidence](submission/evidence/) and [sponsor claim ledger](submission/SOURCES_AND_CLAIMS.md).

**Evidence rule:** archived sponsor receipts attest to historical authenticated runs, not to an unauthenticated judge's current local process. All demonstration observations are fictional; PHIS Discovery associations are not causal or clinical findings.

## Run locally

Requires Python 3.11+ and Node.js 24. The core and Engine require no Python or npm package installation, external account, or paid service. From a clean public clone, run the published `main` branch:

```powershell
git clone https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026.git
cd PHIS-OpenAgent-2026
```

```powershell
$env:PYTHONPATH=(Resolve-Path src).Path
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. The default `SYNTHETIC_LOCAL_ONLY` mode uses only fictional local rows. `/?analysis=v4` exercises the bounded agentic planner; the default `v3` route shows the deterministic scientific investigation. Engine state is under ignored `.local-state/.world/`. `PHIS_SYNTHETIC_STATE_FILE` chooses a different private local namespace. `GET /api/health` reports process health, not sponsor verification.

Three [actual local example inputs and outputs](submission/EXAMPLE_INPUTS_OUTPUTS.md) show Energy PASS, a parent-linked Sleep PASS and clinical-scope abstention. This no-key judge path does not imply live sponsor calls.

In v4, PHIS Discovery's qualified observational findings and the separate Nemotron interpretation have independent statuses: a model abstention or inference failure does not erase scientifically valid PHIS results. The model cannot turn an association into a causal or clinical claim. See the [scientific facts and review release gate](docs/NEMOTRON_SCIENCE_REVIEW_GATE_2026-10-25.md) for the exact genuine hosted receipt, simulated regression boundaries and screenshot.

For a previously authorized local Zetaris instance containing the 1,080-record fictional table, set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS` and choose one documented channel. The existing local stack uses `ZETARIS_CHANNEL=ui_proxy`, `ZETARIS_BASE_URL=http://127.0.0.1:3000`, `ZETARIS_USERNAME` and `ZETARIS_PASSWORD`; the login response supplies a session token and organisation ID. Alternatively, the direct `/api/v1.0` route requires `ZETARIS_REST_URL`, `ZETARIS_ORG_ID` and `ZETARIS_API_KEY`. Set credentials only in the API process environment. Keep credentials and the local Compose bundle outside this repository. The API calls datasource listing, `SELECT 1`, and six bounded synthetic pages on each investigation. See [the verified UI-proxy route](docs/ISSUE_27_LIVE_ZETARIS_RECOVERY_2026-10-23.md), [direct REST activation](docs/ZETARIS_REST_ACTIVATION.md), and [frontend instructions](frontend/README.md).

The optional direct NVIDIA route uses the [official hosted chat-completions API](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-5-lightning-30b-a3b-infer) and defaults to the free endpoint model `nvidia/nemotron-3.5-lightning-30b-a3b`. The documented staging model `stg/nvidia/nemotron-3.5-bolt-e4b` remains an explicit `NVIDIA_MODEL` override. After the account owner enables a free API key, set `NVIDIA_API_KEY` privately in the API process and `PHIS_INFERENCE_PROVIDER=nvidia_direct`; use `/?analysis=v4`. The key is never sent to the browser or stored by the app. A simulated transport or missing provider receipt never verifies Nemotron. Direct NVIDIA does not establish Meterless Power or Runtime. Do not send real health data to this trial API. Cursor is optional per event support and is not a runtime dependency.

## Verify

```powershell
$env:PYTHONPATH=(Resolve-Path src).Path
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
