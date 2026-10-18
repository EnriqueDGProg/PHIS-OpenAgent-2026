# PHIS Discovery extraction audit — 2026-10-18
Status: PREBUILD DOCUMENTATION ONLY. No source extraction or implementation before official build window.

## Source inspection and limitations
Read-only authenticated inspection of private EnriqueDGProg/PHIS default branch, 2026-10-18. Source references below are file blob SHAs, NOT a single pinned repository commit; a repository baseline and exact suite inventory remain P0.

## Verified modules (private source paths)
| Path under components/phis_master/src/phis_master/ | Git blob SHA | Observed functions / classes | Dependency and extraction recommendation |
|---|---|---|---|
| discovery_features.py | add62ef0fe925ac264a1c87672ae2feb56cb235b | Variable, digest, calendar, lag1, prepare, quality, features | Standard-library imports observed. P0 PREEXISTING candidate, conditional on clearance |
| discovery_signals.py | 94a30eac8ff670653c764f949b32df7e7730849c | SearchPolicy, correlation, adjusted_pvalues, block_indices, resampling, exposure_series, search | Imports discovery_features. P0 PREEXISTING statistical candidate; preserve corrections |
| discovery_temporal.py | b3beede8c1ad0f804b29e47b73f5205e86a21694 | TemporalPolicy, differences, iqr, diagnose, pair_diagnostic | Imports discovery_features, discovery_signals, discovery_shapes (not yet inspected). P0 dependent on closure |
| discovery_multivariable.py | c336edbb8b5123edd7bf03238ca6d8c07a756de2 | validate_models, _solve, _fit, _percentile, _max_vif, analyze_models | Imports features/signals/temporal. P1 conditional, not hero-path blocker |
| discovery_nutrition.py | 62be3f20c3c033c4d07856cb5fa22a610935aef0 | load_recorded_nutrition, range_sensitivity | Imports nutrition_estimates, signals, temporal. DEFER; review-only and sensitive completeness semantics |
| nutrition_estimates.py | 86e284c95acb3e6711aa99ff47f7398b25508aad | _r, _day, build_estimate_context | Includes sqlite3 and canonical nutrition semantics. DEFER |
| discovery_registry.py | 057849424f02be14eb988ca4017706fa72bf7994 | private_directory, _run_record, append_run, registry_runs, history | Private run/output paths. EXCLUDE as-is; build independent sanitized run-trace service |
| discovery.py | b403a3673d5836d90fb92f16b3e2284a85a34566 | load_daily, build_foundation, run_foundation | Imports private SQLite opener, features, nutrition, registry, signals. Needs ADAPTED interface or NEW wrapper; cannot transplant unreviewed |
| cloud_projection.py | 42b44ddbf642282a38bb2430df9632ce2242c014 | open_read_only_database, build_cloud_projection, publish_cloud_projection, token_from_environment | Private projection, HTTP/publishing and nutrition deps. EXCLUDE; no direct private bridge |
| tools/discovery_private_run.py | b28d2cad7a4ece5ec4f251a8b1783d26ffeaace9 | private_file, config_from_file, summarize_gate, execute, main | Depends on PHIS refresh, registry, projection; private paths. EXCLUDE completely |
| discovery_plans/energy.json | 1b56c80e7f46ca52cc750f74b99bc9ee36f813c0 | Frozen five-exposure energy plan | P0 PREEXISTING plan, subject to source and reuse clearance |

## Verified direct dependency topology
energy plan -> discovery.py -> discovery_features, discovery_signals, discovery_nutrition, discovery_registry, cloud_projection.
discovery_signals -> discovery_features.
discovery_temporal -> discovery_features, discovery_signals, discovery_shapes.
discovery_multivariable -> features, signals, temporal.
discovery_nutrition -> nutrition_estimates, signals, temporal.
tools/discovery_private_run.py -> discovery, discovery_registry, cloud_projection, refresh.
This is a direct-import summary, NOT a complete transitive / function-local import closure.

## Science baseline from PHIS docs (documented, not rerun here)
docs/DISCOVERY_V12.md; docs/DISCOVERY_SCIENTIFIC_AUDIT_74.md; docs/CURRENT_STATE.md.
- Daily gate validates provenance, unit, range, coverage and freshness. Unrecorded days are unknown, not zero; nutrition associations review-only.
- Fixed energy plan: outcome energy_central; exposures sleep_hours, steps, hrv_avg_ms, heart_rate_avg_bpm, respiratory_rate_avg; routes levels/first_differences, lags 0/1/2, window 1, 999 resamples, block lengths 3/7/14.
- Blocked variables must remain represented in original hypothesis family/denominators (BY/Bonferroni). A partially executable family retains blocked children; no post-hoc selection of more favorable plans.
- Source audit documented max_q .05, min_abs_r .3, min_n 30, min_effective_n 20, coverage .7; caution and temporal diagnostics persist despite sufficient N.
- No diagnostic, autonomous treatment or causal inference.
- docs/CURRENT_STATE.md cites prior synthetic regression counts including Discovery 115, Data Integrity Gate 29 and PHIS Master 325, but THESE WERE NOT RERUN FOR THIS AUDIT.

## Exact-test and source-clearance gaps
Exact test filenames, invocation commands, source HEAD commit, full import closure (including discovery_shapes and any function-local imports), license/ownership grant for publishing, runtime dependency isolation and synthetic test outcomes remain UNVERIFIED. GitHub code search did not surface test files for attempted keywords; this is not evidence that tests are absent. Do not mark verification PASS before independently executing tests on pinned source.

## Safe reuse decision
P0 candidate: scientific pure logic in features + signals + temporal/shapes and frozen energy plan, only if owner-approved and scientifically equivalent tests PASS.
P0 NEW: Zetaris-to-canonical-synthetic-data adapter, allowlisted bounded discovery-tool facade, evidence package, run trace and UI.
P1: adapted discovery foundation runner only after dependency audit; multivariable secondary.
DEFER: nutrition, owner runner, private registry, refresh, cloud projection and real PHIS database.
No private health data, secret, production API endpoint, personal analytics or commit history may enter public repo.

## Risks and acceptance
R1 CRITICAL leakage: all public fixtures exclusively synthetic; scans and independent reviewer check.
R2 HIGH transitive imports/private SQLite: complete AST dependency map and clean stand-alone import test.
R3 HIGH statistical drift: frozen plan, identical correction denominators, missingness, temporal warnings and bootstrap; golden synthetic fixture compared to original.
R4 HIGH licensing/provenance: approved PREEXISTING/ADAPTED/NEW manifest per file with actual source commit and ownership.
R5 HIGH sponsor theater: prove real Zetaris SQL, NVIDIA model and meaningful Meterless read-after-write usage (if selected).
R6 HIGH false PASS: historic PHIS tests do not certify extracted public build.
R7 HIGH organizer eligibility answer and final rules pending.

## Worker instructions and GO/NO-GO
Before Oct 22, read-only audit may enumerate full dependency tree and tests, identify source commit and document fixture expectations; NO copying production/private source into public repo, no feature implementation.
On verified authorized build opening, bounded worker may extract ONLY cleared files into standalone public repo and provide per-file provenance and scientific golden tests; subsequent worker implements sponsor adapter and evidence-first orchestration.
GO for planning. NO-GO for extraction/merge/deployment until source clearance, official window, full tests, safe data boundary and sponsor access confirmed.

## Next work packet
Inventory full Discovery import closure and test locations, pin actual source commit, then finish synthetic fixture schema and acceptance test cases (planning only).
