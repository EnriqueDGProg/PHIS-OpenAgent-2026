# PHIS Open Agent 2026 — Evidence Investigation v2

**Status:** founder-approved product direction / design specification; **not** an implemented feature or verified scientific result.  
**Date:** 2026-10-23. **Validated technical fallback:** Draft PR #13.  
**Owner:** AI Venture Studio / PHIS. **Judge-facing language:** English.

## 1. Product thesis

**PHIS — Personal Health Intelligence System** investigates potential contributors to a change in a person's health by orchestrating multi-source longitudinal records, deterministic scientific analysis, evidence-strength assessment, persistent agent memory, and understandable explanations.

The hackathon demonstrates **two bounded investigation families — energy and sleep — plus meaningful follow-ups**. It should be engineered so new domains can be added with new validated datasets and analytical plans; it does **not** claim to answer arbitrary health questions today.

Primary user value: **What changed? Which factors might explain it? How strong is the evidence? What could disprove the interpretation? What can I track or discuss with a professional next?**

It is **not** a medical device and does not diagnose, prescribe, select treatments or autonomously change medications. It may suggest low-risk, generally sensible self-observation and habit-review steps consistent with actual evidence and user autonomy.

## 2. Flagship judge path

1. Open the English application: PHIS name and expansion, clear explanation, synthetic/fictional disclosure, two supported examples.
2. Ask: **Why has my energy declined recently?**
3. Agent plans and retrieves the actual synthetic rows from **Zetaris**; trace carries request ID, query ID, row/source IDs and query proof.
4. Scientific computation detects change, investigates predeclared factors, temporal lags and confounding/robustness, and returns traceable evidence packages.
5. Agent ranks supported **candidate contributors**, separates observed associations from speculative explanations, and clearly labels insufficient/contradictory evidence.
6. **Meterless official World Model Engine** persists the verified investigation context; the user asks a sleep-related follow-up; the agent reads the prior evidence and makes a measurably different tool decision.
7. Evidence drawer reveals observed values, units, dates, N, missingness, effect estimates, confidence intervals, correction family, method/policy, sensitivity results, uncertainty and tool provenance **only where these quantities were actually computed**.
8. Show an actual negative control / insufficient-data / source-failure case; don't present simulated sponsor calls as real.

One main investigation of outstanding quality is more valuable than many shallow capabilities.

## 3. Fictional dataset v2 — scientific scenario specification

**Proposed, contingent on PHIS Discovery capability audit.** 84 days, one strictly fictional participant, Europe/Madrid dates, reproducible fixed seed, source-typed records, stable IDs, explicit null/missing days and a published generator separated from the runtime analytical evidence. The agent must never receive the generator's causal-structure metadata.

Candidate variables:
- `energy_central`: 1–10 subjective energy diary, **primary outcome**.
- `sleep_hours`: wearable-derived sleep duration, **exposure for energy, outcome for sleep investigation**.
- `caffeine_last_intake_hour` and/or `late_caffeine`: diary-derived exposure with clear units and ascertainment.
- `exercise_load`: activity-derived load/intensity, avoid inventing a medical-grade metric.
- `stress_score`: subjective stress diary; potentially a shared cause/confounder.
- One optional **negative-control** variable with no deliberate association to outcomes (e.g., a simulated unrelated daily count), explicitly excluded from headline conclusions.

**Generator-only hidden ground truth (illustrative design, not inferred from PHIS data):**
- Late caffeine may precede shortened sleep; shortened sleep may contribute to next-day reduced energy.
- High stress may affect sleep, energy and caffeine behavior and create confounding.
- Strenuous training may show a lagged association with next-day fatigue; light activity need not.
- Include weekday patterns, autocorrelation, modest noise, occasional missing entries and realistic phase changes; do not make perfect deterministic correlations.
- Include null associations, misleading contemporaneous correlations and insufficient-data conditions.
- A clear but **not guaranteed** discoverable signal is desirable; the scientific engine must be allowed to reject all candidates if its gates fail.

Before shipping data, independently check ranges, plausible timing, leakage, duplicates, units, missingness and whether a *blind* analytic test (not reading generator internals) behaves as intended. Never tune result labels or code branches to return a predetermined explanation. If scientific thresholds are not met, adjust the generator transparently and rerun controls; do not bypass significance/robustness gates.

## 4. PHIS Discovery integration gate — PRIORITY P0

Private baseline: `EnriqueDGProg/PHIS` commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. Existing dependency audit: `docs/DISCOVERY_DEPENDENCY_TEST_GATE_2026-10-18.md`.

Candidate modules include `discovery_features`, `discovery_signals`, `discovery_shapes`, `discovery_temporal`, `discovery_v11`, `discovery_validation`, and `discovery_multivariable`. Their import closure and real regression status are **not yet certified**. The multivariable module explicitly identifies its analysis as **review-only**.

**No automatic private-to-public copying.** Audit import closure and licenses, test the private baseline, identify minimum extraction, review intellectual-property / reuse rights and a SHA/file manifest; obtain owner's approval before publishing any source. Document pre-existing code versus new competition-window integration in the submission. If extraction fails this gate, use a scientifically narrower separately implemented analysis; do not falsely claim original Discovery was connected.

Statistical requirements where available: predeclared hypothesis family, valid sample and missingness accounting, direction/effect with CI, adjusted multiple-testing metrics, temporal and lag diagnostics, sensitivity / negative controls, explicit exploratory classification, and no causal confirmation from unobserved correlations alone.

## 5. Sponsor separation

**Zetaris:** verified live source and query results, not CSV mocks labeled live.

**Meterless Engine:** genuine, pinned official World Model source used by the agent; event → durable state → fresh read → tool decision changed, with event/proof identity.

**Meterless Runtime/Power and NVIDIA:** separate capabilities; never mark as connected or verified without authentic inference responses. Recheck their binding requirements and documentation before submission. Cursor is optional according to the organizer's newer Build announcement; no purchase needed.

**No secret/PHI publication**; only fictional records; fail closed on unavailable sources; don't use expensive external services without authorization.

## 6. English-first UX revision

Retain the current visual identity: deep green, warm off-white, polished editorial panels. Improve semantic design and information hierarchy, not just typography.

- Brand **PHIS** (uppercase, no terminal dot); explain *Personal Health Intelligence System*.
- Left: short product promise, true scope, supported example prompts, **Run investigation**, readable agent-activity phases (collapsible detailed trace), synthetic disclosure.
- Right: **primary supported finding first**, ranked potential contributors and their evidence strength, alternate hypotheses, practical next observation/action, then time-series visualization and methods / evidence.
- Dynamic heading reflects the actual question, not always energy.
- Remove or demote `Clinical request` and confusing `CONTINUE OR TEST A LIMIT`. Keep safety refusals in tests, not as headline product features.
- Explain supported two domains, and that other domains need datasets and validated plans; avoid unsupported 'universal health AI' claims.
- Remove unexplained `01/01` ornament and `SF` avatar or label fictional profile intelligibly; fix title/ornament overlaps.
- Replace `ABSTENTION` and bare `LIMIT` with user-facing explanations and supported next actions. Keep explicit safety behavior under the hood.
- Visualize gaps as `No measurement recorded`; don't interpolate missing values. Use a legible trend with selected/highlighted points rather than dense unexplained dot markers.
- Hide empty `No period comparison` cards; show something useful in follow-up.
- `Inspect evidence` opens actual source, variable, date, value, N, computation and provenance; `Why this limitation?` explains missing/conflicting evidence and ways to investigate.
- No Spanish copy, including loading statuses; desktop/mobile keyboard accessibility and semantic focus preserved.

## 7. Scientific communication

Prefer **candidate contributing factors** and **strength of evidence**, never a made-up numerical confidence score. Distinguish:
1. Observed change: directly computed and traceable.
2. Association: computed adjusted/descriptive relationship, with N, effect, CI and uncertainty as available.
3. Causal hypothesis: biologically/temporally plausible interpretation with alternatives; observational evidence cannot by itself prove cause.
4. Experimental or clinical confirmation: only when an actual appropriate design exists; **not claimed by this demo**.

Do not saturate the main interface with 'causality not established'. Provide constructive, accurately bounded interpretation with methods accessible behind details. Explain counterevidence and what new observations would strengthen/refute the hypothesis.

## 8. Acceptance gates

- **G1 scientific:** independent tests show dataset/model changes affect computed findings; null and confounded relationships are not falsely promoted; no invented statistics.
- **G2 technical:** true Zetaris REST rows feed computations; official Meterless World Model changes follow-up; distinct verified proof IDs; no silent local fallback; clean clone and process-restart checks.
- **G3 user value:** energy and sleep questions lead to relevant, meaningful conclusions or specific honest insufficiency; evidence link provides real analytical detail.
- **G4 safety:** no diagnosis or therapies, no private data, well-calibrated evidence and uncertainty.
- **G5 UX:** all visible English, clear scope, meaningful buttons/panels, clean charts, no overlap/empty dead cards, desktop/mobile and accessibility.
- **G6 submission:** source disclosure, honest sponsor matrix, reproducible demo, official 1–4 min video, slides, README and HackOS submission.

## 9. Work packets / ownership

- **A — Discovery audit:** read-only on private repo. Audit tests/imports/IP and minimum manifest; English PASS/BLOCKED report. No extraction until approved.
- **B — Dataset + analytic contract:** design-only first, then implementation after A determines supported methods and variables.
- **C — Core integration:** Zetaris → approved Discovery tools → Meterless Engine → explanation contract. Independent PR, protect PR #13 fallback.
- **D — UX:** update visual system against C's evidence payload and founder feedback, English only.
- **E — Submission readiness:** in parallel, real video story, deck, sponsor proof and pre-existing code declarations.

**Deadline:** 2026-10-27 23:45 UTC. Preserve margin for independent E2E, recording and actual submission. Never equate a worker's PASS statement with owner acceptance.
