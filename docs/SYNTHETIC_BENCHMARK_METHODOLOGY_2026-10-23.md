# Synthetic Benchmark Methodology — longitudinal improvement

**Status:** frozen generator and protocol; result ledger appears in `docs/STOCHASTIC_180D_RESULTS_2026-10-23.md`. All records are fictional. This benchmark tests engineering behavior and statistical interpretation, not clinical benefit.

## Why stochastic structure is needed

Independent random numbers have no persistent personal baseline, realistic calendar pattern or interpretable exposure history. Here, random daily variation sits around a fictional baseline and passes through predeclared lagged pathways. This permits both genuine relationships and misleading shared trends. It also makes negative controls, missed relationships and accidental discoveries measurable. One person with 180 calendar days does not provide 180 independent observations because successive days are correlated.

## Design and source dictionary

One generator call creates 180 consecutive local dates, 2026-04-25 through 2026-10-21, for one fictional case and seed. Each date has exactly six typed slots. Absent observations retain their slot with `value: null`, `observed: false` and `quality: not_recorded`; zero remains a legitimate measurement. Dates are local calendar dates, with no time-zone conversion. Synthetic source IDs identify each slot. The runtime analysis receives only the resulting observations. Generator mechanisms and case labels do not enter Discovery or a user-facing agent.

| Variable | Unit/source type | Meaning and timing | Generator bound |
| --- | --- | --- | --- |
| `energy_central` | score/10; fictional energy diary | subjective energy on local date | 1–10 |
| `sleep_hours` | hours; fictional sleep wearable | sleep attributed to waking date | 5.1–9.3 |
| `stress_score` | score/10; fictional stress diary | subjective daily stress | 1–9 |
| `late_caffeine` | binary after 14:00 local; fictional caffeine diary | 0/1 on consumption date; possible effect on following waking date's sleep | 0–1 |
| `exercise_load` | fictional load score/10; activity diary | daily activity load | 0–9.5 |
| `unrelated_count` | count/day; fictional control log | independent irrelevant control | 0–6 |

All values are explicitly synthetic. Source IDs and units follow the public v2 observation contract. The stress and exercise processes have serial dependence and weekday effects. A temporary workload episode rises and recovers; it is a shared potential explanation, not a directly imposed energy drop. Sleep has an overnight relation to prior-day conditions in the opportunity case. Energy has same-day sleep and stress and prior-day exercise relationships in that case. High-baseline and null/confounded cases suppress or weaken those pathways. A separate random stream creates the irrelevant count control; another creates missingness. The generator code gives exact coefficients and is kept offline, away from the runtime adapter.

Missingness is independently sampled at 5–8% by variable, with a two-day sleep-device gap. This is a limited model of real missed logging: missingness depending on fatigue or stress is not simulated. Values are rounded to three decimals. No measurement is a diagnosis, medical threshold or real participant record.

## Scientific evaluation and interpretation

The evaluator uses only the owner-approved isolated, local-only five-file PHIS Discovery v1.1 package pinned to private commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. It uses the **exact PR #18 plan policy** for two families, each with four exposure pairs, lags 0/1 and levels/first-differences routes: 16 children per family. Frozen settings include 999 resamples, 3/7/14-day block sensitivity, minimum N/effective N/coverage/effect, the original temporal policy and original hierarchical BY correction. No thresholds are changed. The plan SHA-256 values are printed in the results artifact. Neither an LLM nor this report recomputes or overrides engine classifications.

The same seed and case are evaluated on the trailing 84 days and all 180 days. Paired comparison exposes what extra history did and did not change. Development seeds are 3101 and 3102; untouched held-out seeds are 4101 and 4102. Seed 4101 is the predetermined illustration, regardless of its score. The protocol was committed at `52f61e5` and generator/evaluator at `d5df9d0` **before** the first Discovery run. Complete derived results are retained, including failed cases, controls and the sleep shuffle/sparse ablations.

Discovery's `candidate_signal` is the only Tier 1 basis. A separate `exploratory-guidance-v1` product policy may call certain original `unstable_candidate` results a *promising hypothesis* only after checking data coverage, aligned N, effect size and CI, lag/route and a low-risk question. It displays all flags, temporal diagnostics, correction values and block results. This label does not imply a statistically qualified signal, actionable factor, adjustment for confounding or cause. Raw correlation alone cannot enter Tier 1 or Tier 2. All other results are unsupported or insufficient. No control can enter the guidance tiers. The guidance policy is independently versioned; it never changes Discovery output.

## Trajectory, headroom and recommendations

Observed 28-day means, SD, range and completeness describe each trajectory independently of possible drivers. The high-baseline case is designed to have low improvement headroom, not a hidden condition to diagnose. The null/confounded case tests whether a shared workload pattern produces misleading pairwise associations. Neither deserves a fabricated improvement recommendation. Even a Tier 2 result supports only a bounded observation question; changes to medication, diagnosis or treatment are outside scope.

Trend-aware residual models, dynamic regression, change-point inference and multivariable adjustment are **proposals** requiring independent preregistration, implementation and validation. This benchmark does not use them.

## Product scope for judges

This branch implements a deterministic offline generator, scientific evaluation harness and separate guidance policy. PR #18 supplies an opt-in local Discovery integration path when the approved package is present, with evidence lineage and an actual tool call. PR #13 remains the runnable fallback. The current v2 live contract still expects 504 slots; this benchmark does **not** claim 1,080-slot Zetaris ingestion, UI integration, real wearable input or Apple Health connection. Automatic ingestion, proactive 24/7 operation and personal experiment coaching are future work. Any live Zetaris claim requires its own query proof; no mock read is represented as live.

## Reproduction

Set `PYTHONPATH` to this repository's `src` and the approved isolated PHIS package's `src` directory. Keep the private package outside the public checkout. Run `python scripts/benchmark_stochastic_180d.py > stochastic-benchmark-results.local.json`, then `python -m unittest tests.test_stochastic_benchmark -v`. The result artifact may be examined as JSON; do not add the private package to this repository. Times are local single-run wall times, not service-level guarantees.
