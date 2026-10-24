# Nemotron contract recovery — 24 October 2026

Branch: `codex/phis-nemotron-contract-20261024`, based on PR #34 `ac24af3e00711c5a52f33693b27df5091b19fb60`. This is a separate worktree. The stable release branch was neither edited nor merged.

## Root cause and correction

One authenticated, fictional 180-day PLAN request inspected only JSON field names and types. NVIDIA returned HTTP 200 with `finish_reason=stop`, model `nvidia/nemotron-3.5-lightning-30b-a3b`, ID `chatcmpl-d9297e93-2e67-4e1f-a376-463ffdce1d67`, 248 completion tokens, and a JSON object shaped `{"parameters": object, "tool": string}`. PHIS requires exactly `{"family": string, "tool": string}`. Thus the observed failure was a **PLAN contract mismatch**; neither token exhaustion nor credits were established as its cause. No raw generated text, secret, prompt or source record was printed or retained.

The NVIDIA-only system prompts now demand the exact PLAN keys and values, or the distinct one-key CRITIQUE contract, with short valid examples and explicit rejection of `parameters`, nesting, extra keys and prose. NVIDIA's documented `response_format: {"type":"json_object"}` and `enable_thinking: false` remain in place. PHIS's duplicate-key, exact-key, allowlist and abstention validators remain unchanged. The Meterless/Nightshift prompt and the deterministic fallback remain unchanged. Sources: [NVIDIA Lightning JSON-mode guide](https://docs.nvidia.com/nim/large-language-models/2.0.10/get-started/advanced/get-started-nemotron-3.5-lightning.html), [hosted Lightning API reference](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-5-lightning-30b-a3b-infer).

## Genuine hosted receipts — five calls total

| Call | Result | Provider response ID | Latency |
| --- | --- | --- | ---: |
| 1. Diagnostic PLAN shape only | Old shape `parameters: object`, `tool: string`; rejected | `chatcmpl-d9297e93-2e67-4e1f-a376-463ffdce1d67` | 3,918 ms |
| 2. Energy PLAN after contract fix | `energy` / `discovery`, strict validator PASS | `chatcmpl-6fd512f9-cc54-4564-8359-cd786dcf72ce` | 561 ms |
| 3. Sleep PLAN after contract fix | `sleep` / `discovery`, strict validator PASS | `chatcmpl-24110c1b-58e9-45b5-b58b-dd086b35caa9` | 521 ms |
| 4. v4 energy PLAN | `energy` / `discovery`, strict validator PASS | `chatcmpl-f2bb11bd-fa90-49a7-839a-b195c8806a9e` | Included in 20,832 ms v4 run |
| 5. v4 evidence CRITIQUE | `accept`, strict validator PASS | `chatcmpl-424b1863-d517-4b27-a3e5-9aa115e07699` | Included in 20,832 ms v4 run |

Every receipt returned the actual model `nvidia/nemotron-3.5-lightning-30b-a3b`. No paid endpoint or additional hosted calls were used.

## Complete v4 evidence path

Run `SYN-RUN-12a0a336e5cf` in `SYNTHETIC_LOCAL_ONLY` returned `PASS`, `NVIDIA_VERIFIED`, `energy/discovery` and `accept`. PHIS Discovery created a `PASS` scientific event `0f7eb1a1c71f0fb87bbe67b7dce71e04d9c41c8a5b7ff914e87844381dffdccb` with 1,080 distinct synthetic source records. The World Model persisted tool evidence event `42d19a960a1b4e1c160436484e77966a0e9b4aa0cc1388de09eaf980ea9371a0`, linked to that scientific event. Reopening the Engine store confirmed the VERIFY event `8600644a2f475e5f07d3e487de1fede90ee5a0a4d42d79bf16a401284a4d02c5` links to the tool event, retains the provider critique ID, and shares the source digest. The run returned `nemotron: VERIFIED` and `meterless_engine: VERIFIED`; `zetaris` and `meterless_runtime` remained `NOT_CONNECTED`. Direct Nemotron does not establish Meterless Power or Nightshift.

## Test and release boundary

Focused simulated inference/planner tests: `python -m unittest tests.test_inference_transport_simulated tests.test_nightshift_agent -q` — **13/13 PASS** in this worktree. The negative test rejects the observed `tool`/`parameters` shape. Simulations are not counted as sponsor proof. No full suite, benchmark, Docker or browser run was performed for this recovery. This is one successful local synthetic v4 run, not a Zetaris-backed live-source or frontend validation.

The shared NVIDIA Build browser tab was reported to expose the key in its snippet. The owner should revoke that key and replace the local DPAPI-protected copy after reviewing this bounded proof. No key material is present in this branch.
