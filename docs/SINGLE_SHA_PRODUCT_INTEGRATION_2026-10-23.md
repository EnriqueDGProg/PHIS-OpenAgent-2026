# Single-SHA product integration gate — 2026-10-23

**Scope:** Issue #28. This Draft PR is an independent integration branch based on PR #30 (`5e0d50a`) and incorporates the bounded planner interface from PR #29 (`59ae96f`) and the premium UI from PR #23 (`cf9e442`). The v3 scientific plan and fictional 180-day case remain from PR #24. PR #13 and PR #22 are untouched. No private Discovery source, credential, raw health data, merge, deployment or paid service is in this PR.

## Decision

**PASS for an owner-machine synthetic technical demo; BLOCKED for a distributable judge release.** The local authorized environment has the unpublished PHIS Discovery v1.1 package. PR #22 still blocks redistribution of its five private files until the owner completes the rights/IP/license gate. Nightshift Web has no verified callable integration, so the v4 planner is clearly labeled **local deterministic mode** unless a provider response can be verified. Meterless Runtime and NVIDIA remain `NOT_CONNECTED` in the demonstrated runs. The product must not claim live Nightshift.

## Reconciliation and provenance

| Surface | Chosen implementation | Integration change |
| --- | --- | --- |
| Real synthetic source | PR #30 authenticated Zetaris UI proxy | A single six-page, 1,080-ID verified readback is handed to v4 Discovery without a second query. No fixture fallback in live mode. Client-sent `queryId` values are not described as server-confirmed. |
| Scientific analysis | PR #24 / PR #30 v3 | Frozen 16-child family, authentic local Discovery v1.1, temporal/correction gates, canonical digest and all source IDs retained. No plan/threshold/data tuning. |
| Follow-up memory | PR #30 official World Model bridge | Scientific event is persisted and read on a fresh run. Live parent requires the same verified digest/mode. |
| Planner | PR #29 v4 bounded plan/critique interface | Live and offline source paths use the same bounded tools; provider outage uses a labeled local deterministic plan. Local verification is displayed as local, not as a blocked scientific result or a Nightshift call. |
| UI | PR #23 files | Default request is v3 180-day science; `?analysis=v4` exposes planner mode. Source labels derive from mode **and** actual Zetaris proof, never window duration. Failure clears prior figures. PHIS wordmark dot removed, hidden controls and dialog tabs repaired. |

The UI's optional `?analysis=v1&scenario=normal` route preserves the PR #13 emergency descriptive fallback for environments without the private Discovery package. That route is not a substitute for the 180-day scientific demonstration.

## Actual test evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Python regression | **PASS 87/87** | `python -m unittest discover -s tests -p 'test_*.py' -q` with `PYTHONPATH` containing this checkout's `src` and the owner-approved unpublished Discovery `src`; 198.889 s. |
| Planner reconciliation | **PASS 6/6** | `python -m unittest discover -s tests -p test_nightshift_agent.py -q` with the same private local path; includes live-source failure, injection/schema rejection, local outage label, and persistent follow-up. |
| Frontend | **PASS 16/16** | `node --test frontend/tests/*.test.mjs`; production presentation functions now tested directly, including 180-day live versus offline provenance. |
| Authenticated v3 HTTP / Engine restart | **PASS** | `python scripts/scientific_180d_live_proof.py --state <new external state> --out <new external proof>` with protected local `ZETARIS_*` process variables. Six HTTP pages `[200,200,200,200,200,80]`, 1,080 unique synthetic IDs, digest `fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea`; parent `SYN-RUN-934db00a7216` and follow-up `SYN-RUN-0f584731fc85`, selected family sleep. External proof SHA-256 `c908b083dafb37aecf0f80da5f2fe12894670582b99324d5e74343df794a455d`. Full proof and World Model state stayed outside Git. |
| Authenticated v4 Chrome | **PASS** | Real Chrome on isolated localhost HTTP server `?analysis=v4`: source VERIFIED; six distinct 200/200/200/200/200/80 queries; 1,080 IDs; authentic Discovery 16-child family; Engine event `8b3e59c0bb1e55e8d9b40ecba61031ca04d270fedb58492f48a614fc44e3f677` for run `SYN-RUN-eec680cd855a`. Planner displayed `local.deterministic_planner`; Runtime `NOT_CONNECTED`; no console errors. |
| Live v4 follow-up | **PASS** | Chrome follow-up `SYN-RUN-143682f11849` read the persisted energy event, selected sleep, queried a fresh six-page source with different request IDs, and persisted another 1,080-ID scientific event `afced535f38cf3644909fed288acf2909e6b995a5e16e4fb5da49403a88a9059`. |
| Source failure / abstention | **PASS** | Separate no-credential live-mode Chrome server returned `source_error`, Zetaris `FAILED`, no chart, comparison or finding, Engine/Runtime `NOT_CONNECTED`, no console errors. A clinical-diagnosis question on verified live source returned responsible abstention and cleared prior scientific figures. |
| Mobile layout | **PASS** | Real Chrome 390×844 viewport: `innerWidth=390`, `documentElement.scrollWidth=375`; screenshot and no horizontal overflow. Desktop Chrome had no console errors. |

No private module contents or protected `.env` values were printed, committed, or placed in browser URLs. Zetaris used the existing local no-fee stack and fictional table; no cloud compute was provisioned.

The authenticated HTTP and Chrome receipts above were collected on **2026-10-23** from this integration worktree before commit. Docker was unavailable on 2026-10-24, so no fresh live replay was attempted that day. The report does not claim a live verification of the committed SHA. Saved real Chrome screenshots: [desktop](evidence/single-sha-final-desktop.jpg), [mobile top](evidence/single-sha-final-mobile-top.jpg), and [mobile results](evidence/single-sha-final-mobile-result.jpg).

## Scientific and product limits

The energy run's observed latest-period difference was **+0.347 score/10**. Three candidate associations were presented: same-day sleep hours (`r=+0.560`, `N=159`), prior-day stress (`r=-0.517`, `N=163`), and same-day stress (`r=-0.439`, `N=164`). These are pairwise observational results under the preregistered gates, not adjusted effects, causal explanations, or medical guidance. The negative control was not promoted. Every tested child remains visible in the evidence table with effect, N, CI, p, BY-adjusted q, temporal state and classification.

## Owner gate and next sequence

1. Review this Draft PR as the single integration SHA and reproduce the external live proof with the approved local package and protected credentials.
2. Resolve PR #22 rights/IP/license gate before any private Discovery redistribution or public judge deployment.
3. Obtain a documented callable Nightshift route and a real request/response receipt before changing planner or Runtime sponsor status from local/NOT_CONNECTED.
4. Only then perform final clean-environment judge rehearsal and reviewed merge/submission. PR #13 remains the fallback.
