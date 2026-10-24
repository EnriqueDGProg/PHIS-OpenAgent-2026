# P0 evidence critic quality gate — 24 October 2026

**Scope and base.** Draft PR #39 targets the PR #37 branch at `b79ba3fbbcc0c34b269b37c01e36ecb0b0d92309`. The five original PHIS Discovery modules, fictional generator/seed, scientific thresholds, Docker, deck and sponsor adapters were not changed. PR #37 remains available as rollback. This change addresses the [director's PR #37 audit](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/37) without claiming new scientific findings.

## What changed

- The v4 critic receives a compact `phis-critic-evidence.v1` packet copied from **actual** Discovery output: up to three qualified signals, one unstable signal and a negative control, each with original signal ID, classification, effect, N, lag, available q values, temporal state, block stability and flags. It also receives exact classification counts, existing 28-day comparison coverage, uncertainty text, source digest, source mode, query request IDs when applicable, and World Model science/tool event IDs. Provenance and numeric fields are type-checked against the persisted scientific event before any model call. Raw observations are not sent in this packet, and model text cannot become a measured value.
- A first `replan_coverage` decision is persisted with its authentic provider ID. The agent reruns the deterministic coverage tool and checks the **unchanged** PHIS requirement of at least 20 observed days in each compared 28-day window. The check, output hash, source IDs and event link are persisted. When the original Discovery result and this gate pass, at most one further critique is requested. The original scientific result is returned only on a final model `accept`; otherwise the agent returns `BLOCKED / evidence_review_required` (or a specific invalid/output outage reason), with no chart or findings. A genuinely failing Discovery `weak_coverage` result remains `INSUFFICIENT_DATA` and is never promoted by the model.
- The no-series title now reserves “Question outside scope” for `unsupported_question`; a scientific review block says “Result unavailable.” This is a status-label correction, not a UI redesign.

## Focused checks

Set `PYTHONPATH=src`; on Windows set `TEMP` and `TMP` to ignored `.local-state/tmp`.

| Check | Result |
| --- | --- |
| `python -m unittest tests.test_v4_evidence_critic tests.test_nightshift_agent tests.test_discovery_release tests.test_inference_transport_simulated -q` | **PASS 21/21**. Includes v4 Discovery PASS, high-coverage replan then accept, high-coverage final abstention, invalid second critique, model outage, clinical abstention, actual in-memory low-coverage synthetic case, World Model readback and simulated receipts remaining unverified. |
| `node --test frontend/tests/*.test.mjs` | **PASS 16/16**. |
| `python -m unittest tests.test_scientific_180d.Scientific180ContractTests.test_frozen_opportunity_case_and_exact_calendar -q` | **PASS 1/1**; frozen 180-day fictional calendar and 1,080 normalized rows unchanged. |
| Five original Discovery blobs | **UNCHANGED** in the PR diff; the byte-pinned release guard is included in the 21-test set. |

The legacy v1 adversarial battery is **not** counted as v4 validation. The simulated transport tests make no sponsor verification claim.

## One genuine hosted synthetic Chrome investigation

On implementation code SHA `c7d247614037e4badd35e3205eacddb65506db9b`, one installed-Chrome v4 investigation used the owner-held Windows DPAPI key only in a hidden child API environment. The child was stopped afterward; no key, raw provider text or private state was committed. The [actual desktop capture](evidence/evidence-critic-nvidia-v4-desktop.png) shows `SYNTHETIC · LOCAL`, NVIDIA and Meterless Engine **VERIFIED**, Zetaris and Meterless Runtime **NOT CONNECTED**, and no browser page errors.

Run `SYN-RUN-412e05dfdf03` selected `energy/discovery` with hosted plan ID `chatcmpl-fdebfa94-da12-404f-a804-100e83fa3e4a`. Discovery produced a `PASS` scientific event `baefcebce51f57817ec1feaca409fdd3dcf350e4c0d0fd8cb4ccbef4bd5d6fb2` linked to 1,080 fictional source IDs. The first hosted critique `chatcmpl-18c8bb2e-8424-4d20-affa-00f54a3e05b5` requested `replan_coverage`. The deterministic comparison gate passed (170/180 overall observed energy days; its two compared 28-day windows met the unchanged 20-day minimum), and coverage event `d405b427743ec81ce923ca911008aff82048e2db68b674b3eda11a83ff8ba684` was persisted. The **one** final hosted critique `chatcmpl-9866027c-19cd-48e7-bf33-cbc9485402d4` did not accept the finding. The typed result was **`BLOCKED / evidence_review_required`** with no chart, comparison or finding. Reopening the official World Model store after the child stopped returned eight validated, linked events, including both real critique IDs and the final abstention event `5277e7622e93a4efb9c2c7e79cfba4f24ec38a6a756b5f5715d7635717314485`.

This is authentic provider-backed planning, evidence critique, coverage recheck and safe abstention. It is **not** a positive hosted scientific answer or a combined Zetaris run. No second hosted investigation was attempted.

**GO for Draft PR review:** the false insufficient-data label is fixed, deterministic science remains authoritative, a positive PASS is reachable in the targeted v4 test, and abstention/provenance are observable in the one hosted browser run. **NO-GO for claiming a positive hosted answer or sponsor combination from this run.** Founder/director should review the bounded packet and branch before any merge or final submission.
