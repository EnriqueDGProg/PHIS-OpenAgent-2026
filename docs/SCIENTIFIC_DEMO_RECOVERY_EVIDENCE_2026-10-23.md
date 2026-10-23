# Scientific demo recovery: one registered scenario, one Discovery evaluation

**Decision: FAIL for scientific promotion; keep the PR #13 fallback.** This Draft PR is based on [PR #18](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/18). It adds a fictional generator, copied plans with unchanged scientific settings, offline evaluation entry point, focused source tests, and this English report. It does not wire an unqualified finding into the live agent. No private PHIS module, record, credential or proprietary path is committed. The owner still controls any private-code publication, license, merge or deployment.

## Why revision 2 promoted zero signals

The authentic local PHIS Discovery v1.1 baseline in PR #18 evaluated 16 predeclared children per family and classified energy 0 candidate / 5 unstable / 11 weak and sleep 0 candidate / 3 unstable / 13 weak. Strong raw associations were insufficient:

| Revision 2 comparison (levels) | r, N, 95% CI | Temporal diagnostic | 3/7/14-day block support | Selection child / parent BY q | Engine flags and result |
| --- | --- | --- | --- | --- | --- |
| Same-day sleep → energy | +.777, 74, [.703, .842] | incompatible: energy time trend Spearman −.654 exceeds frozen .55 incompatibility bound; sleep trend −.527 is caution | yes / yes / **no** | .0125 / **.1000** | `block_length_sensitive_or_insufficient`, `temporal_validity_incompatible_for_current_inference`; unstable |
| Previous-day stress → energy | −.501, 75, [−.691, −.248] | incompatible via energy | yes / yes / **no** | .0333 / **.1167** | same two flags; unstable |
| Previous-day late caffeine → sleep | −.810, 76, [−.858, −.755] | incompatible: caffeine half-median shift/IQR 2.0 exceeds frozen 1.5 bound | yes / yes / **no** | .0083 / **.0667** | same two flags; unstable |
| Previous-day stress → sleep | −.512, 73, [−.663, −.292] | caution | yes / yes / **no** | **.1000 / .2000** | block sensitivity; unstable |

The correction is performed within the full predeclared family, including both lags, two routes and the negative control. Primary resampling p values were .001 for these pairs, but the engine used worst-block selection p and hierarchical Bonferroni/BY corrections. Small primary p values and narrow intervals did not override unsupported 14-day blocks, parent q above .05 or temporal flags. The large recent caffeine/stress and energy shifts plausibly contributed to the temporal diagnostics; that is a diagnostic interpretation, not an adjusted or causal conclusion. The revision-2 temporal metrics were obtained by read-only `diagnose()` on its existing rows; its Discovery families and perturbations were **not** rerun.

## Chronology and frozen scenario

The [preregistration](SCIENTIFIC_DEMO_RECOVERY_PREREG_2026-10-23.md) was committed as `a324e89` before scenario code and before evaluation. The generator and plans were committed as `ec09f82` before the single baseline run. The generator is a modification of the public PR #17 fictional generator: a workload episode begins at index 63 (last 21 days), adding 0.90 to simulated stress and 0.08 to late-caffeine probability. No direct energy offset is used. The existing sleep, energy and exercise equations, seed `20261023`, independent control/missingness streams and two-day sleep logging gap remain. These equations are *simulation ground truth*, isolated in an offline module; they are never passed to Discovery or the answering agent.

The planned nonobvious pathway is prior late caffeine → next-day sleep → current energy, with stress as an observed confounder of multiple links. The planned sustained association is sleep versus energy across the full 84 days. Current stress and previous exercise also affect energy. This is a plausible fictional design, not evidence of mediation or an adjusted effect. No multivariable causal claim is available from the approved five-file Discovery subset.

Both v3 plan JSON files differ byte-for-byte from their PR #18 counterparts **only** in `dataset_id`. The unchanged scientific grid is four exposures per family, lags 0/1, levels and adjacent-calendar first differences, linear method, one-day window, 999 resamples, block lengths 3/7/14, min N 30, min effective N 20, coverage .70, |r| .30, BY q .05 and min group N 15. First differences remain review-only. The private temporal policy SHA-256 is `d708d6113ac1c503cd06aaf8f9f5db184136ad65c56d2429fbb21da4d402f460` and was not changed.

| Artifact | SHA-256 |
| --- | --- |
| Offline v3 generator bytes | `7ed78fb72ea64c9ee84009aaef12b678f648d5e8256b3fbd23a6bd51a268ea10` |
| Energy v3 plan bytes | `fa9b75351f0f25719361beab0180a2e26783688de30d11d9f978a749854d3c18` |
| Sleep v3 plan bytes | `12977e1c05a30516d4e679344bcb6f74d73b2496f8a8df4fe5e4eb64ed045432` |
| 504 sorted synthetic rows, compact sorted-key JSON, ASCII | `ea49eb084eed5aa10b3ffe0369239e26a53f1ce9bbea6af9ab93779cf864a650` |
| First baseline derived JSON bytes (local-only) | `0c1540aa30764af537efd71727dc9131e77b2afe0920197c46fcaf92f1a0346b` |

## One blind baseline: actual outcome

The first and only revision-3 baseline finished successfully. Both families returned all 16 children, but **zero `candidate_signal`**: energy 4 unstable / 12 weak; sleep 4 unstable / 12 weak. The predeclared recent energy-change target passed: observed consecutive 28-day means were 6.5786 / 6.0576 / 5.7657, final minus middle **−0.2919** points. This is a descriptive change without an inferential interval. Observed sleep means were 7.2418 / 7.0460 / 6.8172 hours; caffeine frequencies .3333 / .4286 / .6071; stress means 3.9169 / 4.2426 / 4.7083. The last-window differences arise from this single fixed seed; they were not selected by rerunning seeds.

| Revision 3 comparison (levels) | r [95% resampling CI], raw N | Primary p / child BY q | Worst-block selection p / child BY q / parent BY q | 3/7/14-day blocks | Temporal, flags, class |
| --- | --- | --- | --- | --- | --- |
| Same-day sleep → energy | +.8717 [.8226, .9216], 74 | .001 / .00417 | .003 / .01111 / .05000 | yes / yes / yes | **caution**, `temporal_validity_caution`, unstable |
| Previous-day stress → energy | −.4580 [−.6300, −.2649], 75 | .001 / .00833 | .002 / .01667 / .05000 | yes / yes / yes | **caution**, `temporal_validity_caution`, unstable |
| Previous-day late caffeine → sleep | −.8462 [−.8896, −.8023], 76 | .001 / .00417 | .002 / .00833 / **.06667** | yes / yes / **no** | caution, block/temporal flags, unstable |
| Previous-day stress → sleep | −.5243 [−.6689, −.3797], 73 | .001 / .00833 | .004 / .02083 / **.06667** | yes / yes / **no** | caution, block/temporal flags, unstable |
| Energy negative control, same day | −.0609 [−.2911, .1754], 76 | .604 / 1 | .654 / 1 / 1 | no / no / no | weak, unpromoted |
| Sleep negative control, same day | −.1574 [−.3486, .0365], 74 | .211 / .8792 | .285 / 1 / 1 | no / no / no | weak, unpromoted |

The strongest energy pair met the numerical q and block checks, but **did not meet the temporal validity gate**. The energy series time Spearman statistic was −.3897, crossing the frozen .35 caution bound, while sleep was −.3183 and compatible. Stress also had caution for time trend (+.3528), half-regime shift (.8303) and variance shift. Caffeine's robust half-median shift was 1.0, above the .8 caution bound. These observations explain the `unstable_candidate` classes. They cannot be promoted by rounding q=.05, ignoring temporal flags or changing thresholds.

## Integrity, timing and adversarial checks

The source has 504 unique date-variable slots for 2026-07-30 through 2026-10-21, all explicitly synthetic and tied to `fictional-001`; missing values are null, never zero-filled. Observed counts of 84 are energy 80, sleep 78, caffeine 83, exercise 79, stress 80, control 79. Counts in successive 28-day windows are energy 26/27/27, sleep 24/27/27, caffeine 27/28/28, exercise 26/25/28, stress 27/25/28, control 26/26/27. All exceed .70 coverage, without a severe late missingness shift. Observed ranges are energy 3.712–8.043/10, sleep 5.388–8.286 h, exercise 1.091–6.683/10, stress 1.789–6.900/10, caffeine 0–1 and control 0–6. The 20–21 sleep gap remains null.

Calendar-aligned complete pairs show prior-day caffeine versus next-day sleep r=−.8462 (N=76), while same-day caffeine versus sleep is −.0543 (N=77). Same-day sleep versus energy is +.8717 (N=74); prior-day sleep versus energy is −.0462 (N=73). These descriptive checks confirm the intended lag direction and show why shifting dates by one would materially change the conclusion. Adjacent-calendar differences never bridge a missing day. A static import test verified the offline v3 generator is not imported by the v2 source contract, Zetaris adapter, Discovery adapter or agent. The live PR #18 route still points to the prior synthetic revision, because v3 failed promotion.

All four predefined perturbations completed using the unchanged v3 plans:

| Check | Actual result | Gate |
| --- | --- | --- |
| Shuffle observed sleep, preserving missing slots | sleep→energy r +.8717 → +.0332; N 74; CI [−.1308, .1886]; child/parent selection q 1/1; weak | PASS |
| Shuffle observed caffeine, preserving missing slots | caffeine→sleep r −.8462 → +.2411; N 76; CI [.0501, .4542]; selection q .1292/.2833; weak | PASS for no promotion; residual association is a limitation |
| Reflect energy around its observed mean | sleep→energy r −.8717; N 74; CI [−.9218, −.8227]; still unstable due temporal caution | PASS sign check |
| Keep sleep only every sixth day | N 13, coverage .155, raw r +.8975; `insufficient_data`, CI null, p/q 1 | PASS abstention |
| Unrelated-count negative controls | neither family promoted one in baseline or perturbations | PASS |

The shuffled caffeine residual r=.2411 is not zero and has a primary interval above zero, but it fails the unchanged selection correction and effect gate. It must not be presented as a supported finding. None of the above tests establishes causality or robustness to unmeasured confounding.

## Reproduction, exact commands and next decision

Environment used: Python 3.12.10 on Windows, public branch from PR #18 at `a2dc3c0`, approved local-only PHIS Discovery baseline `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. Set `PHIS_PRIVATE_SRC` to the approved five-file package's local `src` directory **outside this checkout**. The path and module contents are intentionally withheld. Save derived JSON outside the public repository; the four local outputs have SHA-256 baseline `0c1540aa30764af537efd71727dc9131e77b2afe0920197c46fcaf92f1a0346b`, ablation `d146ae4cc033930fd01577e5bfe53a5328c2c699bb7d6ccdf13a0729deda0f36`, reversal `31cdc85c428e4e6f558aa365e683fc40d12d6ffc4781b987df004bba413fce97`, low coverage `9524c309debcb50407c6edc0cd3a2c0550b895aea5122805942c7d5d9b88d24a`.

```powershell
$env:PYTHONPATH = "src;$env:PHIS_PRIVATE_SRC"
python scripts/validate_scenario_recovery.py --mode baseline > $env:PHIS_LOCAL_EVIDENCE\recovery-baseline.local.json
python scripts/validate_scenario_recovery.py --mode ablate > $env:PHIS_LOCAL_EVIDENCE\recovery-ablate.local.json
python scripts/validate_scenario_recovery.py --mode reverse > $env:PHIS_LOCAL_EVIDENCE\recovery-reverse.local.json
python scripts/validate_scenario_recovery.py --mode low-coverage > $env:PHIS_LOCAL_EVIDENCE\recovery-low-coverage.local.json
python scripts/check_scenario_v2_results.py $env:PHIS_LOCAL_EVIDENCE\recovery-baseline.local.json $env:PHIS_LOCAL_EVIDENCE\recovery-ablate.local.json $env:PHIS_LOCAL_EVIDENCE\recovery-reverse.local.json $env:PHIS_LOCAL_EVIDENCE\recovery-low-coverage.local.json
python -m unittest discover -s tests -q
```

Actual command results: all four Discovery invocations exit 0; the perturbation checker prints `PASS: baseline, ablation, sign reversal, low coverage, control, plan identity`; Python tests **PASS 74/74**. Scientific acceptance criterion 1 (integrity/coverage) PASS, criterion 2 (recent energy drop) PASS, criterion 3 (at least one promoted energy candidate) **FAIL**, criterion 4 (perturbations/control) PASS with the residual caffeine-ablation caveat. These are separately reported so successful execution is not mistaken for scientific promotion.

**Next decision: no-go for presenting v3 as a supported scientific-contributor demo.** Preserve the fallback PR #13 and the honest abstaining PR #18 narrative. Another scenario would require a new, separately approved preregistration and independent evaluation; this PR makes no further revisions. Owner review of rights/IP and license remains required before any private Discovery source extraction or publication. No merge, deployment, paid service or real health data was involved.
