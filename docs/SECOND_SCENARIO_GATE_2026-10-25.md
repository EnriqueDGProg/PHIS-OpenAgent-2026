# Second 180-day fictional scenario — first-gate decision

Date: 2026-10-25. Review base: PR #46 head f08c6f5f36a97e97d61eb6d53805e59167d8f601, stacked on PR #42 head b6e3d48f66ba99b22aff91359771316208d52727.

**Decision: NO-GO for implementation under the requested isolation boundary.** The current v3/v4 route is a strict, single-dataset protocol. A second case cannot reach unchanged PHIS Discovery and Meterless evidence while using separate dataset, participant and source IDs. It would require changing the source contract and the adapter or duplicating and rewiring that stack. This is the user's first-gate stop condition. This branch records the gate only; it contains no second generator, dataset, selector, statistical run, or sponsor claim.

## Evidence from the exact base

| Boundary | Existing guard | Consequence for a second ID |
| --- | --- | --- |
| Observation schema | src/phis_open_agent/scenario_contract_180d.py fixes DATASET_ID, PARTICIPANT_ID and expected_id; normalize_observations rejects any other identity and requires exactly 1,080 slots. | A distinct fictional participant or source namespace fails before analysis. |
| Discovery adapter | src/phis_open_agent/discovery_adapter_180d.py compares the frozen plan's dataset ID to the single constant and checks fixed plan SHA-256 values. | A new dataset needs a new plan or adapter route; changing the frozen plan would violate the request. |
| Zetaris source | src/phis_open_agent/zetaris_180d.py filters SQL to the fixed dataset and participant, then validates rows with the same single-dataset contract. | A separate dataset cannot produce a verified Zetaris readback through this route. |
| Agentic v4 | src/phis_open_agent/nightshift_agent.py generates opportunity/4101 locally, reads the single Zetaris route in live mode, and returns the same dataset and scenario. | A UI-only selector would mislabel or still run the original case. |
| Meterless lineage | src/phis_open_agent/run_world_model.py requires all 1,080 science source IDs to start with SYN-180-opportunity-4101-. | An isolated new source namespace is rejected by persisted science evidence validation. |
| API and UI | src/phis_open_agent/api.py accepts only opportunity for v3/v4. frontend/client.mjs defaults to it; frontend/index.html describes one fixed fictional record. | An explicit honest selector needs API and presentation changes, plus all upstream identity changes. |

The original offline benchmark in src/phis_open_agent/stochastic_benchmark.py has other synthetic cases, but the live investigation is wired to the one frozen opportunity/4101 case. Those benchmark cases do not constitute an isolated second product scenario.

## Scope and evidence boundaries

The requested mechanism would have to be recorded before generation or evaluation: six existing variables, explicit missingness, shared time-dependent stress/sleep/activity patterns, confounding, and an independent unrelated negative control. No coefficients, seed, acceptance target, or statistical outcome for a new case were selected here. No new case was evaluated or tuned for significance.

The official event page still lists the Oct 22–27, 2026 build window and Oct 27 23:45 UTC submission deadline: https://hackathon.genai.works/event/open-agent-hackathon-2026 . The existing PR #46 source and scientific data remain byte-for-byte unchanged by this documentation-only branch. No original PHIS Discovery modules, thresholds, plans, sponsor receipts, or submission materials changed.

Existing PR #46 local captures show the original scenario only: [desktop energy](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/f08c6f5f36a97e97d61eb6d53805e59167d8f601/docs/evidence/issue44-energy-desktop.png), [mobile energy](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/f08c6f5f36a97e97d61eb6d53805e59167d8f601/docs/evidence/issue44-energy-mobile.png), [desktop evidence](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/f08c6f5f36a97e97d61eb6d53805e59167d8f601/docs/evidence/issue44-evidence-desktop.png), and [mobile evidence](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/blob/f08c6f5f36a97e97d61eb6d53805e59167d8f601/docs/evidence/issue44-evidence-mobile.png). No second-scenario screenshots exist because implementation stopped before UI changes.

**GO:** review this first-gate finding and, if desired, separately scope a versioned multi-dataset source/adapter protocol with sponsor and memory compatibility tests before preregistering a new mechanism. **NO-GO:** implementing or presenting a second scenario under the current single-dataset contract, or claiming new scientific/sponsor results. No merge, deployment, or submission.
