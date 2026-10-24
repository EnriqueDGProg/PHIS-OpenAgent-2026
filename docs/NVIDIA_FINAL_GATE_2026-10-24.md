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

The agentic badge must not be promoted from the successful connectivity probe alone.

## P0 JSON-mode follow-up on Draft PR #34

The two earlier responses were authenticated, then rejected by `parse_plan`. Their raw content and validator subcategory were not retained, so the exact earlier shape cannot be recovered from sanitized evidence. The first exhausted its 160-token limit; the second used 205 of 512 tokens, excluding that limit as the explanation for the second rejection. Both safely recorded abstention in World Model.

NVIDIA's [Nemotron Lightning guide](https://docs.nvidia.com/nim/large-language-models/2.0.10/get-started/advanced/get-started-nemotron-3.5-lightning.html) documents `response_format: {"type":"json_object"}` with subsequent schema validation. Its [hosted evaluation example](https://docs.nvidia.com/nemo-helix/documentation/evaluate-models/metrics/agentic-metrics) uses the same format with the Lightning hosted endpoint. The Lightning-specific hosted API reference does not document a `json_schema` request form, so this update uses documented JSON mode and retains the existing exact-key and allowlist validator. Only NVIDIA plan and critique requests receive the new parameter; the plain-text connectivity probe and Meterless route do not.

| Genuine JSON-mode plan | Provider-issued response ID | Latency | Result |
| --- | --- | ---: | --- |
| Energy | `chatcmpl-415191b2-62fb-4e34-878a-66a98f97e9ad` | 2,804 ms | **BLOCKED**: `PlanRejected: Model response schema invalid`; 212 completion tokens. |
| Sleep | `chatcmpl-cbe928f7-928c-4b33-b659-451369bdac9e` | 2,320 ms | **BLOCKED**: `PlanRejected: Model response schema invalid`; 204 completion tokens. |

Both responses identified `nvidia/nemotron-3.5-lightning-30b-a3b`, but neither met the required exact `family` and `tool` shape. Raw output was neither printed nor retained; no invalid text was accepted. Per the owner's stop condition, there were no further hosted calls and no scientific v4 run or critique. The local deterministic fallback and the `nemotron: NOT_CONNECTED` agentic proof remain correct. Focused simulated inference/planner tests: **13/13 PASS**. No browser, full suite, scientific benchmark or Docker run was performed in this follow-up.

**Release gate remains NO-GO for NVIDIA agentic verification.** Connectivity is genuinely verified by the earlier probe; model-driven plan, critique and World Model evidence based on a valid hosted plan remain BLOCKED.
