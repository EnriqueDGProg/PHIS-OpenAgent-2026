# NVIDIA final integration gate — 24 October 2026

Base: Draft PR #33, `fb806023a5fb7d84cba05e299b2384acfbb02250`. This branch changes only the documented hosted-model selection, Lightning direct-answer setting and bounded NVIDIA response length. No science, dataset, Zetaris, Docker, frontend design or private PHIS source changed.

## Authentic provider evidence

The owner stored a free NVIDIA Build key in a Windows DPAPI-protected file outside Git. It was decrypted only into the probe process environment and never printed, committed or sent to the browser. All provider prompts used fictional synthetic context.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Initial Lightning probe | BLOCKED: HTTP 200 response contained no final plain-text answer with the prior 128-token setting | 2,134 ms; no PASS claimed. NVIDIA documents `chat_template_kwargs.enable_thinking=false` for a direct answer. |
| Corrected Lightning probe | **PASS, genuine hosted response** | Model and returned model `nvidia/nemotron-3.5-lightning-30b-a3b`; provider ID `chatcmpl-a6608296-36b2-4895-a4c4-fb1735d5acd3`; 1,056 ms. This verifies connectivity and inference only. |
| v4 investigation attempt 1 | **BLOCKED**: model output did not pass the strict plan JSON schema; safe abstention, no scientific claim | Provider planning ID `chatcmpl-05a25f82-63c8-4288-bcd7-ddba35c299a4`; 160 completion tokens (the then-current limit); 5,346 ms overall; run `SYN-RUN-1d5bdbfc1747`; World Model event IDs `evt_2`, `evt_4`, `evt_6`. |
| v4 investigation attempt 2 | **BLOCKED**: strict plan JSON still rejected after raising the NVIDIA-only maximum to 512; safe abstention, no scientific claim | Provider planning ID `chatcmpl-c9dbe999-a42a-4ea8-9961-1903ab885113`; 205 completion tokens; 4,677 ms overall; run `SYN-RUN-cc11b4da1112`; World Model event IDs `evt_8`, `evt_10`, `evt_12`. |

The second failure is not a token-length failure. Further hosted probes stopped under the owner's repeated-failure limit. Neither attempt ran Discovery or evidence critique, and neither verifies the Nemotron agentic sponsor badge. The two distinct model-driven investigations requested for acceptance remain **BLOCKED**. The official [NVIDIA model page](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b) marks this as a free endpoint; the [API reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-5-lightning-30b-a3b-infer) defines the hosted route and token range. No paid endpoint was activated.

## Local product acceptance

Targeted simulated tests: `python -m unittest tests.test_inference_transport_simulated tests.test_nightshift_agent -q` **13/13 PASS** with `TEMP` and `TMP` set to ignored `.local-state/tmp`. These injected transports are not hosted inference proof. Frontend contract tests: `node --test frontend/tests/*.test.mjs` **16/16 PASS**.

One real installed-Chrome session exercised the local Python HTTP API at `http://127.0.0.1:4173/?analysis=v4`, with no NVIDIA key in that server process. Energy investigation `SYN-RUN-ab796a0980b4` returned 180 synthetic days, 1,080 source records in its Discovery evidence, 3 qualified signals and Engine events `evt_2` through `evt_12`. The follow-up `SYN-RUN-88fca403b063` recovered the parent decision, investigated sleep, returned 2 qualified signals, and recorded Engine events `evt_14` through `evt_24`. Chrome visibly labeled `SYNTHETIC · LOCAL`, `Meterless Engine: VERIFIED`, `NVIDIA Nemotron: NOT CONNECTED`, `Zetaris: NOT CONNECTED`, and `Meterless Runtime: NOT CONNECTED`. The screenshot was captured in the browser QA transcript; it is not a hosted NVIDIA screenshot. No additional browser run was made.

## Release gate

| Requirement | Status |
| --- | --- |
| Official free Lightning model and minimal adapter | **PASS** |
| Authenticated hosted Nemotron inference receipt | **PASS (connectivity only)** |
| Strict model plan accepted in v4 | **FAIL / BLOCKED** |
| Two distinct model-driven investigations and evidence critique | **BLOCKED** |
| PHIS Discovery and World Model local product path | **PASS (local, deterministic)** |
| NVIDIA agentic sponsor badge | **NOT CONNECTED** |
| Meterless Power/Runtime and Zetaris proof in this run | **NOT CONNECTED** |

Next technical gate: inspect the rejected synthetic-only plan response locally without retaining or publishing raw provider text, then make one schema-constrained adapter correction and seek approval before further hosted calls. Do not promote the badge from the successful connectivity probe alone.
