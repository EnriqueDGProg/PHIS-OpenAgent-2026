# PHIS Discovery P0 scientific feasibility — 2026-10-23

**Status:** bounded feasibility audit; no source extraction or product implementation. **Recommendation:** **NO-GO for public extraction now; conditional GO for a five-file extraction after the owner grants explicit rights/IP approval and reviews the manifest below.** The present RC remains a descriptive two-variable product. This report does not certify a v2 scientific finding.

## Scope and provenance

- Private source: `EnriqueDGProg/PHIS`, cited baseline commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0` (2026-10-13). The available private checkout had HEAD `7de5eca7d13d276931e39c66667e3977e597ac35`.
- Public reference: RC Draft PR #13 at `ee117c0fc8ebab543f2fd62b40a9f5471de662b2`; founder-approved **design**, Draft PR #14, `docs/PRODUCT_DIRECTION_V2_2026-10-23.md`. This PR is independent of both and targets the PR #13 branch.
- Baseline Git blobs of all seven inspected Discovery modules were compared to checkout files after CRLF normalization: **identical**. The selected signal, extension, v1.1, integrity, and ingestion test files were also identical. The three selected v1.2 multivariable test methods were identical, although their containing test file had other changes. `discovery.py` and `discovery_summary.py` differed, so integration tests using those are **checkout regression evidence**, not a claim that the entire baseline tree was executed exactly.
- Inspection used Git object reads and local test execution. No private source, reports, database, credentials, or observations were copied to the public repository. Test temporary files were removed.

## Result ledger

Run from `C:\Users\ediaz\Documents\AI-Venture\PHIS\components\phis_master` with Python 3.12. The successful runs used this PowerShell setup (an isolated writable directory outside both Git repositories):

```powershell
$testTemp='C:\Users\ediaz\.codex\visualizations\2026\10\23\01a167e5-069b-7d93-9653-7e1d4315674a\.tmp-phis-discovery'
New-Item -ItemType Directory -Force -Path $testTemp | Out-Null
$env:TEMP=$testTemp; $env:TMP=$testTemp; $env:TMPDIR=$testTemp
$env:PYTHONPATH='src'
```

| Exact command after setup | Actual result | Wall time |
| --- | --- | ---: |
| `python -m unittest discover -s tests -p 'test_discovery_signals.py' -q` | **PASS**, 12 tests, exit 0 | 46.84 s |
| `python -m unittest discover -s tests -p 'test_discovery_extensions.py' -q` | **PASS**, 15 tests, exit 0 | 179.26 s |
| `python -m unittest discover -s tests -p 'test_discovery_v11.py' -q` | **PASS**, 13 tests, exit 0 | 103.04 s |
| `python -m unittest discover -s tests -p 'test_integrity_gate.py' -q` | **PASS**, 29 tests, exit 0 | 230.70 s |
| `python -m unittest discover -s tests -p 'test_ingestion_integrity.py' -q` | **PASS**, 23 tests, exit 0 | 1.96 s |

Three selected v1.2 multivariable tests also **PASS** (3 tests, exit 0, 7.79 s). Their exact command used `$env:PYTHONPATH='src;tests'` with the same external `TEMP/TMP/TMPDIR`:

```powershell
python -m unittest -q test_discovery_v12.DiscoveryV12Test.test_multivariable_conditional_effect_and_order_invariance test_discovery_v12.DiscoveryV12Test.test_collinear_and_trending_models_abstain test_discovery_v12.DiscoveryV12Test.test_multivariable_null_never_promotes
```

**Total selected PASS: 95 tests.** The first `test_integrity_gate.py` run with Python's default sandbox temp directory ended `FAILED (errors=58)` across 29 tests due to `WinError 5` creating/removing temporary files. A broad `test_discovery*.py -v` run was interrupted after the same setup error; it has **no suite PASS/FAIL conclusion**. With temp placed inside the public Git checkout, integrity ran 29 tests and ended with one `discovery_output_must_be_outside_git_repository` error; a v1.1 run using that location was interrupted without a conclusion. Moving temp outside both repositories yielded the PASS results above. These are **environment setup failures**, not observed failed scientific assertions. No full broad Discovery suite PASS is claimed.

## Static import closure, runtime and ownership

A full AST walk of imports in the seven baseline files, including function-local imports, found no `__import__`, `eval`, or `exec` calls. The file-level closure for `search_v11` is:

```text
discovery_v11
  -> discovery_features
  -> discovery_signals -> discovery_features
                       -> discovery_shapes (function-local)
                            -> discovery_features + discovery_signals
  -> discovery_temporal -> discovery_features + discovery_signals + discovery_shapes
```

`discovery_validation` imports features, signals and v11; it supplies version comparison and walk-forward validation, not a required live search import. `discovery_multivariable` imports features, signals and temporal; it is review-only and not a required live search import. The shapes/signals reciprocal edge is function-local on the signals side; the selected tests exercised these imports successfully. The closure uses only Python standard library modules (`collections`, `copy`, `dataclasses`, `datetime`, `hashlib`, `json`, `math`, `random`, `statistics`). The private package declares Python >=3.11, no runtime dependencies, and setuptools for building. A minimal new package initializer and the public project's packaging will still require a cold-clone import check.

No `LICENSE`, `COPYING`, or `components/phis_master/LICENSE` existed at the cited baseline. Absence of a license is **not a reuse grant**. Owner must confirm copyright, contributors, third-party obligations and public license selection before any blob is moved. Private `discovery.py`, registry, nutrition, SQLite, projection, owner runner and real-data paths are excluded. The old frozen `energy.json` plan is excluded: it declares sleep, steps, HRV, heart rate and respiratory rate, not the proposed caffeine/exercise/stress scenario. Its baseline blob is `1b56c80e7f46ca52cc750f74b99bc9ee36f813c0`; it is provenance evidence only.

## Exact minimum candidate manifest — **do not copy until approved**

These five pre-existing PHIS files are the smallest **file-level** runtime set for authentic v1.1 search. Paths are relative to the private baseline; hashes are Git blob IDs at commit `516e3388...`.

| Private path under `components/phis_master/src/phis_master/` | Git blob | Purpose |
| --- | --- | --- |
| `discovery_features.py` | `add62ef0fe925ac264a1c87672ae2feb56cb235b` | Calendar, digest, lag-one and preparation/quality primitives |
| `discovery_signals.py` | `94a30eac8ff670653c764f949b32df7e7730849c` | Search policy, pairwise effects, block resampling and corrections |
| `discovery_shapes.py` | `4d455ca190db0affa84e01e6741a1b4478000289` | Extended results and block sensitivity used by signals |
| `discovery_temporal.py` | `b3beede8c1ad0f804b29e47b73f5205e86a21694` | Frozen temporal diagnostics and first differences |
| `discovery_v11.py` | `92ad6ebc98274eb51832426ed6993962963f2aac` | Route handling and fixed-family hierarchical correction |

**Inspected, excluded from the P0 live manifest:** `discovery_validation.py` blob `4df1fea7a19258af528dd1ba324a862329c5f75a` (offline validation only); `discovery_multivariable.py` blob `c336edbb8b5123edd7bf03238ca6d8c07a756de2` (review-only and hardcodes pain/energy outcomes). The private `__init__.py` is not necessary to reuse: a new minimal public package initializer is hackathon work. The five blobs would remain clearly labeled **PREEXISTING PHIS** with commit/blob provenance; Zetaris adapter, v2 synthetic generator and declared plans, evidence API, caching, Meterless event schema, tests and frontend are **NEW hackathon-window work**. No copied code is in this PR.

## Scientific fit for a fictional 84-day energy/sleep investigation

| Question | Existing baseline capability | Limit for v2 |
| --- | --- | --- |
| Daily coverage and missingness | `Variable` validation and `quality` report valid days, gaps, duplicates, source changes and freshness; missing is not zero. | New Zetaris-to-daily adapter must enforce units, dates, uniqueness, provenance and allowed synthetic source IDs. |
| Pairwise energy/sleep factors | `search_v11` accepts numeric series and predeclared exposure/outcome pairs, including `sleep_hours -> energy_central` and a proposed sleep outcome. | Caffeine timing, exercise load and stress are **not** certified private variables or plans. Define their semantics, units and timing as new work. Clock hour needs a predeclared late-caffeine encoding; arbitrary "exercise load" is not medically validated by this code. |
| Temporal order and robustness | Predeclared calendar lags, levels/first-difference routes, temporal diagnostics, reverse-direction warning, half stability, trimming and block-length sensitivity exist. | A lag is a calendar alignment, not causal identification. Overnight sleep date and caffeine date must be specified; no claim of mediation or direction can follow from lag alone. |
| Effect, CI, multiple tests | Pairwise correlation effect, 95% paired circular-block bootstrap CI, exploratory block-permutation p, BY correction and v1.1 parent Bonferroni/BY hierarchy exist. Untestable children remain in the declared family at p=1. | Retain all planned children and denominator even when exposure rows are blocked. CI may be null when resampling completeness fails. Do not manufacture numerical confidence or a causal effect. |
| Confounding | Temporal warnings and interaction/shape checks exist. `analyze_models` gives 2–3 predictor standardized betas, block-bootstrap CIs, collinearity/VIF and residual diagnostics. | Multivariable results are explicitly `exploratory_review_only`, with no multiplicity-based promotion; outcomes are hardcoded to pain/energy. P0 pairwise findings must state stress may confound. A sleep multivariable review requires new implementation and validation. |
| Negative control | A numeric control can be a predeclared pair in the same fixed family. | Control construction, null expectations and blind acceptance test are **new**; absence of a signal is not proof of no effect. Never silently drop it from correction or promote a favorable subset. |
| Replication | `discovery_validation` can do held-out walk-forward checks offline. | One 84-day person does not give independent replication; overlapping windows and an in-sample holdout cannot be labeled external confirmation. |

At 84 days, the default search floor of 70% paired coverage requires at least **59 aligned days**, plus `min_n=30`, approximate effective N >=20, minimum group sizes 15 and temporal/resampling checks. Passing sample count alone does not imply a candidate. Conservative abstention is a valid demo outcome. No synthetic v2 dataset or blind discovery run exists yet, so whether any proposed factor will actually qualify is **unverified**.

## Bounded deterministic demo configuration (proposal, not measured)

Create two **new predeclared** families before generating or inspecting findings: energy outcome with sleep duration, exercise load, stress and one unrelated control; sleep outcome with late caffeine, exercise load, stress and the control. Per family: linear method, 1-day exposure window, lags 0/1, levels and first differences, fixed seed, 999 resamples, 7-day primary blocks and existing 3/7/14-day sensitivity blocks. This is 4 pairs x 2 lags x 2 routes = **16 declared children per family**, below the engine's 64-child bound. Retain the baseline policy floors (`min_n=30`, effective N >=20, coverage >=0.7, |r| >=0.3, adjusted q <=0.05). Do not lower gates to force a finding. If the control must be outside the candidate list, it still remains in the tested family and evidence record.

This configuration entails at least 32 x 999 bootstrap/permutation attempts plus extended sensitivity work. The suite wall times above are **test times, not per-investigation latency**. No honest live latency estimate exists yet. Next implementation must benchmark a cold 84-day run on the demo machine, enforce one bounded run per verified row/plan digest with a timeout and explicit failure status, and optionally reuse deterministic evidence keyed by that digest after a fresh Zetaris readback. No paid service is required for Discovery.

## Minimum integration contract (new work)

1. **Zetaris readback → canonical observations.** Accept only allowlisted fictional participant, Europe/Madrid ISO day, named variable, finite value or explicit missing, unit, source type and stable `SYN-` record ID; reject duplicates/invalid units/out-of-window rows. Record query ID, request ID, SQL hash, dataset version and complete source-ID set. The RC currently verifies the original 156 energy/sleep rows against its generator with `LIMIT 200`; v2's additional variables require a new bounded/paginated verifier and cannot pass through that unchanged. No silent local fallback in live mode.
2. **Deterministic Discovery tool.** Request: `run_id`, source-proof digest, fixed `plan_id` and version, `as_of`, family, bounded calendar and seed. Build full 84-day arrays with `None` for missing, run the declared v1.1 family unchanged, and derive each result's cited source IDs from its actual paired dates/lag/window. Reject arbitrary SQL, caller-supplied search grids and future access.
3. **Evidence package.** Return `PASS | EXECUTED_PARTIAL | INSUFFICIENT_DATA | BLOCKED | ERROR`; observed trend separately from association; full family/child IDs and policy hashes; computed r, CI, p/q, N, coverage, temporal/sensitivity flags and missing/blocked reasons, using null where unavailable. Include exact source IDs and Zetaris proof. A classification is emitted only by deterministic code. No LLM generated measurements or causal claims.
4. **Meterless World Model → follow-up.** Store a compact verified evidence ID/digest, status, question scope and source/proof IDs, then read it through the official Engine before choosing the next bounded tool. The RC event schema only has `energy_comparison` and `agent_state`; a new validated event kind/schema is required. Do not store raw health rows or present the Engine as Runtime inference.
5. **Frontend.** Render supported finding or specific insufficiency first; show candidate contributors only where classification permits, with methods, units, N, CI, correction, temporal cautions and source lineage in the evidence drawer. Preserve synthetic disclosure and no medical advice.

## Blockers and sequence

**B1 — rights/IP (hard blocker):** owner approves exact five blobs, public license and pre-existing-code attribution; no inferred permission from the private repo. **B2 — baseline equivalence:** cold-clone import plus golden synthetic equivalence after approved extraction; available checkout integration tests do not certify an extracted public package. **B3 — v2 data:** independent fictional generator, semantics, source proofs, missingness and negative-control tests; current Zetaris verifier/query cap is v1-specific. **B4 — scientific:** predeclare families, blind null/confounding/lag tests, show no promotion on weak evidence; review-only multivariable must not become adjusted headline. **B5 — runtime:** measure cold analysis cost and enforce bounded execution. **B6 — product:** new evidence and Meterless schemas, English accessible UI and actual end-to-end proof.

Implementation order after B1 approval: (1) approved five-file extraction with provenance and isolated import/golden tests; (2) new synthetic v2 dataset/semantics and predeclared plans, blind scientific controls; (3) bounded verified Zetaris adapter and Discovery evidence tool; (4) new Engine evidence event and changed follow-up decision; (5) evidence-first frontend and cold-start/live verification. Merge, deployment, private-data use and final submission remain owner-controlled.

**Decision:** **GO** for design and this report. **NO-GO** for extracting/publishing private Discovery source today. Once B1 is explicitly cleared, the five-file set is a technically plausible minimum for *pairwise exploratory* energy/sleep analysis; extraction itself must still pass B2–B5 before any scientific claim or live demo acceptance.
