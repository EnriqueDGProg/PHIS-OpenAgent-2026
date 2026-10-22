# PHIS synthetic release candidate — 22 October 2026

## Composition and boundaries

This branch starts at PR #4 (`0df6721`) for the visual experience. It takes the bounded orchestrator and World Model from PR #5 (`272b409`) and the updated optional inference/Zetaris adapters and their simulated transport tests from PR #3 (`30e5f55`). It leaves `main` untouched. `POST /api/investigations` calls `SyntheticAgent`; the previous independent investigation sequence has been removed. No private PHIS code, real health record, credential, paid service, sponsor installation, or live sponsor call is used.

The public response stays `investigation.v1`. Optional `phase`, `reason_code`, and `parent_event_id` fields on `tool_trace` carry agent decisions; the rest of the contract stays compatible with PR #4. Numbers, points and source IDs come from the deterministic Python tools. The agent performs a full 84-day trend, checks recent coverage, compares two 28-day windows only when covered, and conditionally inspects sleep. It abstains on unsupported questions, weak coverage and tool errors. A follow-up reads the append-only World Model from disk, checks that the parent run finished with a verified response, then chooses the next tool from its persisted comparison.

The local state file is ignored by Git and contains only synthetic run events and source IDs. It does not store raw observations or the question text. The browser stores only the synthetic parent run ID. All sponsor proofs are `NOT_CONNECTED`. The Meterless-inspired World Model does not establish official Meterless Engine conformance; the inference probes from PR #3 are optional connectivity code and are not invoked by this demo.

## Reproduce

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
python -m phis_open_agent.api
```

Then open `http://127.0.0.1:4173`. Submit the energy question, click **Investigar sueño**, restart the server, reload the page, click **Investigar sueño** again, and submit. The parent run ID stored in the browser and the World Model file must survive restart. Use `/?scenario=insufficient` and `/?scenario=tool_error` for explicitly synthetic failure states.

Chrome visual check without new installations, using an existing Playwright module and installed Chrome:

```powershell
$env:PHIS_PLAYWRIGHT_MODULE='RUTA_ABSOLUTA_A_PLAYWRIGHT/index.mjs'
node frontend/tests/e2e_chrome.mjs
```

## Verification matrix

| Gate | Result | Evidence |
| --- | --- | --- |
| Python unit + handler integration | PASS | `python -m unittest discover -s tests -q`; 35 tests after final integration. |
| Frontend contract tests | PASS | `node --test frontend/tests/*.test.mjs`; 6 tests. |
| Clean clone | PASS with local bundle | A new `git clone --branch codex/phis-release-candidate-20261022 phis-rc.bundle phis-rc-clean-clone` at commit `b1e5403` passed 35 Python and 6 Node tests, then remained clean. Direct HTTPS clone was blocked by the sandbox (`getaddrinfo() thread failed to start`); the bundle was created from the pushed commit. |
| Browser desktop and mobile | PASS with intercepted transport | Real installed Chrome, 1440×900 and 390×844; no horizontal mobile overflow or page errors. |
| Follow-up after Python process restart | PASS | Each browser POST starts a new Python handler process; persisted parent decision changes the follow-up tools. |
| Sparse coverage and tool error | PASS | Both abstain; no comparison or stale numbers in failed response. |
| Actual localhost HTTP socket in this sandbox | FAIL / environment block | Python HTTP clients received `WinError 10013`; Chrome received `ERR_CONNECTION_TIMED_OUT` or `ERR_NETWORK_ACCESS_DENIED`. No security settings were changed. The same API handler was tested in-process and in Chrome through a socketless route bridge. Repeat native HTTP smoke test in an unrestricted environment before release. |
| Sponsor integrations | BLOCKED | Optional adapters present, but no verified live response or official Meterless conformance. |

## Real Chrome captures

- [Desktop answer](evidence/rc-desktop-pass.png): 84-day energy series, actual plan/tool phases and descriptive comparison.
- [Desktop follow-up](evidence/rc-desktop-followup.png): recovered prior decision, sleep coverage and trend, no comparison claim.
- [Mobile answer](evidence/rc-mobile-pass.png): 390 px layout without horizontal overflow.
- [Insufficient coverage](evidence/rc-desktop-insufficient.png): abstention with source gaps.
- [Tool error](evidence/rc-desktop-error.png): no stale numeric result.

The captures are from real Chrome rendering the repository UI and real Python handler responses. The test intercepts the network transport because the execution sandbox blocks loopback sockets. They do not prove an unrestricted production HTTP connection.

## Remaining review gates

Run a native HTTP smoke test and accessibility review in an unrestricted environment. Keep all sponsors disconnected until actual vendor requests and receipts are verified. Before merging, review the additive trace extension and the local state lifecycle. This Draft PR must not be merged or deployed as a sponsor-compliant submission yet.
