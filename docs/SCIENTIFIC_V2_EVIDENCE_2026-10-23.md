# Scientific v2 integration: synthetic case and execution evidence

**Status: partial integration, not judge-ready.** This branch starts at PR #13 and leaves its `investigation.v1` route intact. `analysis_version: "v2"` or `?analysis=v2` explicitly selects the new route. No merge, deployment, private PHIS source publication, real health data, paid service or sponsor claim based on a mock occurred.

Sources: [product direction PR #14](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/14), [Discovery feasibility PR #15](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/15), [local-only preparation PR #16](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/16), [scenario PR #17](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/17), [founder issue #1 refinement](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/issues/1), and fallback [PR #13](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/13). Original private baseline: `516e3388ce67061028c1b1b29afb4a4ed965a2e0`. The approved five private modules were loaded from an isolated local package during tests. Their source is absent from this branch.

## Synthetic Case Design & Anti-Cheating Appendix

The 84 local dates run 2026-07-30 through 2026-10-21 for `fictional-001`. There are 504 date-variable slots: energy score/10, sleep hours assigned to waking date, late caffeine after 14:00 local, exercise load, stress score and an unrelated count. Each slot has a stable synthetic ID, source type, unit, explicit observed/quality state and a nullable value. Source validation rejects incomplete grids, duplicate slots, wrong units, non-fictional participants, non-finite/out-of-range values and missing values silently converted to zero. It verifies the source schema and canonical digest; it does **not** compare queried values with the local generator or use simulation equations to write an answer.

PR #17 revision 1 showed energy means 6.579/6.058/6.001 across consecutive 28-day windows. The latest-versus-middle difference was only −0.056. Its sleep–energy r=+.869 may look unusually neat, and fixed-sample lag-1 energy/stress correlations were +.018/+.044. The [dated preregistration](SCENARIO_REVISION_PREREG_2026-10-23.md) was committed before revision 2 was evaluated. One generator-only revision introduced modest serial dependence, a recent stress/caffeine shift, reduced sleep's deterministic energy coefficient and increased independent noise. Seed remains `20261023`. Negative control and missingness streams remain independent. Dataset/source IDs changed to `PHIS-SYN-84D-v2r2`/`SYN-V2R2-*`. No further generator tuning was performed after the evaluation.

Simulated mechanisms are **design facts**, not measured findings: current stress affects late caffeine and energy; prior caffeine, stress and exercise affect the following sleep; sleep, current stress and prior exercise affect energy. Weekday training/stress variation, bounded Gaussian noise, persistence, ~5–7% missingness and a two-day sleep logging gap are present. These mechanisms are visible in the offline generator for judge inspection, but `scenario_contract_v2.py`, `zetaris_v2.py`, `discovery_adapter_v2.py` and `scientific_v2.py` do not import them on the live source path. Confounding and shared trends remain deliberately possible.

Revision 2 observed counts: energy 80/84, sleep 78/84, caffeine 83/84, exercise 79/84, stress 80/84, negative control 79/84. Energy min/max 3.636/8.330, sleep 5.623/8.418 hours; lag-1 energy +.461, sleep +.368, stress +.494. First/middle/final 28-day **observed** means: energy 6.808/6.129/5.390; sleep 7.327/7.174/6.605 hours; late caffeine .333/.357/.786; stress 3.943/4.363/4.935. Latest-minus-middle energy is **−.739**, inside the preregistered −.80 to −.25 goal. Sleep is **−.569 hours**, narrowly outside the preregistered −.55 to −.15 goal: **FAIL**. High recent late-caffeine frequency is a scenario limitation. These observed means have no inferential interval or causal interpretation.

Generator SHA-256: `577139be73d3a59b484673cc49e4bbf7fa6a3780633306ed0ad28aefdd5ddadb`. Canonical normalized-record digest: `926f2e88d43f699d53845a8fbe79e847147a26318c62a317abc20bd0e58b258c`. The synthetic CSV export produced 504 rows, file SHA-256 `ba039b9b124c08a4af372a437a969eb0f4d9be00bef1b29831ca061cc30b703a` and the same normalized-record digest; that CSV stayed outside the public worktree. `.gitattributes` pins LF checkout for the byte-hashed generator and plans, including on Windows.

## Frozen Discovery analysis and measured results

The PR #17 scientific grid and thresholds did not change: four predeclared exposures per family, lags 0/1, levels plus adjacent-calendar first differences, linear method, one-day window, 999 block resamples, 3/7/14-day sensitivity, minimum raw N 30, effective N 20, coverage .70, |r| .30, BY q .05 and group N 15. Each family keeps all 16 children including the negative control and untestable children. First differences are review-only. The plan JSON dataset ID changed to v2r2; the scientific policy and pairs did not.

| Family | Frozen plan SHA-256 | Discovery family ID | Classes |
| --- | --- | --- | --- |
| Energy | `02b7495e68c577170335d7403f777ecb3105dc6857b07baf538493a2fccf235a` | `1025cf49f6e372f8706899b96aa3022765eb59a82081b8cbf57a863adc67080b` | 0 candidate, 5 unstable, 11 weak |
| Sleep | `864844abbafc9c0743f4f6e9a82b560c8f86276ee45c537617fa1a0fb7299b44` | `ea0865e75de0339dc5009c88439994945993c3ba3e77c8972ff5aad703ba1e39` | 0 candidate, 3 unstable, 13 weak |

Selected **levels** results from authentic local PHIS Discovery v1.1 follow. CIs are the engine's 95% resampling intervals. `q child/parent` is the worst-block selection correction, with Bonferroni within parent and BY across parents/children; the primary child BY is shown separately. These controls are exploratory, not global selective child FDR.

| Family / exposure, lag | r [95% CI] | Raw N | Primary p / child q | Selection p / child q / parent q | Temporal / 3-7-14 blocks | Engine class |
| --- | --- | --- | --- | --- | --- | --- |
| Energy / sleep, 0 | +.777 [.703, .842] | 74 | .001 / .0042 | .003 / .0125 / .1000 | incompatible / unstable | unstable_candidate |
| Energy / stress, 1 | −.501 [−.691, −.248] | 75 | .001 / .0083 | .008 / .0333 / .1167 | incompatible / unstable | unstable_candidate |
| Sleep / late caffeine, 1 | −.810 [−.858, −.755] | 76 | .001 / .0042 | .002 / .0083 / .0667 | incompatible / unstable | unstable_candidate |
| Sleep / stress, 1 | −.512 [−.663, −.292] | 73 | .001 / .0083 | .012 / .1000 / .2000 | caution / unstable | unstable_candidate |
| Energy / negative control, 0 | +.051 [−.197, .285] | 76 | .659 / 1.000 | .699 / 1.000 / 1.000 | incompatible / stable blocks | weak_candidate |
| Sleep / negative control, 0 | −.100 [−.321, .092] | 74 | .409 / 1.000 | .438 / 1.000 / 1.000 | caution / stable blocks | weak_candidate |

**Scientific acceptance FAIL:** no revision-2 factor passes the original promotion gates. The prominent raw sleep–energy and caffeine–sleep correlations cannot be called qualified contributors. Their common recent level shift is one plausible reason for temporal incompatibility; this is an inference about the diagnostic, not an adjusted causal finding. The baseline five-file package has no authorized multivariable-adjusted inference. The v2 answer therefore reports the measured energy change and says no tested contributor qualifies. It does not turn a designed mechanism into a finding.

Counterfactual checks on the same fixed plans: shuffling observed sleep reduced energy r from +.777 to +.062 (N 74, CI [−.154,.277], child/parent selection q=1/1, weak). Shuffling caffeine reduced next-day sleep r from −.810 to +.036 (N 76, CI [−.222,.290], q=1/1, weak). Reversing energy sign produced sleep–energy r=−.777 (N 74, CI [−.842,−.704], still unstable). Reducing sleep coverage to N=13 yielded `insufficient_data`, CI null and p/q=1 despite raw r=.861. Negative controls were not promoted. The derived-results checker passed these conditions without changing plans.

## Integration and provenance

`scenario_contract_v2.py` normalizes 504 slots without zero filling and hashes canonical records. `zetaris_v2.py` requests three bounded SQL pages (200/200/104 expected), requires a preflight, and rejects missing/extra/malformed rows; each page carries distinct real request/query IDs. `discovery_adapter_v2.py` pins both plan hashes, invokes only authentic local `search_v11`, retains all 16 results and verifies exact paired-source counts/IDs. The v2 agent ranks only engine-promoted candidates, separates unstable and weak hypotheses, and persists the validated family ID, plan and record digests plus candidate IDs and source-query IDs in the **official** Meterless World Model Engine. A later generic follow-up reads the persisted event and selects the other predeclared family. No LLM writes measurements, p values, confidence intervals or conclusions. PR #13 remains the default API/UI route.

The localhost HTTP smoke used actual Python HTTP, local authentic Discovery and official Engine persistence/readback. Energy run `SYN-RUN-4e214a23e40f` recorded PHIS event digest `3a8ca3202bb5e03a15393d3e52855a282f3f45a64f1385ecaa7eca558f2bbb44` with Engine receipt `evt_4`; persisted evidence selected the sleep family for follow-up `SYN-RUN-9a0d1df32d08`, whose PHIS event digest was `95618a0f94b80b12e5dff8f39e96e976786fe67aaa995b8bc1e3a9c30e3d1c91` with Engine receipt `evt_10`. Both returned 16 children and the same canonical source digest. Those IDs are **local synthetic Engine proof**, not Zetaris proof.

## Commands and gate results

Environment: Python 3.12.10, Node 24.19.0. Set `PHIS_PRIVATE_SRC` to the approved local-only five-file package's `src` directory outside the public checkout. The exact local path is intentionally excluded from publication. No package install is required.

```powershell
$env:PYTHONPATH = "src;$env:PHIS_PRIVATE_SRC"
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
$env:WORLD_MODEL_IMPL = (Resolve-Path 'vendor\meterless-world-model\src\index.ts').Path
node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts
python scripts/scientific_http_smoke.py
$SyntheticCsv = Join-Path $env:TEMP 'phis-v2-synthetic-new.csv'
python scripts/export_scenario_v2.py $SyntheticCsv
python scripts/validate_scenario_v2.py --mode baseline > baseline.local.json
python scripts/validate_scenario_v2.py --mode ablate > ablate.local.json
python scripts/validate_scenario_v2.py --mode reverse > reverse.local.json
python scripts/validate_scenario_v2.py --mode low-coverage > low-coverage.local.json
python scripts/check_scenario_v2_results.py baseline.local.json ablate.local.json reverse.local.json low-coverage.local.json
```

| Gate | Actual result |
| --- | --- |
| Existing plus new Python tests with local Discovery | **PASS 70/70** |
| Frontend client tests | **PASS 11/11** |
| Official Meterless World Model conformance | **PASS 8/8** with required `WORLD_MODEL_IMPL`; first attempt without it was an environment-setup failure, not an engine test failure |
| Actual localhost HTTP → Discovery → official Engine, then follow-up read | **PASS**, proof IDs above; Zetaris explicitly NOT_CONNECTED |
| Fixed-seed revised Discovery families and perturbation checker | **PASS execution** 16+16 children and perturbation checks; **FAIL scientific promotion** 0 candidate in both families |
| Preregistered latest sleep mean change | **FAIL** −.569 h, .019 h beyond lower bound |
| Public branch without private package | **PASS fail-closed**: five source-contract tests pass, one engine test skips, and a v2 request returns `BLOCKED` with no scientific package. |
| Real local Zetaris 504-slot HTTP query and distinct sponsor IDs | **BLOCKED**: Docker client exists but daemon pipe is absent; `ZETARIS_REST_URL`, `ZETARIS_ORG_ID` and `ZETARIS_API_KEY` are unset in the execution environment. Injected-transport 200/200/104 pagination tests pass but are not sponsor proof. |
| Private Discovery public packaging and clean-clone scientific operation | **BLOCKED** by owner rights/IP/license gate in PR #15/#16; clean clone retains runnable PR #13 fallback, while v2 abstains without the local private package. |
| Judge-ready supported contributor to recent change | **FAIL** under frozen scientific gates; no causal or adjusted claim. |

Next live step: start an authorized local Zetaris daemon/service, provide its direct REST URL/org ID/API key securely, export and stage the fictional v2 CSV server-side, register the table using the documented SQL path, then run the v2 HTTP route in `LIVE_SYNTHETIC_ZETARIS` mode and capture its **actual** three request/query IDs and Engine receipt. Do not substitute injected transport or generator rows when live mode is requested. Owner review is required before any private Discovery source publication or merge.
