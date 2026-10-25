# Final integrated acceptance gate — 25 October 2026

**Decision: NO-GO for the combined hosted v4 submission path.** This is an acceptance record, not a change to science, providers, contracts, or UI. It starts at PR #50 commit `9a01202611332d4fe8de7d59c1e3854055776c21`; protected PR #49 was not changed. The single authentic Chrome investigation reached authenticated Zetaris, PHIS Discovery, NVIDIA's hosted planner and critic, and the official Meterless World Model Engine. The final critique failed strict validation, so PHIS correctly withheld a model-endorsed result. No second hosted attempt was made: the rejected response body and granular validator reason were not retained, so there is no concrete defect to correct and test before a permitted retry.

## The one authentic run

- **Run:** `SYN-RUN-e28646fe2cb1`; Energy question, `investigation.v4`, `LIVE_SYNTHETIC_ZETARIS`, entirely fictional participant data. Installed Chrome sent exactly one investigation POST to an isolated API at `http://127.0.0.1:4203/?analysis=v4`; HTTP 200 returned `BLOCKED/invalid_critique`. The credential-bearing child API was stopped immediately afterward. This URL is therefore a tested URL, **not a currently running review server**.
- **Source:** the pre-existing healthy local Zetaris Compose stack authenticated through the supported `ui_proxy` login. Its protected Compose login and the existing Windows DPAPI NVIDIA key were passed only in the API child environment; values were never printed, committed, or sent to the browser. Real HTTP preflight succeeded. Six real pages returned `200 + 200 + 200 + 200 + 200 + 80 = 1,080` fictional observation slots. No local fallback was used.
- **Source request IDs:** `7f50a9a3-63dd-445b-b311-6bf4ad2572ed`, `d231674e-0a90-4bd6-8d3f-0ee409560fd1`, `da1471c5-4e46-4604-96c8-cd5cc2567dc4`, `eca1371c-e694-4609-b3f7-a42dc4da7d27`, `544123cb-a9f4-4fe6-994f-67b4edbde31a`, `83fef491-3af1-4faa-952d-b18049e12dc3`.
- **Authenticated query IDs:** `13221ccd-d520-4527-a1f5-28cc2472a84b`, `1a62d78a-cd3b-4c7b-b27e-bceed8592815`, `6b887f45-ddc0-4c1f-82dc-53b3b8267c80`, `f706cc6c-6335-4b6f-95d3-594f4150b3a0`, `60c40632-7e85-4b1b-a4d1-b227a5a2acd8`, `4085c65c-3dca-41e8-8990-3627a68014ff`.
- **Canonical source digest:** `fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea`. Source IDs follow the frozen `SYN-180-opportunity-4101-000-energy_central` through `SYN-180-opportunity-4101-179-energy_central` series; the full 1,080-ID set stayed in ignored local evidence and the World Model.
- **PHIS Discovery:** independently returned PASS for its 16 frozen tests: 3 qualified `candidate_signal`, 2 `unstable_candidate`, 11 `weak_candidate`. Energy coverage was 170/180 observed days. Six returned 30-day descriptive intervals had 28, 30, 27, 28, 28, and 29 observed Energy days. Scientific evidence event: `d7c36370a95ed809880e24956ac5c4adf73c6ff16c953d3ae4db820fcdd6e60e`. These are observational associations, not causes, diagnoses, or medical advice.
- **NVIDIA:** real provider response IDs `chatcmpl-53c3d375-8866-4f8a-a6a2-c91297064283` (correct `energy/discovery` plan) and `chatcmpl-11976d66-645b-4ea3-8058-e2ed6175ee51` (critic). Transport was verified. The critic was **not accepted**: `review=null`, `verification=abstain`, `reason_code=invalid_critique`. No deterministic coverage recheck was requested or executed. The original model wording is not retained, so neither a substantive rationale nor a precise failing validation rule can be asserted.
- **Meterless:** official Engine persisted seven events and a separate process read them back after the API stopped: two decisions, two agent states, one scientific evidence, one tool evidence, and one `agent_review_180d_v2`. All seven had Engine event IDs. Review event `5134571fee7944ca948e0e0cbdaa9de25fd266a08f5403fe2721e38da3c1d0cc` records the validation failure. Meterless Power/Runtime remain `NOT_CONNECTED`.

## Scientific equivalence

A separate deterministic `SYNTHETIC_LOCAL_ONLY` Energy v3 run returned PASS. Its signal objects, plan hash, family ID, temporal-policy hash, hypothesis count, canonical digest, longitudinal windows, series, findings, comparison, and coverage were **exactly equal** to the live Zetaris-backed PHIS audit. Only the truthful source mode differs. No original Discovery module, frozen generator/seed, data, plan, negative control, threshold, or scientific output was modified.

## Browser and focused checks

| Check | Result |
| --- | --- |
| Isolated API `GET /api/health` | HTTP 200; live source mode |
| One installed-Chrome authenticated Energy investigation | HTTP 200; safe `BLOCKED/invalid_critique`, one POST |
| Genuine desktop and 390 px mobile screenshots | Captured; no page error or horizontal mobile overflow |
| Retained scientific evidence dialog | 16 rows and clear non-endorsement, verified in Chrome by replay of the **captured synthetic response** with no sponsor call |
| v4 simulated critic tests | 7/7 PASS |
| Frontend contract tests | 24/24 PASS |
| API integration tests | 9/9 PASS |
| Adversarial battery | 14/14 PASS |
| Official Meterless World Model conformance | 8/8 PASS |
| Clean public HTTPS clone of PR #50 | Exact base SHA; authorized Discovery release checks 2/2 PASS |
| Bounded tracked-file secret scan | No tracked `.env`, database, DPAPI, private-key file, or matching NVIDIA/GitHub key shape |

The first sandboxed v4 test invocation failed because Windows denied temporary-directory cleanup. The same focused suite passed 7/7 with normal local filesystem access; this did not require a code change.

**Genuine screenshots:** [desktop](evidence/final-integrated-authentic-desktop.png), [390 px mobile](evidence/final-integrated-authentic-mobile.png). **Labeled response replay:** [scientific evidence dialog](evidence/final-integrated-science-audit-replay.png). The replay demonstrates the UI's retained PHIS audit and is not a second live sponsor receipt.

## Sponsor and release interpretation

| Capability | Evidence | State for this run |
| --- | --- | --- |
| Zetaris authenticated fictional source | Six HTTP pages, request/query IDs, 1,080 rows, matching digest | VERIFIED LIVE |
| PHIS Discovery | Frozen 16-test output and exact local/live equivalence | VERIFIED LOCAL on live-sourced rows |
| NVIDIA plan and critique transport | Two provider-issued response IDs | VERIFIED transport; critique **invalid**, no endorsed answer |
| Meterless World Model Engine | Seven durable events and readback after API stop | VERIFIED LOCAL |
| Meterless Power/Runtime, other optional sponsors | No run receipt | NOT_CONNECTED |

The 180-day-first page rendered actual coverage, all six intervals, a full recorded series, the failed Nemotron review, and separated PHIS science in Evidence. Adjacent 28-day comparison remains secondary in the unchanged PR #50 interface and frontend contract tests. The browser made no clinical claim and did not show an unaccepted model association as endorsed.

**Release gate:** NO-GO for a claim that the full hosted chain produced a validated scientific answer. PR #49 remains the protected fallback. PR #50's runtime can be reviewed, but this audit offers no evidence-backed prompt or validator change to justify another hosted attempt. A future fix requires retaining a safe, bounded failure category or otherwise diagnosing the actual rejected response, testing the specific correction, and then performing a separately authorized authentic check. No merge, deployment, or HackOS submission occurred.

## Reproduction and local review

For a credential-free functional review of the preserved application, from a clean checkout run:

```powershell
$env:PYTHONPATH=(Resolve-Path src).Path
$env:PHIS_DATA_MODE='SYNTHETIC_LOCAL_ONLY'
$env:PORT='4203'
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4203/` for the verified local v3 interface. Hosted v4 needs the existing private `NVIDIA_API_KEY` and the documented Zetaris channel supplied only to the API child; do not copy credentials into the checkout. The authentic run's URL was `http://127.0.0.1:4203/?analysis=v4`, and its isolated server has been stopped. The repository README already documents the supported mode and provider variables. No README or submission-deck claim was changed on the basis of this blocked run.
