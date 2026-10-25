# Scientific facts and Nemotron review — release gate, 25 October 2026

**Scope.** Draft PR #43 is based on PR #49 (`79929061570d0aa3c7e5e524f87dbbfbad6e7e51`); PR #49 and the stable release were not changed. The genuine browser run below exercised the code checkpoint `2ecf27c2d73ef69a996fbd3c2ff23ca6d667d370` in `SYNTHETIC_LOCAL_ONLY`. All observations are fictional. This change does not alter PHIS Discovery, data, thresholds, or the 28-day calculation.

## The three independent states

| State | Owner | Display and audit rule |
| --- | --- | --- |
| `scientific_qualification` | PHIS Discovery deterministic gates | A valid `PASS` retains the original 180-day observations, six longitudinal intervals, candidate/exploratory classes, statistics, source IDs and scientific event even if model review abstains or fails. A real scientific or source-provenance failure remains blocked. A qualified observational association is not a causal result or clinical advice. |
| `nemotron_review` | Hosted model, then strict local validation | `ACCEPTED`, `ABSTAINED`, `FAILED` or `NOT_ATTEMPTED`, with bounded decision, reason, cited signal, direction, lag, uncertainty, provider response ID and event ID. It critiques interpretation; it does not compute or rewrite science. Invalid citation, sign, lag or uncertainty cannot become acceptance. Abstention never becomes acceptance. |
| `sponsor_proofs` | This run's real receipts | World Model is `VERIFIED` only on durable Engine event readback. NVIDIA is `VERIFIED` on a genuine valid hosted response, including a valid abstention; a genuine but unusable review is `PARTIAL`. Simulated transport cannot verify NVIDIA. Zetaris and Meterless Runtime remain `NOT_CONNECTED` in the local run below. |

The NVIDIA Lightning API is requested with its documented JSON-object response mode. The prompt asks for the exact six-field PLAN/CRITIQUE contracts, and the existing allowlists and new citation validator reject additional text or arbitrary fields. A valid positive critique must cite one actual PHIS `candidate_signal`, preserve its effect direction and lag, identify the observational association, and state confounding and causal limits. The UI renders bounded copy from these validated fields; the model does not author numerical findings. A bounded deterministic coverage recheck remains available when the model requests it. No favorable verdict is hardcoded.

Implementation locations: [strict critique parser](../src/phis_open_agent/nightshift_agent.py#L79-L122), [orchestrator separation and Engine persistence](../src/phis_open_agent/nightshift_agent.py#L695-L822), [World Model event validator](../src/phis_open_agent/run_world_model.py), [browser contract validator](../frontend/client.mjs#L221-L279), [bounded review copy](../frontend/presentation.mjs#L179-L220), and [focused adversarial tests](../tests/test_v4_evidence_critic.py).

## Before / after decision matrix

| Scenario | PR #42 | PR #43 addendum |
| --- | --- | --- |
| PHIS passes; Nemotron accepts a supported association | Show PHIS results, but model's one-key decision had no cited rationale | Show PHIS results under PHIS attribution and a separate validated model review with signal, direction, lag, uncertainty and provider/event IDs. |
| PHIS passes; Nemotron abstains, returns invalid JSON, or inference fails | `BLOCKED` hid chart, intervals and qualified findings | PHIS remains `PASS` and visible; model panel states non-endorsement/failure. No model-approved interpretation is shown. Actual model failure/abstention is persisted. |
| PHIS source/scientific gate fails, low coverage, or clinical question | Block | Still block; the model cannot promote it. |
| Model requests verification | Recheck may run, but the second critique could still erase science | Recheck result and event ID are fed to the second critique and persisted; valid PHIS results survive a subsequent model abstention. |

## Genuine hosted acceptance and UI proof

An isolated local Python API and separate headless Chrome ran one energy investigation; no founder Chrome, Docker or Zetaris process was touched. The source was the preexisting **1,080-record fictional local fixture**, canonical digest `fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea`. Code checkpoint: `2ecf27c2d73ef69a996fbd3c2ff23ca6d667d370`. The API was stopped afterward. Browser elapsed time: **37,838 ms**; page errors: **0**.

| Receipt | Actual value |
| --- | --- |
| Run | `SYN-RUN-5714fc44d649`, `investigation.v4`, `PASS`; PHIS scientific event `45a6ee8ac5ba3544beff87297d952c4da0d37b847819d27aba0d48d35da59009` (`evt_6`). |
| Genuine NVIDIA PLAN | Model `nvidia/nemotron-3.5-lightning-30b-a3b`; provider ID `chatcmpl-d14339fd-1b02-4ee6-b255-47acdc5dd93e`. |
| Genuine NVIDIA CRITIQUE | Provider ID `chatcmpl-8d3d49de-2730-4857-bb87-2d912cdb14af`; decision `accept`, reason `qualified_observational_association`; cited PHIS signal `90ef93bc76d478a9059f1b1fefcf6486a10aeddab94aa349cbf8364ac77ab86a` (sleep-hours / energy, **positive**, same day, lag `0`), `confounding_and_no_causality`. This is an observational association, not a causal estimate. |
| Meterless World Model | Independent readback: **6** durable events, scientific event `evt_6`, final VERIFY event `041d3bfc7d201b5a6217fcce533f2a349aceb66a52911d1c7920e7524ba21c63` (`evt_12`) stores provider ID, cited signal, direction, lag, uncertainty and reason. |
| Screen and sponsor labels | [Authentic desktop screenshot](evidence/nemotron-review-hosted-desktop.png): 170 plotted days in the 180-day series, six fixed longitudinal intervals, three PHIS-qualified candidate cards, separate NVIDIA review, secondary latest 28-day comparison. `meterless_engine=VERIFIED`, `nemotron=VERIFIED`, `zetaris=NOT_CONNECTED`, `meterless_runtime=NOT_CONNECTED`. |

An earlier **direct hosted API probe** on a separate local synthetic run (`SYN-RUN-b14c98858390`) also returned a genuine valid `accept`, with PLAN `chatcmpl-ead49816-69ed-4efd-a066-a16c4e1e5051`, CRITIQUE `chatcmpl-66d70278-b72a-4969-b105-3ffd9107f279`, and durable final review event `18d034f7d13756d20e6a25cc86bfd737cad57571c10d6b2ffed9ed3f8d95acba`. It is a second receipt, not a second browser run. Neither genuine positive response requested a coverage recheck; no hosted recheck is claimed.

## Regression and limits

Focused tests use **SIMULATED provider transport** and real local Discovery/World Model code. They cover grounded accept, abstention preserving PHIS facts, post-recheck abstention, wrong citation/sign/lag/classification, negative control, low coverage, clinical request, malformed JSON, and provider outage. Separate simulated Chrome accept/abstain checks verified the visible PHIS chart (170 points), six intervals, three candidate cards, separate review copy, secondary 28-day detail and zero page errors; those screenshots are **not** hosted NVIDIA receipts. The real hosted screenshot above is the positive UI receipt.

At this checkpoint, `PYTHONPATH=src python -m unittest tests.test_v4_evidence_critic -q` passed **8/8** in 110.270 s with an allowed local temporary directory for the Engine subprocess. `node --test frontend/tests/*.test.mjs` passed **25/25** in 304 ms. The first broad Python attempt under the Windows sandbox failed on temporary-directory permission errors and was not counted as a product failure; it was stopped, then the focused v4 command above passed outside that restriction. No full scientific suite or new benchmark was run.

The original combined `LIVE_SYNTHETIC_ZETARIS` run `SYN-RUN-c13b6edef2e0` remains a valid historical Zetaris receipt on PR #42; its model abstained after a passing deterministic coverage recheck. Its hidden rationale cannot be reconstructed from the old one-key protocol. The new code was **not** tested with same-run Zetaris, so the current PR must not claim a fully combined Zetaris–NVIDIA browser receipt. The hosted positive review was structured and evidence-grounded; it did not provide a freeform explanatory essay, and it did not request an extra tool. A hosted abstention on the new code has not been induced or claimed; deterministic adversarial tests cover that branch without forcing a real provider verdict.

**Release gate:** GO for review of the narrow science/review separation and genuine hosted positive local-synthetic demonstration; NO-GO for claiming a new same-run live Zetaris proof, a model-performed coverage recheck, causal/clinical efficacy, Meterless Runtime/Nightshift, or final merge/deployment/submission. Preserve the stable release and require human review of Draft PR #43.
