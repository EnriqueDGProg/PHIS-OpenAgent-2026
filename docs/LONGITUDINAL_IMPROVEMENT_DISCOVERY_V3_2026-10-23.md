# PHIS Open Agent — Longitudinal Improvement Discovery v3
**Founder-approved direction proposal, 2026-10-23. Specification only; no claim of implementation.**

**Key objective:** Help a person understand *how their wellbeing is evolving*, what modifiable factors plausibly relate to worse or better energy/sleep, how much evidence supports each explanation, and what to observe next to improve their **long-term trajectory**. Do not optimize solely for a dramatic last-28-day drop or today's isolated value.

**Sources:** protected functional RC PR #13; product direction PR #14; Discovery local extraction audits PRs #15–16; scenario PR #17; integrated scientific adapter PR #18; controlled but non-promoting scenario PR #19. Scientific baseline: private PHIS Discovery v1.1, commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. This document authorizes neither private-code publication nor alteration of the original PHIS scientific policy.

## 1. Diagnosis from actual experiments

- Original fictional 84-day PR #17 scenario returned **two energy `candidate_signal`** results, but almost no middle-to-final period energy decline and an unusually strong same-day sleep-energy correlation (+0.869).
- Revision 2 (PR #18) showed a credible recent decline (energy -0.739 vs prior 28 days), but zero promoted candidates because temporal incompatibility, sensitivity to 14-day blocks and corrected parent-family q excluded strong raw correlations.
- Registered v3 (PR #19) showed a smaller decline (-0.292), stronger/stable sleep-energy relation in all three blocks (r +0.872), but the energy time trend triggered a temporal `caution` flag and **the engine's exact v1.1 `candidate_signal` policy rejects ANY relevant flag**. It was correctly labeled `unstable_candidate`.
- **Core mismatch:** a trend-focused personal improvement question is being answered by a stringent stationary-association *promotion* gate. Discovering exploratory opportunities for subsequent testing is not equivalent to confirming a statistically qualified stationary association. No scientific finding should be invented to resolve that mismatch.
- **Longer history may help; length alone is not a fix.** Temporal trend, serial correlation, confounding and model assumptions must remain explicit. A single person with 180 daily observations does not have 180 independent samples.

## 2. Two complementary investigation lenses

**Lens A — Longitudinal state and trajectory (always provide when data support it):**
- Compare recent 28 days against a user-appropriate longer baseline (e.g. prior 56/84 days), and depict six-month history, within-person variability, sustained deterioration/improvement and observation completeness.
- Emphasize trajectory, variability, recovery and improvement headroom rather than a point estimate for today or an artificially dramatic change.
- Detect phase changes/regime shifts descriptively, clearly separated from scientific identification of contributors.
- A healthy high baseline may yield little improvement headroom; present maintenance and personalized monitoring, not manufactured risk or a forced cause.

**Lens B — Potential improvement drivers:**
- Search predeclared energy/sleep exposures and valid calendar lags over a longer representative history, with legitimate temporal diagnostics, sensitivity tests, null controls and (if approved) methods that model or account for trends.
- Surface *ranked investigable hypotheses* with full provenance and evidence tier. Distinguish robust relationships, promising-but-unstable exploratory patterns, and unsupported or insufficient evidence.
- A factor may be a candidate for low-risk tracking even if it does not meet strict Discovery promotion; it must **never** be described as a qualified signal, likely cause, adjusted effect, or numerical confidence that the engine did not support.
- Recommendations should focus on *what to observe or discuss next*, plus optional generally safe habit reflection; do not diagnose or prescribe. Never issue personalized treatment modifications.

**Judge/user question:** “How has my energy evolved, what tends to be different on my worse days, and what could I investigate or change to improve it?” Sleep is the other fully supported investigation family. Follow-up asks what can sharpen or challenge the hypotheses.

## 3. Evidence interpretation policy — new product layer, not a hidden modification to PHIS

Preserve unmodified original `discovery_v11.search_v11` outputs, IDs, original `candidate_signal`/ `unstable_candidate`/ `weak_candidate` classifications, frozen thresholds and full hypothesis corrections. Introduce a separately versioned **Exploratory Guidance Policy** in new hackathon code that consumes the actual evidence packages:

- **Tier 1 — Supported exploratory signal.** Original engine `candidate_signal`, with statistical details, temporal compatibility and limitations. Explain as a robust *within-person observational association*, not confirmed causality.
- **Tier 2 — Investigate further.** Original engine `unstable_candidate` or selected measurable association only if a *predeclared* minimum-data/effect/evidence gate is met and every blocking reason is displayed prominently. Use language “possible contributor worth checking”; never represent as qualified. Split instability due to trend, multiplicity failure, inconsistent block lengths, reverse direction or confounding. Not all `unstable_candidate` merits mention: data sufficiency, interpretable effect, temporal order where appropriate and low-risk testability must all be checked. Strong raw r alone is insufficient.
- **Tier 3 — No support / insufficient evidence.** Unpromoted weak, negative control, unavailable or too sparse. Do not rank null findings as drivers; suggest targeted missing observations or acknowledge limited improvement headroom.

An honest empty Tier 1 is acceptable; the answer should still provide verified trajectory plus appropriately bounded Tier 2 or explain how to gather better evidence. Do not reward the system for simply filling Tier 2. Verify false-positive behavior against null simulations.

**Future methods** (separately predeclared, implemented, tested and named): within-person dynamic regression, trend-aware residual analysis, change-point analysis, repeated lag models and multivariable confounder review. Do not relabel v1.1 pairwise correlations as adjusted/causal. Do not quietly lower statistical thresholds or ignore temporal warnings. Original private PHIS behavior must remain intact absent a separate scientific governance decision.

## 4. Credible stochastic synthetic benchmark — proposed 180 days

Prefer **180 consecutive days** (six months) for the flagship scenario as an engineering hypothesis to test, not an established optimal duration. Keep six initially typed daily fields unless evidence motivates a seventh; 180 × 6 = **1,080 date-variable slots**, with nullable values, source IDs, valid units, timestamp semantics and bounded paginated Zetaris transport. Update the current v2-specific 504-slot schema, planner, pagination limits, benchmarks, and source lineage explicitly; never present mock reads as live.

Generate **structured stochastic data** for one fictional person:
- A stable personal baseline and realistic bounded day-to-day variability.
- Stochastic stress, sleep, caffeine, exercise and subjective energy, with weekly cadence, serial dependence, time-lagged pathways, partial compensation/recovery and nonconstant exposures.
- Known generator-only mechanisms (direct, mediated/confounded, irrelevant) and independent negative controls; no omniscient answer labels available to runtime/LLM.
- Realistic missed logging, wearable gaps, optional measurement noise, and correct overnight sleep/caffeine alignment; zero ≠ missing.
- Episodes of higher workload, calmer weekends, behavioral changes and recovery that arise plausibly rather than deterministic step changes forcing a perfect rank correlation. Avoid generating direct energy declines without plausible exposures.
- Per-variable distribution and calendar screenshots/data dictionary for judges. Public generator, code version, random seed, cohort parameters and change log should be inspectable.

**Crucial testing design:** do not optimize one favorite seed until a target result passes. Predeclare generator parameter ranges and outcome goals **before** evaluation; use fixed *development* seeds to calibrate statistical utility and separately frozen *held-out* seeds for independent reporting. Report the detection rate of injected mechanisms and false-positive rate for unrelated factors across all held-out seeds, not just the prettiest one. If no seed supports a qualified association, report that and let product-level Tier 2 function transparently; do not secretly cherry-pick.

Design **three synthetic archetypes** as validation, with one main demo record and two tests:
1. **Improvement opportunity:** real but nontrivial modifiable influences, identifiable with appropriate historical data.
2. **High-baseline / low headroom:** adequate sleep/energy, no invented diagnosis, maintenance focus.
3. **Null/confounded:** misleading correlations or insufficient data; abstention/uncertain claims rather than invented causes.

Initial demonstration should show an identifiable opportunity when supported, plus at least one competing/unstable hypothesis and one irrelevant control. The scenario itself is deliberately designed to contain a possible improvement mechanism; this is transparent *benchmark construction*, not data falsification.

## 5. What results should be displayed

Primary result hierarchy:
1. **Your trajectory:** recent vs personal baseline, observed mean, variability, N and no arbitrary healthy threshold.
2. **Potential contributors to investigate:** evidence-ranked, reasoned explanations drawn from real deterministic packages. Visible difference between supported pattern, exploratory opportunity and unsupported candidate.
3. **What argues against these ideas:** temporal caution, trend, competing causes, confounding, unstable resampling, missingness.
4. **Improvement next steps:** safe self-observation, preference-sensitive habit reflections, follow-up questions; no diagnosis/prescriptions, no fictitious proof that intervention will work.
5. **Check again:** show how a future additional data point or newly logged behavior can update evidence, distinguishing built follow-up from *roadmap* automated/24-7 ingestion.

Do not claim PHIS has automatically connected Apple Health, a wearable, user-entered context or continuous background ingestion unless genuinely implemented. Describe future consented sources and continuous re-evaluation as roadmap.

## 6. Judge-facing transparency and differentiated value

Publish an English **Synthetic Case and Benchmark Methodology**:
- Why simulated non-random *structure* and random *daily realizations* are needed: pure independent noise cannot yield a meaningful personalized improvement problem.
- Explicit data dictionary, population/individual assumptions, source identity, generator seed, parameter registration, plausible bounds, missingness, autocorrelation, distributions, latent confounders, mechanisms and null controls.
- Complete results across independent seeds, unsuccessful scenarios and changed-data tests, not only winner statistics.
- Split designed mechanisms vs *observed outputs* vs *statistical discoveries*. The source generator is not used by the runtime scientific analyzer.
- Explain that synthetic results are a technical feasibility proof, not clinical effectiveness or guaranteed transfer to real patient data.

Document **PHIS vs a prompted LLM** factually: an ordinary tool-enabled LLM can analyze a supplied spreadsheet, but PHIS offers purpose-built ingestion/normalization, fixed scientific plans, statistical/temporal robustness, reproducible evidence lineage, persistent World Model context, longitudinal re-analysis and auditable source/tool failures. Report only implemented and tested capabilities as current; Apple Health, automated ingestion, 24/7 proactive work and N-of-1 self-experiment coaching are roadmap unless actually demonstrated.

## 7. Engineering priority and acceptance criteria

**P0:** Preserve PR #13 release candidate as fallback; integrate real 504-row PR #18 data path with local Zetaris first or explicitly record that live proof remains BLOCKED. Complete public packaging/license review of the five PHIS files before any publication; never publish private source automatically. Do not let exploration research jeopardize a working sponsor-backed E2E demonstration.

**P1:** Independent study of 180-day stochastic benchmark, frozen generation/evaluation protocol, 3 archetypes and small deterministic multi-seed test; validate distributions, signal detection and false positives. Benchmark wall time and transport (>=1080 slots). No expensive infinite seed or algorithm sweeps.

**P1:** Implement an **additive**, provenance-backed Guidance Policy with three tiers. Maintain v1.1 semantics intact. Product copy and both evidence lenses in English.

**P2:** UI hierarchy, real Chrome evidence, judge script, README/deck/video and submission.

Quality gates:
- Original scientific tests and v1.1 classifications unchanged; raw CI/N/p/q/method/flags verifiable.
- Any extra 'possible contributor' is explicitly exploratory, its evidence/counterevidence traceable, with low-risk next steps; null simulations must not systematically invent drivers.
- A high-baseline/no-signal participant does not get manufactured improvement claims.
- Data mutations modify results and World Model follow-ups; fail closed on invalid/missing live data.
- Cold-clone reproducibility, official sponsor proof and private source safety required before submission.
- Technical, product and demo claims distinguish **CURRENT VERIFIED**, **INTEGRATED BUT BLOCKED**, and **ROADMAP**.

**Not yet implemented:** 180-day dataset, Guidance Policy, multi-seed benchmark or new v3 UI. Treat this as an explicit proposal/acceptance document for the next workers, not evidence that they work.
