# PHIS Discovery reproducibility and safe release gate — 2026-10-23

**Decision: BLOCKED for public source publication.** This branch contains a packaging gate, synthetic-only tests and release documentation. It contains none of the five private PHIS modules, no source archive, no health data and no selected repository license. The owner authorized local preparation in the [PR #15 comment](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/15#issuecomment-6361765874); that authorization explicitly withheld publication of the source contents. A Draft PR for this branch is therefore a review of the release mechanism only.

## Scope and source of truth

- [Official event page](https://hackathon.genai.works/event/open-agent-hackathon-2026): the build window opens **22 October 2026, 00:00 UTC**. The Wildcard description explicitly accepts an existing project extended with sponsor technology and scores new work rather than prior development. No statement on that page is a license grant for PHIS source. Record PREEXISTING and NEW work separately.
- Public functional reference: [RC PR #13](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/13). Scientific feasibility and first local package evidence: [PR #15](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/15) and [PR #16](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/16). [PR #18](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/18) adds NEW v2 scientific integration while leaving authentic Discovery import dependent on local preparation. [PR #20](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/20) is a NEW v3 direction specification; its benchmark is another worker's separate scope.
- Private baseline: `EnriqueDGProg/PHIS` commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0`, dated before the competition window. The five file contents remain private. The checked-out private HEAD was newer; the pinned commit, not HEAD, defines the candidate.

## Exact PREEXISTING manifest

Each path below is relative to private `components/phis_master/src/phis_master/` at the pinned commit. Git blob IDs are hashes of the original byte streams, not hashes of re-encoded text.

| Module | Original Git blob | File-level role |
| --- | --- | --- |
| `discovery_features.py` | `add62ef0fe925ac264a1c87672ae2feb56cb235b` | Calendar and quality primitives |
| `discovery_signals.py` | `94a30eac8ff670653c764f949b32df7e7730849c` | Pairwise search, resampling and correction |
| `discovery_shapes.py` | `4d455ca190db0affa84e01e6741a1b4478000289` | Shape and block sensitivity |
| `discovery_temporal.py` | `b3beede8c1ad0f804b29e47b73f5205e86a21694` | Temporal diagnostics |
| `discovery_v11.py` | `92ad6ebc98274eb51832426ed6993962963f2aac` | Frozen v1.1 search and fixed-family hierarchy |

The minimum import closure for `discovery_v11` is `v11 → features, signals, temporal`; `signals → features` and function-local `shapes`; `shapes → features, signals`; `temporal → features, signals, shapes`. The reciprocal signals/shapes edge is function-local and imported successfully in the selected tests. AST imports, including nested imports, use only `collections`, `copy`, `dataclasses`, `datetime`, `hashlib`, `json`, `math`, `random`, `statistics` and those four internal edges. No non-stdlib runtime dependency was found. Python **3.12.10** was tested; the declared lower bound **3.11** remains untested here. A prior private package metadata file declares `setuptools>=68` as a build dependency, which is distinct from runtime imports.

Excluded: private `discovery.py`, `discovery_validation.py`, `discovery_multivariable.py`, nutrition, registry, projection, runners, private `__init__.py`, frozen private plan, SQLite databases, reports and observations. The original v1.1 test module imports the excluded `discovery_validation`; its full isolated run remains blocked at collection. The five-file runtime closure does not imply that every original integration test can be copied or run unchanged.

## Independent verification on 23 October 2026

| Gate | Status | Evidence and limit |
| --- | --- | --- |
| Five local files against private commit | **PASS** | `git rev-parse <commit>:<path>` matched `git hash-object <local-file>` for all five manifest entries. No newline normalization was needed. |
| Package contents | **PASS** | Local source directory has exactly five private `.py` modules and a NEW initializer; generated cache files were ignored. A newly built local, unpublished archive contains exactly those five byte-identical files and a NEW initializer, SHA-256 `7509aa85192322eb8d6f233e562f68280fe4da13ff5fa574c78fbf77b0dc32d8`. The archive is outside all Git checkouts. |
| Import/dependency closure and static risk scan | **PASS for defined checks** | Original local `audit_scan.py` checked AST imports and patterns for credential shapes, email, absolute paths, database/export paths, URLs, third-party notices, network/process/file-open references; all five returned zero hits. The new public packaging gate independently enforces the pinned hashes, exact file set, import allowlist and risk patterns. A zero-hit scan cannot establish copyright ownership or rule out every secret. |
| Scientific regression | **PASS for selected checks** | `compare_golden.py` on two synthetic 84-day cases returned identical canonical JSON from local source and local archive: SHA-256 `00bf940a3b2bbfebc77c879462967372fc908d34691d6be926d6f4a3b1d08308` (12 children) and `c6234e10da3f4e3c73c1a498a5eafb8526753fdf6cbb711be0d9979289d3cf43` (4 children). Original `test_discovery_signals.py`: **12/12 PASS** against the local package. These are synthetic compatibility checks, not a clinical or v2 finding. |
| Packaging gate tests | **PASS with one platform skip** | `python -m unittest tests.test_package_discovery_candidate -v`: 5 passed, 1 symlink test skipped because Windows symlink creation was unavailable. Hash mismatch, extra module, Git-checkout source/output and absent private source fail closed. |
| Clean public clone without private package | **PASS, fail closed** | A fresh local clone of this four-file branch contained no `phis_master` source, private archive or SQLite file. The synthetic gate tests passed. Invoking the packager with clone-local `src/phis_master` returned exit **2** and produced no archive. |
| Installable wheel and Python 3.11 | **BLOCKED** | The local host lacked `setuptools.build_meta`/`wheel` for an offline wheel; no wheel or 3.11 runtime was verified. The local zipimport archive is importable but is not an installable wheel. |
| Rights and publication | **BLOCKED** | No license exists in the pinned private baseline or this public branch. Git history of the five paths showed two author display labels sharing one email identity. That does not establish exclusive rights or third-party provenance. The owner must confirm rights, exact scope, copyright holder and final license wording. |

No FAIL scientific assertion was observed in these bounded checks. PR #15 documents earlier temp-directory errors and the selected private baseline suite; those results should not be reported as isolated package passes. No broad v1.1 suite PASS is claimed.

## Public-safe packaging mechanism

`scripts/package_discovery_candidate.py` accepts a local module directory **outside every Git checkout**. It requires exactly the five pinned Git blobs, rejects extra modules and symlinks, scans imports and selected sensitive patterns, and writes a new deterministic six-entry `.zip` **outside every Git checkout**. It never fetches private source. The archive is an **unpublished candidate** and has no license grant. Its hash is evidence for review, not publication approval. The script deliberately emits no source text.

A clean public clone contains no `src/phis_master` private package. Running the script with that path fails before producing an archive. A source tree with any modified byte, additional Python module, changed import, sensitive pattern, or output path inside a Git checkout also fails closed. This is a safety property, not a substitute for a separate reviewer checking the final Git diff and history.

## Exact approval gate and publication procedure

1. **Owner rights decision, in writing:** confirm authority to license the exact five blobs at the pinned commit, identify the legal copyright holder and any contributors/third-party sources, choose the license and scope (five modules only or a coherent public-repository license), approve the final `LICENSE` and NOTICE wording, and explicitly authorize public publication of those bytes. Until then, do not add source, wheel, zip or SPDX headers to any public branch or PR. The [proposed NOTICE and MIT text](DISCOVERY_NOTICE_AND_MIT_PROPOSAL_2026-10-23.md) are review material only.
2. **Isolated local candidate:** read only the five named blobs from the pinned private commit into a non-Git directory; compare original Git blob IDs; execute the public gate with `--source <local-phismaster-directory> --output <new-local-zip-outside-git>`. Keep all archives and temporary outputs outside the public and private repositories. Do not copy real data or private tests into the public tree.
3. **Resolve reproducibility blocks:** verify Python 3.11 and 3.12, build an installable wheel using reviewed local build dependencies or explicitly approve zipimport distribution, run a clean isolated import and the synthetic golden comparison, and document the excluded `discovery_validation` test dependency. Run relevant scientific tests, including weak-evidence abstention and negative controls, without altering frozen v1.1 policy. The separate longitudinal benchmark may add evidence but cannot silently replace these gates.
4. **Owner-approved source PR, separately:** start from a reviewed public base; add only the approved five files, a NEW initializer, final license/NOTICE, packaging metadata and public synthetic tests. Label every copied file **PREEXISTING** with private commit and original blob; label adapters, plans, package metadata and tests **NEW** with competition-window commits. Do not import private runners, plans, data, archive, history or credentials.
5. **Independent review:** inspect every changed path and Git blob in the source PR; run secret/PII and path scans over the **entire PR diff and Git history**, confirm exact file allowlist and third-party license obligations (including the independently Apache-2.0 licensed Meterless vendor subtree in PR #13), then run clean-clone tests with no private checkout, hidden local package, account or paid service. The public app must fail closed or explicitly abstain when Discovery is absent; no false claim of a live sponsor read.
6. **Final publication gate:** owner explicitly approves the reviewed PR head SHA and release contents after checks pass. Merge, deployment and hackathon submission require their own approvals and are outside this branch's scope.

**Current decision:** local six-entry candidate and the public-safe mechanism are reviewable; publication of the five original modules or an archive is **BLOCKED** pending the owner rights and license decision and the remaining reproducibility checks.
