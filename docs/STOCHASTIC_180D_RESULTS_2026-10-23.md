# Stochastic 180-day benchmark — actual results and decision

**Scientific decision: FAIL for automatic longitudinal improvement guidance.** The deterministic benchmark and authentic Discovery execution work, but results do not support a general claim that 180 days reliably identifies improvement drivers or abstains in the confounded archetype. The preregistered generator and guidance gates remain unchanged. Do not tune a preferred seed or scientific threshold after this result.

The [preregistration](STOCHASTIC_180D_PREREG_2026-10-23.md) was committed as `52f61e5`; the [generator and evaluator](../scripts/benchmark_stochastic_180d.py) as `d5df9d0`, before any new Discovery output was read. The English [methodology and dictionary](SYNTHETIC_BENCHMARK_METHODOLOGY_2026-10-23.md) distinguish generator truth from engine findings. The complete compact results for **all 12 seeds/cases, both windows, both original 16-child families and both ablations** are in [stochastic_180d_results.json](evidence/stochastic_180d_results.json), SHA-256 `6cde0e35c0c1a84edd6cb3f34007cc72bfc885f977db782bfc946e78c6153592`. This public artifact contains derived synthetic statistics only, no private engine source or real health record.

## Execution and scientific plan integrity

- Authentic owner-approved local PHIS Discovery v1.1, private baseline `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. The five approved source files stayed outside this public checkout.
- Exact PR #18 scientific policy and families, including 999 resamples, 3/7/14-day blocks, original temporal flags and BY corrections. Original plan hashes: energy `02b7495e68c577170335d7403f777ecb3105dc6857b07baf538493a2fccf235a`; sleep `864844abbafc9c0743f4f6e9a82b560c8f86276ee45c537617fa1a0fb7299b44`. The plan JSON's `dataset_id` is the inherited v2 label; only its policy/pairs/routes/seed are passed to `search_v11`, while benchmark rows carry their own 180-day IDs. This metadata mismatch prevents claiming the existing v2 runtime contract supports 1,080 slots.
- Four predeclared seeds per archetype. Development 3101/3102; held-out 4101/4102. No seed was discarded. Each case has 1,080 unique typed slots; every variable across all 12 full-history cases has >=89.44% observed coverage. Missing slots remain null.

## Every seed: original `candidate_signal` counts and runtime

Counts are energy/sleep, each out of the unchanged 16-child family. Other children and all diagnostic values remain in the JSON artifact.

| Cohort | Case | Seed | 84-day candidates E/S | 180-day candidates E/S | 180-day both-family seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| development | opportunity | 3101 | 4 / 0 | 3 / 2 | 23.0 |
| development | opportunity | 3102 | 0 / 0 | 3 / 2 | 22.0 |
| development | high baseline | 3101 | 0 / 0 | 0 / 0 | 33.6 |
| development | high baseline | 3102 | 0 / 0 | 0 / 0 | 22.5 |
| development | null/confounded | 3101 | 0 / 0 | 2 / 1 | 32.3 |
| development | null/confounded | 3102 | 0 / 0 | 1 / 0 | 26.2 |
| held-out | opportunity | 4101 | 4 / 4 | 3 / 2 | 35.8 |
| held-out | opportunity | 4102 | 3 / 2 | **0 / 2** | 17.8 |
| held-out | high baseline | 4101 | 0 / 0 | 0 / 0 | 35.0 |
| held-out | high baseline | 4102 | 0 / 0 | 0 / 0 | 19.3 |
| held-out | null/confounded | 4101 | 0 / 0 | 1 / 1 | 39.5 |
| held-out | null/confounded | 4102 | 0 / 0 | 1 / 0 | 18.7 |

Across all 12 cases, both-family wall time was 7.47–11.26 s (median 8.87) at 84 days and **17.85–39.51 s (median 24.57)** at 180 days on this local Windows host. Several 180-day runs exceed the PR #16 proposed 30-second operational deadline for a bounded live investigation. This is a measured local cost, not a production SLA. No resampling or block reduction was made to improve it.

## Known mechanisms: detected and missed

In the opportunity archetype across four seeds at 180 days, original levels-route `candidate_signal` detection was: same-day sleep → energy **3/4**, same-day stress → energy **3/4**, prior-day caffeine → sleep **4/4**, prior-day stress → sleep **4/4**, prior-day exercise → energy **0/4**. At 84 days those counts were 3/4, 3/4, 2/4, 2/4 and 0/4 respectively. Thus longer history improved two sleep-family pathways but did not recover the weaker exercise pathway and lost both energy promotions in held-out seed 4102. A true simulated coefficient is not proof the pairwise engine can identify it.

The predetermined illustration is opportunity seed **4101**, not the highest-scoring seed selected after testing. Over 180 days, same-day sleep → energy was `candidate_signal`, r=+.5604, N=159, 95% CI [.4211,.6742], selection BY child/parent q=.00417/.01667, temporally compatible, supported at 3/7/14-day blocks with no quality flags. Prior-day caffeine → sleep was also `candidate_signal`, r=−.5546, N=160, CI [−.6437,−.4412], q=.00417/.01667 and all three block lengths supported. Same-day stress → energy was r=−.4390, N=164, CI [−.5523,−.2785], q=.00417/.01667, similarly supported. These are **unadjusted observational associations in fictional data**, not causal or clinical claims. Stress is a competing explanation for part of the sleep–energy relation. Prior-day sleep also correlates with energy (+.304 descriptively), consistent with serial dependence, so calendar direction matters.

Across that illustration, energy means in successive complete 28-day blocks were 6.165, 6.108, 5.849, 4.965, 6.110 and 5.619/10: a dip, recovery and later variability, rather than a monotone scripted drop. Full-history mean/SD were energy 5.823/1.001, sleep 6.897/0.653 h and stress 4.436/1.153. Caffeine on date *t* correlated −.555 with sleep on *t+1*, compared with −.208 same-day; sleep on date *t* correlated +.560 with energy on *t*. These alignment figures are descriptive checks, not additional inferential discoveries.

## Negative controls, ablation and failures

- The independent unrelated-count control was **never** an original `candidate_signal`: 0 of 192 declared control children across 12 cases × 2 windows × 2 families × 4 lag/route children. It is excluded from guidance tiers. In illustration seed 4101, the same-day sleep-family control's primary CI excluded zero, yet it remained `weak_candidate` (selection parent q=.05556 and no supported block length). This demonstrates why an isolated raw interval/correlation cannot qualify a factor.
- Illustration sleep shuffle preserved missing slots and changed same-day sleep → energy from r=+.5604 `candidate_signal` to r=−.0634 `weak_candidate`, N=159, CI [−.1789,.0624], selection child/parent q=.9271/1.0. Sparse sleep retained a large raw r=+.7606 but yielded `insufficient_data`, N=25, coverage .139, CI null, selection q=1/1. Both abstention checks passed.
- High-baseline 180-day cases had **zero** engine candidates and zero guidance tiers above unsupported. Example seed 4101 energy averaged 7.715/10 (SD .582) and sleep 7.758 h. No improvement recommendation is warranted. At 84 days, development seed 3102 did receive one Tier 2 stress hypothesis: an explicit failure of across-window low-headroom abstention. It must not be framed as a need to improve.
- The `null_confounded` case is **not a pure null**: the frozen generator includes genuine stress pathways to energy and sleep. The engine promoted stress in the 180-day cases, so those are not automatically false-positive scientific findings. However, the archetype **fails the intended null abstention test** and cannot establish false-positive control for confounded drivers. The absent direct sleep → energy and caffeine → sleep pathways were not promoted in these four cases, but this limited result does not validate general confounding robustness. No parameter or guidance gate was changed after seeing this outcome.
- The additive `exploratory-guidance-v1` maps original `candidate_signal` to supported observational pattern, selected flagged `unstable_candidate` to promising *observation* hypothesis only with predeclared N/coverage/effect/CI checks, and all others to unsupported/insufficient. It preserves class, q, temporal and block flags. It is **not validated for broad automatic guidance**: confounded cases can still surface stress, and 84-day high-baseline seed 3102 surfaces a Tier 2 hypothesis. No automatic recommendation from this policy should power the final demo.

## PASS / FAIL / BLOCKED and demo recommendation

| Gate | Result |
| --- | --- |
| Reproducible generator, complete unique synthetic slots, plausible ranges, missingness and source labels | **PASS** |
| Authentic unchanged Discovery on all predeclared seeds, both windows; complete results retained | **PASS** |
| Expected sleep/caffeine/stress opportunity pathways detectable in some independent seeds | **PASS with misses** |
| Independent negative control unpromoted; shuffle and sparse ablations abstain | **PASS** |
| 180 days uniformly improves identification; exercise pathway recovered | **FAIL** |
| Pure null/confounded case and high-baseline abstention across both windows | **FAIL** |
| Automatic exploratory improvement guidance validated for general use | **FAIL** |
| Existing live Zetaris v2 route accepts 1,080 slots and meets <=30 s paired-family budget | **BLOCKED / FAIL**: v2 contract is 504 slots; 180-day local timing sometimes exceeds 30 s |
| Public redistribution of private Discovery, merge, deployment and final submission | **BLOCKED** by the existing owner rights/IP, review and submission gates |

**Concrete demo choice:** PR #13 remains the runnable fallback. If the approved local package is available, the final demo may show the *specific* original Discovery v1.1 observational findings in opportunity seed 4101, clearly labeled synthetic and unadjusted, plus the descriptive trajectory, competing stress explanation, null control and ablation. Do not imply the existing PR #18 live route ingests this 180-day record, that the exploratory policy is generally validated, or that automatic wearable/Apple Health ingestion and 24/7 operation exist. The 84-day PR #17 qualified findings remain separately documented; the PR #18/#19 recent-drop claims failed their own gates. A genuine 180-day live scientific route and a true confounded-null validation require a new reviewed packet and preregistration.
