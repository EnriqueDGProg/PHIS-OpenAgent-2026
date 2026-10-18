# Discovery Dependency and Test Gate — 2026-10-18

Status: architecture and verification plan only. No implementation, source copy, tests or deployment executed.

## Source baseline
The PHIS main branch was inspected at commit 516e3388ce67061028c1b1b29afb4a4ed965a2e0, dated 2026-10-13. Recursive tree listing returned truncated=false. This commit is the source-of-truth candidate for later provenance.

## Discovery dependency map
Under components/phis_master/src/phis_master:
- discovery_features.py: Variable, digest, calendar, prepare, quality, features; standard Python library imports observed.
- discovery_signals.py: SearchPolicy, search, correlation, adjusted_pvalues, resampling; imports discovery_features.
- discovery_shapes.py: ranks, shape_resampling, extended_results; imports discovery_features and discovery_signals.
- discovery_temporal.py: TemporalPolicy, diagnose, pair_diagnostic; imports features, signals and shapes.
- discovery_v11.py: search_v11, dual_correction, apply_hierarchy; imports features, signals and temporal. This module and discovery_shapes were missing from the earlier extraction shortlist and are needed for the complete v1.1 scientific behavior.
- discovery_validation.py: analyze, compare_versions, walk_forward; depends on v11, features and signals.
- discovery_multivariable.py: analyze_models; depends on features, signals and temporal. P1.
- discovery.py: build_foundation, run_foundation; depends on private orchestration, projections, nutrition, registry and statistics. Do not copy as-is.
- discovery_nutrition.py: depends on nutrition_estimates, signals and temporal; defer.
- discovery_registry.py, discovery_product.py and discovery_product_report.py: local execution/reporting, not first-pass public core.
- cloud_projection.py and tools/discovery_private_run.py: private runtime integrations and refresh dependencies, exclude.
- components/phis_master/discovery_plans/energy.json: frozen five-exposure energy plan; preserve correction/test family.

These are checked top-level import links, not certified transitive function-local or dynamic imports. The core package pyproject.toml declares Python >=3.11, no runtime dependencies, setuptools build backend.

## Verified test filenames
Under components/phis_master/tests:
test_discovery_adversarial.py
test_discovery_capture.py
test_discovery_extensions.py
test_discovery_foundation.py
test_discovery_operational.py
test_discovery_product.py
test_discovery_product_hardening.py
test_discovery_registry.py
test_discovery_signals.py
test_discovery_v11.py
test_discovery_v12.py
test_integrity_gate.py
test_ingestion_integrity.py

The inspected test_discovery_signals.py, test_discovery_v12.py and test_discovery_product_hardening.py import unittest.

Candidate command from components/phis_master with PYTHONPATH set to src:
python -m unittest discover -s tests -p 'test_discovery*.py' -v
python -m unittest discover -s tests -p 'test_integrity_gate.py' -v
python -m unittest discover -s tests -p 'test_ingestion_integrity.py' -v
These commands were inferred from test layout and have NOT been run or validated today. No independent PASS is claimed.

## Design-only JSON contracts
Canonical observation fields: schema_version, participant_id (fictional), local_date (ISO), variable (allowlist), value (number or null), unit, source_type, observed boolean, quality, source_record_id. Missing is never zero.

Request envelope fields: contract, run_id, tool, args. Tool allowlist: get_variable_coverage, get_longitudinal_trend, compare_periods, run_predeclared_discovery, get_evidence_package. Argument allowlist includes participant_id, variables, date bounds and as_of. Reject arbitrary SQL and out-of-bounds/future dates.

Evidence response envelope: contract, status (PASS / EXECUTED_PARTIAL / BLOCKED / INSUFFICIENT_DATA), finding_type (observation / association / hypothesis), run_id, data_window, coverage with numerator/denominator, statistical_result or null, source_record_ids, warnings, trace_ids. Actual statistical result includes effect, CI, N, correction family and temporal diagnostics when computed. These are design contracts, not working endpoints.

## Synthetic acceptance fixtures (specification only)
A: seeded fictional timeline at least 84 Madrid calendar days with 28-day energy change and recorded data sources; show trend without asserting causation.
B: low-N/all-missing records, abstain and never impute zeros.
C: blocked exposure amid valid others; execute partial unchanged predeclared family and BY/Bonferroni denominator.
D: temporal confounding / coverage drift; preserve caution.
E: repeat and paraphrase; stable tool-mediated evidence and no false independent replication.
No private observations may be used as a fixture source, and no statistical outputs are predeclared without an original engine run.

## Gates
Pre-extraction: source reuse/ownership approval; complete imports including local-function imports; exact baseline; real test execution; independent secret/data boundary audit.
Post-window: approved minimal extraction, regression equivalence on synthetic data, complete provenance manifest, sponsor real-call traces, cold start without private dependencies, human review before merge.
Status: GO planning; NO-GO public source extraction or feature implementation before allowed 22 October window.

## Next
Design the end-to-end interaction and visual UI states from the JSON contracts; verify binding official rule and account access on 21 October, then authorize bounded worker packets only after gates.
