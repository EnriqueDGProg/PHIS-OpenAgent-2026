# Synthetic 84-day scientific scenario — offline evidence record

Status: **Draft review only.** This package is new hackathon work. Every record is fictional. The PHIS Discovery v1.1 implementation remains in an owner-approved local package outside this repository; this PR contains no private module, health record, credential, or source extract.

## Scope and provenance

- Product direction: [PR #14](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/14). Scientific feasibility and reuse gate: [PR #15](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/15). Local-only extraction preparation: [PR #16](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/16). Existing runnable fallback: [PR #13](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/13). This PR changes none of them.
- The original private Discovery baseline is `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. Its five-file preparation manifest and rights gate are recorded in PR #15/#16; no Discovery source is proposed here.
- Competition work is separate from preexisting PHIS code. The [official event page](https://hackathon.genai.works/event/open-agent-hackathon-2026) was checked on 2026-10-23 for the October 22 build-window opening and Wildcard preexisting-project rule. Final organizer interpretation and submission remain owner gates.

## Dataset and scientific intent

`src/phis_open_agent/scenario_v2.py` generates 84 consecutive local dates, 2026-07-30 through 2026-10-21, for one explicitly fictional participant. There are six typed rows per day (504 total): daily energy score, previous-night sleep hours assigned to waking date, late caffeine indicator (after 14:00 local), exercise load, stress score, and an unrelated count as negative control. Source types and unique synthetic source record IDs allow a Zetaris adapter to preserve row lineage. Null values mean missing measurements; no zero-filling or calendar compression is allowed.

The generator uses independent fixed-seed streams for the modeled signals, missingness, and negative control. It includes weekday variation and noise; stress affects late caffeine and energy, prior-day caffeine/stress/exercise influence subsequent sleep, and sleep/stress/prior exercise influence energy. A modest recent stress and caffeine shift creates a plausible 84-day investigation. This is a *simulation design*, not an inferred causal explanation. The design equations live only in the offline generator. Runtime answer construction must receive observations and Discovery evidence, never these equations or a prewritten answer label.

The fixed seed is `20261023`; changing it changes the fictional sample. Expected missingness is roughly 5–7% per variable, plus a two-day sleep logging gap. The fixed sample has observed counts: energy 80/84, sleep 78/84, caffeine 83/84, exercise 79/84, stress 80/84, control 79/84. Recorded values remain bounded in their declared units.

## Frozen analysis plans

The plans were declared before scientific tuning. Revision 0 of the generator produced no promotable candidate; revision 1 adjusted only fictional signal strength/noise and was then frozen. No analysis threshold, grid, family membership, or promotion gate changed between revisions. Both plans use 999 resamples and seed `20261023`, linear correlation, lags 0/1, one-day window, levels and adjacent-calendar first differences, blocks 3/7/14 days, minimum raw N 30, effective N 20, coverage 0.70, effect magnitude 0.30, BY q 0.05, and minimum group N 15. Each family has four predeclared pairs × two lags × two routes = **16 children**, including untestable hypotheses. First differences are review-only.

| Family | Predeclared exposures → outcome | Plan SHA-256 |
| --- | --- | --- |
| Energy | sleep, exercise, stress, negative control → energy | `6e9d1d9b87b0588558e173a0cacf2d94e5aa492f5b436dc0935928cced8cf3fe` |
| Sleep | late caffeine, exercise, stress, negative control → sleep | `1f82700b33f9790dbe6859a3bc98dd68ec60d1f21843d493ef3c685d07d8a6af` |

Discovery v1.1 applies a primary block-resampling child BY correction and a separate worst-block selection correction: Bonferroni minimum child within each parent, then BY across four parents, plus BY across four local children. Promotion also requires a confidence interval excluding zero, temporal compatibility, stable blocks, clean flags, and the levels route. The correction scope is exploratory dual parent/child control, **not global selective child FDR**.

## Fixed-seed Discovery results

The first, middle, and final 28-day **observed** means are energy 6.579, 6.058, 6.001; sleep 7.242, 7.046, 6.939 hours; late caffeine 0.333, 0.429, 0.571; stress 3.917, 4.243, 4.283. Energy is 0.577 points lower in the final than the first window, but only 0.056 lower than the immediately preceding window. These descriptive differences have no inferential interval and do not establish a sharp recent drop or cause.

The energy family yielded 2 `candidate_signal`, 2 `unstable_candidate`, and 12 `weak_candidate`; the sleep family yielded 0, 4, and 12 respectively. Selected levels-route results below are from the unchanged local PHIS Discovery v1.1 engine. `q child` and `q parent` are **selection** BY values; CI is the engine's 95% resampling interval for Pearson r. All p values are exploratory.

The primary child BY q values for the first four rows below are .0042, .0083, .0042, and .0083 respectively. The selection parent gate is exactly .0500 for the two energy candidates and .0667 for the two sleep results. A displayed equality at .0500 is a boundary pass under the declared `q <= .05` rule, not evidence of broader robustness beyond this fictional sample.

| Family / exposure, lag | Class | r [95% CI] | Raw N / effective N | Primary p; selection p | Selection q child / parent | Temporal / block robustness |
| --- | --- | --- | --- | --- | --- | --- |
| Energy / sleep, 0 days | candidate_signal | +0.869 [0.819, 0.920] | 74 / 73.7 | .001; .003 | .0111 / .0500 | compatible; 3/7/14-day blocks stable; no flags |
| Energy / stress, 1 day | candidate_signal | −0.413 [−0.594, −0.217] | 75 / 75.0 | .001; .002 | .0167 / .0500 | compatible; blocks stable; no flags |
| Sleep / late caffeine, 1 day | unstable_candidate | −0.859 [−0.900, −0.816] | 76 / 74.0 | .001; .002 | .0083 / .0667 | temporal caution; blocks stable; **no promotion** |
| Sleep / stress, 1 day | unstable_candidate | −0.506 [−0.666, −0.348] | 73 / 73.0 | .001; .004 | .0167 / .0667 | temporally compatible, but parent gate fails; **no promotion** |
| Energy / negative control, 0 days | weak_candidate | −0.099 [−0.308, 0.125] | 76 / 76.0 | .401; .464 | 1.000 / 1.000 | unpromoted |
| Sleep / negative control, 0 days | weak_candidate | −0.183 [−0.370, 0.0003] | 74 / 70.9 | .149; .191 | .796 / .900 | unpromoted |

**Supported wording:** in this fictional sample, same-day sleep and prior-day stress show qualified associations with energy under the frozen exploratory plan. The late-caffeine/prior-night-sleep association is strong in raw magnitude but remains unstable under the engine's temporal and family gates. The data do not justify saying late caffeine *caused* the energy change, giving medical advice, or claiming an adjusted multivariable effect. Stress is an explicit potential confounder; this plan is pairwise. A multivariable review would need a separately declared method and test family. The negative-control result gives a useful failure check, not proof of model validity.

## Adversarial checks and exact commands

The public generator and tests need Python 3.11+ and the standard library. The offline validation script additionally requires the owner-approved local-only `phis_master` package on `PYTHONPATH`; it is intentionally absent from this repository. The following commands were run under Python 3.12.10 with the local package path supplied externally. Output files named `*.local.json` were kept outside this repository and were not published.

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v

# In a separate secure local checkout, set PHIS_LOCAL_SRC to the approved
# private package's src directory. Keep these derived outputs local.
$env:PYTHONPATH = "src;$env:PHIS_LOCAL_SRC"
python scripts/validate_scenario_v2.py --mode baseline > baseline.local.json
python scripts/validate_scenario_v2.py --mode ablate > ablate.local.json
python scripts/validate_scenario_v2.py --mode reverse > reverse.local.json
python scripts/validate_scenario_v2.py --mode low-coverage > low-coverage.local.json
python scripts/check_scenario_v2_results.py baseline.local.json ablate.local.json reverse.local.json low-coverage.local.json
```

| Check | Result |
| --- | --- |
| Four generator contract tests | **PASS**, 4/4 |
| Baseline two frozen families | **PASS** execution, 16/16 children per family; classifications as above |
| Delete sleep and caffeine timing associations through deterministic observed-value permutation | **PASS**: sleep→energy r fell from +.869 to +.062 (N 74, CI [−.104, .219], primary p .587, selection q child/parent 1/1, weak); caffeine→sleep changed from −.859 to +.247 (N 76, CI [.046, .458], primary p .016, selection q .115/.417, weak). Neither target promoted. |
| Reverse energy sign about its observed mean | **PASS**: sleep→energy r changed from +.869 to −.869, N 74, CI [−.920, −.819], still candidate under the unchanged plan. The engine did not encode the expected sign. |
| Suppress sleep to roughly one-sixth calendar coverage | **PASS**: sleep→energy N 13, coverage .155, class `insufficient_data`, CI null, p=1, child/parent q=1, despite an uninterpretable raw r=.895. No promotion. |
| Negative control never promoted in baseline or perturbations | **PASS**, both baseline families and all four perturbation runs |
| Machine-check derived results | **PASS**: `check_scenario_v2_results.py` checked family size, plan identity, ablation, sign reversal, low coverage, and negative controls. |

These perturbations are offline counterfactual checks. They do not create a second plan, change correction denominators, or supply labels to runtime.

## Integration boundary and release gates

The intended path is `Zetaris records → typed synthetic observation rows → calendar-aligned Discovery evidence package → Meterless World Model event → frontend evidence panel`. A request supplies a dataset ID, fictional participant ID, 84-day date range, exact plan ID/hash, six numeric series with explicit nulls and source record IDs. The response should preserve the Discovery family ID, engine version, baseline commit, policy hash, declared family size, signal ID, r/CI/N/p/q, temporal and robustness states, classification, and quality flags. World Model and UI may summarize only those returned fields, with explicit abstention when evidence is insufficient. Synthetic provenance must remain visible. PR #13 remains a runnable fallback until the adapter and UI consume this contract and pass end-to-end tests.

**Review gates:** this Draft PR proposes the generator, plans, validation harness, and evidence record only. The rights/IP and license approval for any private PHIS source remains with the owner under PR #15/#16. No private Discovery module is published here. No merge, deployment, paid service, or real health data is part of this work.

