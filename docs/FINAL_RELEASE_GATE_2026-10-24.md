# Final release candidate gate — 24 October 2026

**Draft PR:** [#37](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/37), branch `codex/phis-final-release-20261024`, target `main`. This release starts at the exact PR #35 commit `815ac9ef426cd632732f7b7f22a3a200a025e3c5` and adds the completed PR #36 `submission/**` tree from `2c2833e08308913e917ca51ee6f605255c579ee8` without rebuilding the deck. The PR diff against `main` contains the whole application, five Discovery modules, frontend, tests, scripts, licenses and submission package. It has not been merged or deployed.

## Current clean public clone

A fresh HTTPS clone of this public Draft PR branch was made without the private PHIS checkout, Python/npm installation or credentials. The code tree tested was checkpoint `d96e5bc90da5fd7a4c1453594de7e2ef12debd41`; later edits in this PR are documentation and the genuine local screenshot only. The exact final review SHA is in the PR head and should be used for recording. Python 3.12 and Node 24 were present on the host.

| Check | Result | Evidence |
| --- | --- | --- |
| Public clone, standalone imports and authorized Discovery | **PASS** | Five exact Git blobs and no sixth scientific file: `python -m unittest tests.test_discovery_release -q` within the 31-test focused set. `src/phis_master/NOTICE.md` scopes their owner-authorized MIT release; `vendor/meterless-world-model/LICENSE` retains Apache-2.0. |
| Focused Python inference, planner, release, API and Engine | **PASS 31/31** | `python -m unittest tests.test_inference_transport_simulated tests.test_nightshift_agent tests.test_discovery_release tests.test_integration_api tests.test_meterless_engine -q`, with `PYTHONPATH=src` and `TEMP`/`TMP` set to ignored `.local-state/tmp` on Windows. Simulated provider tests are contract checks, not sponsor receipts. |
| Frontend contract tests | **PASS 16/16** | `node --test frontend/tests/*.test.mjs`. |
| World Model conformance | **PASS 8/8** | `WORLD_MODEL_IMPL=vendor/meterless-world-model/src/index.ts node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts`. |
| Adversarial battery | **PASS 14/14** | `python -m unittest tests.evaluation.test_adversarial_battery -q`, with the same Python/temp environment. |
| Secret/private-file review | **PASS for tracked files** | No tracked `.env`, private key, SQLite/database or certificate named file. Tracked-text scan for common private-key, cloud-key and NVIDIA/OpenAI token patterns returned zero file hits. This is a bounded scan, not a guarantee about GitHub/account state. |
| Editable submission deck | **PASS existing package** | Unchanged PR #36 ten-slide PPTX and source/citation ledger. Its existing [QA](../submission/DECK_QA.md) labels PR #33 Zetaris screenshots and PR #35 NVIDIA receipts as separate prior runs. |

## Real browser and persistence proof on the clean clone

One installed Google Chrome desktop investigation at 1440 × 900 used native localhost HTTP and `/?analysis=v4`. Run `SYN-RUN-069d71512a43` returned `investigation.v4`, `PASS`, family `energy`, 180 fictional days, the scientific chart and source-linked findings. The browser had zero page errors. The [actual full-page capture](evidence/final-rc-local-v4-desktop.png) visibly labels `SYNTHETIC · LOCAL`; proof badges show **Meterless Engine VERIFIED**, **Zetaris NOT CONNECTED**, **NVIDIA Nemotron NOT CONNECTED** and **Meterless Runtime NOT CONNECTED**. Engine proof event: `baf7434050658fdcb63c99137c1f5c57448405f2bcb513ed6d9e92ddaf0610a0`.

The API process was stopped and restarted with the same ignored local Engine state. A subsequent readback-backed follow-up, run `SYN-RUN-a4262a3a0509`, used parent `SYN-RUN-069d71512a43`, returned `PASS`, selected `sleep`, and verified the Engine again. Reopening the official Engine store returned six validated events for each run. State files and complete responses were kept out of Git. This proves persisted local follow-up behavior on this branch; it is **not** NVIDIA or Zetaris sponsor proof.

## Authentic sponsor evidence, with execution boundaries

| Capability | Verified state | Trace boundary |
| --- | --- | --- |
| PHIS Discovery | **VERIFIED in current clean clone and Chrome** | Five byte-pinned pre-existing modules executed on fictional data. Qualified associations remain observational. |
| Meterless World Model Agent Engine | **VERIFIED in current clean clone and restart** | Parent Engine event above; readback changed the follow-up to sleep. This is Engine use, not Power/Runtime. |
| NVIDIA Nemotron direct hosted | **VERIFIED in earlier PR #35 local synthetic run, not current Chrome** | [Contract recovery](NEMOTRON_CONTRACT_RECOVERY_2026-10-24.md): energy plan `chatcmpl-6fd512f9-cc54-4564-8359-cd786dcf72ce`, sleep plan `chatcmpl-24110c1b-58e9-45b5-b58b-dd086b35caa9`, critique `chatcmpl-424b1863-d517-4b27-a3e5-9aa115e07699`; v4 run `SYN-RUN-12a0a336e5cf`. PR #35's earlier failed JSON plans were repaired by the later contract recovery; the older [failed gate](NVIDIA_FINAL_GATE_2026-10-24.md) is historical, not the final PR #35 state. |
| Zetaris authenticated local query | **VERIFIED in earlier PR #33, not current Chrome** | [PR #33 gate](JUDGE_RELEASE_GATE_2026-10-24.md): six real query pages covering 1,080 fictional variable-day records, with source and request IDs. This task's local Zetaris port `127.0.0.1:3000` was unavailable; credentials were absent. |
| Same-SHA NVIDIA-enabled Chrome | **PENDING** | `NVIDIA_API_KEY` was absent from this task process at first gate. A key is being activated separately by the owner. No provider badge or receipt is claimed for the current screenshot. |
| Same-SHA combined Zetaris + NVIDIA + Discovery + Engine | **BLOCKED by local Zetaris availability/auth** | No combined request was attempted; earlier separate receipts must not be composed into one run. |
| Meterless Power/Runtime and other sponsor services | **NOT CONNECTED** | No claim is inferred from Engine or NVIDIA direct use. |

## Reproduce and record

From a fresh clone, check out `codex/phis-final-release-20261024`. In PowerShell set `$env:PYTHONPATH=(Resolve-Path src).Path`, then run `python -m phis_open_agent.api` and open `http://127.0.0.1:4173/?analysis=v4`. The default data mode is `SYNTHETIC_LOCAL_ONLY`. Ask the energy question, open evidence and source IDs, inspect the trace and sponsor badges, restart the API with its ignored state intact, then use **What's next?** for the sleep follow-up. The [180-second script](../submission/DEMO_SCRIPT_AND_STORYBOARD.md) marks any cut to the separately verified NVIDIA receipt; the [form draft](../submission/HACKOS_FORM_DRAFT.md) and [deck](../submission/deck/PHIS_Open_Agent_2026_Track02_Review.pptx) carry the same boundary. If the owner provides a key to the API process, `PHIS_INFERENCE_PROVIDER=nvidia_direct` enables a new hosted v4 run; only a returned provider ID and verified badge can support a new same-SHA claim. Live Zetaris requires the already authorized local service and private environment variables documented in the README. Never show a key, provider console or protected local file in the recording.

**Review gate:** GO for Draft PR review and a reproducible local synthetic demo. NO-GO for claiming a same-SHA hosted NVIDIA Chrome run or combined sponsor run until separately executed and recorded. NO-GO for HackOS submission until founder/director review, real video, public default-branch access, link playback and explicit final approval. The owner should rotate the previously exposed NVIDIA Build key noted in the PR #35 recovery report before using it for final footage.
