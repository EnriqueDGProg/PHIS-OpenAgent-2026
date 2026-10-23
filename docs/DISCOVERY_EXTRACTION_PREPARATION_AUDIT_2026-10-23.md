# PHIS Discovery P0 extraction preparation audit — 2026-10-23

**Publication status: HOLD.** Owner authorization in [PR #15's 2026-10-23 comment](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/15#issuecomment-6361765874) permits strictly local preparation of the five named baseline modules, but explicitly withholds approval to publish their contents. This PR publishes **only this English audit report**. No source file, package archive, harness, health data, secret, merge or deployment was pushed. RC PR #13 and product PR #14 were not modified.

## Local preparation and provenance

A new untracked local directory was created **outside both the public and private Git repositories**. It contains only the five approved PHIS baseline Python modules, a new minimal package initializer, new packaging metadata and synthetic-only test/build harnesses. Git reported that directory was not a repository. The isolated source remains local for owner inspection; its exact path is provided privately in the task response.

Each copied byte stream was read from private Git commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0`, checked against the PR #15 blob manifest before writing, and compared byte-for-byte after writing:

| PREEXISTING PHIS file | Expected and observed Git blob | Result |
| --- | --- | --- |
| `discovery_features.py` | `add62ef0fe925ac264a1c87672ae2feb56cb235b` | PASS |
| `discovery_signals.py` | `94a30eac8ff670653c764f949b32df7e7730849c` | PASS |
| `discovery_shapes.py` | `4d455ca190db0affa84e01e6741a1b4478000289` | PASS |
| `discovery_temporal.py` | `b3beede8c1ad0f804b29e47b73f5205e86a21694` | PASS |
| `discovery_v11.py` | `92ad6ebc98274eb51832426ed6993962963f2aac` | PASS |

There are **no other private source files** in the package. The new `__init__.py`, `pyproject.toml`, build helper and harness are **NEW hackathon preparation**, not represented as pre-existing PHIS. The private `__init__.py`, `discovery_validation.py`, `discovery_multivariable.py`, private runner, database and plan were not copied.

## PASS / FAIL / BLOCKED ledger

All tests used Python **3.12.10** and only fictional synthetic data. The source-package and archive runs set `PYTHONPATH` to the local preparation `src` directory or its local zip archive, respectively; original test files were loaded read-only from private `components/phis_master/tests`. Temporary output was placed in the same local untracked preparation directory, outside both repositories.

| Check / exact command | Result and interpretation |
| --- | --- |
| Source import: `python -c "import phis_master.discovery_v11 as m; print(m.__file__)"` with local `src` on `PYTHONPATH` | **PASS**; resolved to the isolated package, not the private checkout. |
| `python -m compileall -q src/phis_master` | **PASS**, exit 0. |
| `python -m unittest discover -s <private-tests> -p 'test_discovery_signals.py' -q` | **PASS**, 12/12 against local source; **PASS**, 12/12 again against local zipimport archive. |
| `python -m unittest discover -s <private-tests> -p 'test_discovery_extensions.py' -q` | **PASS**, 15/15 against local source; **PASS**, 15/15 again against local zipimport archive. |
| `python compare_golden.py` | **PASS**; baseline checkout, isolated source and isolated archive returned byte-identical canonical result JSON for two synthetic 84-day cases. Signal case: 12 declared children, 8 weak candidates / 4 insufficient; SHA-256 `00bf940a3b2bbfebc77c879462967372fc908d34691d6be926d6f4a3b1d08308`. Sparse case: 4 children, all insufficient; SHA-256 `c6234e10da3f4e3c73c1a498a5eafb8526753fdf6cbb711be0d9979289d3cf43`. These are compatibility checks, not evidence of an actual v2 finding. |
| `python build_zip.py` | **PASS**; local importable archive has exactly six entries (five manifest files and NEW initializer), each byte-identical to local package. Archive SHA-256 `0019a00f16ed5a30efaf03859774941dceaac782d460ebff0ba09079b6c656ad`. Archive remains local and unpublished. |
| `python -m unittest discover -s <private-tests> -p 'test_discovery_v11.py' -q` against isolated package | **BLOCKED at test import**, exit 1: original test module imports excluded `phis_master.discovery_validation`. This is a test-harness dependency, not a failed v1.1 scientific assertion. The private-checkout v1.1 suite passed 13/13 in PR #15; the isolated v1.1 behavior was checked by golden equivalence here. |
| `python -m pip wheel . --no-deps --no-build-isolation --no-index -w dist` | **BLOCKED at packaging metadata**, exit 1: this host lacks `setuptools.build_meta` and `wheel`; no network or new dependency was used. The stdlib zipimport archive and tests passed, but an installable wheel remains unverified. |
| `python audit_scan.py` | **PASS for defined static checks**; five blob hashes, AST import closure and listed risk patterns were checked. This is not an independent legal provenance opinion or a full secret-scanning service. |

The static scan found **zero** credential-shape matches, email addresses, absolute private paths, database/export references, external URLs, third-party notices, and network/process/file-open patterns in the five files. Its AST walk found internal imports only among the five modules and standard-library imports only: `collections`, `copy`, `dataclasses`, `datetime`, `hashlib`, `json`, `math`, `random`, `statistics`. No external runtime package was found. The package declares Python >=3.11; it ran on 3.12.10, while Python 3.11 was unavailable for a lower-bound test. Git history showed two author display labels associated with one email identity. No license or copyright notice appeared in these five files. These observations support the owner's rights claim for preparation but do not replace owner review of third-party IP.

A single synthetic-only benchmark on this host used 84 days, four predeclared pairs per family, linear method, lags 0/1, two routes and 999 resamples: **2.758 s energy**, **2.222 s sleep**, 16 children each. These timings are local measurements, not a production SLA; both runs returned weak/insufficient classifications only. No thresholds were tuned for a desired answer.

## Attribution and license proposal — owner decision required

- Label the five exact baseline blobs **PREEXISTING PHIS Discovery**, cite private commit `516e3388...` and each blob ID in a public provenance/NOTICE document **only after owner publication approval**. Record any later edits and resulting public hashes separately; do not imply the algorithms were created during the competition window.
- Label the new initializer, packaging, synthetic generator, declared investigation plans, Zetaris adapter, evidence contract, Meterless event integration, UI and tests **NEW hackathon work**. Keep the local preparation harness and archive unpublished unless separately approved.
- **Proposal for review, not a license selection:** owner could grant the five modules for this public repository under MIT while retaining the private PHIS product separately, if the owner confirms exclusive rights and the legal copyright-holder name. The public repository presently has no root license; a coherent repo-level `LICENSE` and an explicit provenance/NOTICE entry would be needed. Preserve the separately licensed Meterless vendor code under its own license. The owner may choose another compatible license. Do not add SPDX headers or publish a license until the owner approves the exact text and rights scope.
- The static scan found no third-party notice or non-stdlib runtime import in the five files, and baseline Git history did not reveal a distinct second email identity. This cannot rule out uncredited code provenance; owner content and history review remains a publication gate.

## Bounded Zetaris → Discovery evidence API proposal (NEW work)

**Trusted boundary.** The public caller requests `family = energy | sleep`, a synthetic `run_id`, and an `as_of` within the frozen 84-day dataset. It cannot submit SQL, raw analytical rows, a search grid, model thresholds or a seed. A server-side Zetaris reader performs a fresh bounded, paginated read and retains request ID, query ID, SQL SHA-256, dataset version, row digest and source-ID set. It fails closed if source verification is incomplete; it never swaps in local fixture rows while claiming live Zetaris.

**Input limits.** One fictional participant; exactly 84 Europe/Madrid calendar dates; allowlist `energy_central`, `sleep_hours`, `late_caffeine`, `exercise_load`, `stress_score`, `unrelated_count`; at most one observation per date/variable and **504 rows total**. Missing is `None`, never zero. Reject nonfinite numbers, invalid units, duplicate IDs/date-variable pairs, future dates, unapproved source types and non-synthetic IDs. Define caffeine/sleep overnight alignment and exercise-load units before a plan is frozen. Fetch pages of at most 200 rows, at most three pages for this fixed dataset; verify row completeness and a canonical payload hash before analysis. The current RC's 156-row/`LIMIT 200` verifier must be revised for this contract.

**Deterministic tool call.** `run_predeclared_discovery(verified_batch, family, as_of)` selects a server-owned immutable plan: at most four pairs, two lags (0/1), one window, two routes, linear method, fixed seed, 999 resamples, and the original policy thresholds. This yields at most 16 declared children per family, below the engine's 64-child cap. Keep blocked children in the original correction family. Set a **30-second computation deadline** per family and return a typed error on timeout; benchmark and adjust the operational deadline on the final demo host without changing statistical gates. A cache may be keyed by verified row digest + plan/policy hash, but every live answer still requires a fresh Zetaris proof and a matching digest.

**Response envelope.** Return `schema_version`, `run_id`, `family`, `status` (`PASS`, `EXECUTED_PARTIAL`, `INSUFFICIENT_DATA`, `BLOCKED`, `ERROR`), `evidence_id`, `source_proof`, `plan_hash`, `policy_hash`, `data_window`, and a fixed list of all child results. Each child carries engine classification, exposure/outcome/lag/route, aligned N and coverage, effect estimate, 95% CI, raw and adjusted p/q where actually computed, temporal/sensitivity diagnostics, warnings, and **exact paired source IDs** reconstructed from the verified rows. Use null for unavailable statistics. Separate observed period change from association; never infer cause or create an LLM confidence number. Store only compact evidence IDs/status/proof in a new validated Meterless World Model event; the frontend may display statistics only from this package.

## Decision and remaining gates

**PASS — local preparation:** exact five blobs, isolated imports, selected original tests, synthetic golden equivalence, stdlib-only closure, defined static scans and measured bounded synthetic run. **BLOCKED — wheel:** build backend unavailable offline. **BLOCKED — broader isolated original v1.1 test module:** its test import requires a deliberately excluded module. Neither block is a failed scientific assertion.

**HOLD / NO-GO for public source publication.** Before any push of the five files or archive, the owner must inspect the local extracted contents and this scan, confirm copyright-holder and final license/NOTICE text, approve the exact five-blob scope, and accept the remaining package verification plan (including a wheel or other approved distribution check). Then an independent reviewer should confirm public diff contains no private data/extra modules, run clean-clone golden and scientific controls, and separately approve any merge/deployment. PR #13 remains the fallback. This report alone does not authorize publication.
