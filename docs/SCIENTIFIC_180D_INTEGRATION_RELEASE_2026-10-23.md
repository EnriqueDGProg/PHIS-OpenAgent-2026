# 180-day scientific integration: release check

**State: functional local synthetic backend, live sponsor gate BLOCKED.** This independent Draft PR is based on [PR #18](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/18). PR #13's default v1 fallback and PR #18's opted-in v2 route remain unchanged. The unchanged public fictional generator and preregistration came from [PR #21](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/21) commit `b5b85ec6c1bde39bc658eeb8a843e6067c26290f`; the copied generator's Git blob is `542874624383ace139677950f8fdddfe0261a72c` in both branches. Case `opportunity`, held-out seed `4101`, was selected there before this integration. [PR #22](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/22) still blocks any private Discovery source publication pending owner rights/IP/license approval. No frontend file, private PHIS source, real health record, credential, paid service, merge or deployment is in this PR.

## What runs

`analysis_version: "v3"` selects a separate 180-day API. The synthetic record contract validates exactly 1,080 calendar slots across six variables, stable synthetic IDs, one fictional participant, units, source types, quality state, nulls and numeric bounds. Observed counts are energy 170, sleep 169, late caffeine 171, exercise 162, stress 173 and unrelated control 170. The original CSV was exported **outside** the checkout, 1,080 rows, SHA-256 `06449f70b135532b7aadfe05f0020341608252e2ff14c3e77110e94d5531a053`; CSV readback reproduces the canonical row digest `fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea`.

The six bounded SQL pages require sizes 200/200/200/200/200/80, independent request and query IDs, a SHA-256 for each SQL statement, all 1,080 source IDs and the same canonical digest. Injected transport tests pass but are explicitly `SIMULATED`. In live mode the code requires real HTTP transport, preflight and full verified readback before Discovery; there is no fixture fallback.

The v3 adapter passes **the verified rows** to the approved local-only PHIS Discovery v1.1 package. Its copied plans differ from the PR #18 scientific plans only in synthetic dataset ID; pairs, lags, routes, 999 resamples, blocks 3/7/14, BY corrections and all gates remain frozen. Energy plan SHA-256 `243c769261d158793db1c0a16a784994de45fa5f8cbdcbed27980f6278555cb8`; sleep plan `9b19ae45e60bf48ef8aaf97f8e323444e5f6780f1af3569fc00b16eb80943236`; temporal policy `d708d6113ac1c503cd06aaf8f9f5db184136ad65c56d2429fbb21da4d402f460`. Every family retains 16 hypotheses, including unsupported children and the negative control. Lineage reconstructs exact paired source IDs and checks each Discovery raw N.

The official Meterless World Model Engine persists a validated `scientific_evidence_180d` event with plan/policy/family/digest hashes, classification counts, source query IDs/SQL hashes and all 1,080 source IDs. A restarted API/Engine instance reads this event and selects the next family. No cache was needed or added: one family runs per request; a live request must query fresh Zetaris rows, so changed data cannot reuse stale evidence. No exploratory guidance recommendation is promoted into a scientific or clinical claim.

## Measured results and gates

| Gate | Result and evidence |
| --- | --- |
| Authentic local Discovery energy, 180 days | **PASS** 16 children, 3 `candidate_signal`; direct adapter wall time 10.729 s. Same-day sleep r=+.5604, N159, CI [.4211,.6742]; previous-day stress r=−.5168, N163, CI [−.6480,−.3342]; same-day stress r=−.4390, N164, CI [−.5523,−.2785]. Each had child/parent selection BY q .00417/.01667, compatible temporal state and 3/7/14-day block support. Pairwise observational associations only. |
| Localhost HTTP energy request | **PASS** first measured call 16.5605 s; `SYN-RUN-953d45739183`, canonical digest above, official Engine evidence event `b0c9575c560784f1685ebe6917dd44e84fea53e8401290121974cc56383dda76`; 1,080 source IDs persisted. Latest 28-day energy mean 5.5676 → 5.9142, +.3466 descriptive points. A second timing run measured same-server cold 12.5748 s and warm 12.5872 s: no material speedup, as no cache was added. |
| Restarted API/Engine follow-up | **PASS** first run 13.2117 s; parent event read selected sleep, `SYN-RUN-20c63e51aaa9`, official Engine event `ada2fac14fba9b0a2efef4c637e7d592def7628324dd277bd58d8fb006f73bcb`. Sleep family 16 children, 2 candidates: previous-day late caffeine r=−.5546, N160, CI [−.6437,−.4412], and previous-day stress r=−.5158, N161, CI [−.6409,−.3453]; same corrected q and three-block support. The independent cold/warm timing run's restarted sleep call took 37.2889 s, showing variable Engine/API wall time. |
| Source and adversarial tests | **PASS** six exact simulated pages, unique IDs and complete source set; duplicate, missing, malformed, nonfinite, wrong unit/identity and zero-filled nulls rejected; injected transport rejected in live mode; missing local Discovery blocks before a claim; changing verified sleep observations changes both digest and calculated sleep–energy effect. No negative control was promoted in the actual baseline. |
| Python regressions with approved local Discovery | **PASS 79/79**, including v1/v2 and focused v3 tests. One initial v3 test isolation check failed because loaded Python modules defeated `sys.modules` patching; the test was corrected to intercept imports, its focused rerun passed, and the complete 79-test run passed. This was a test setup issue, not a scientific calculation failure. |
| Existing frontend client tests | **PASS 11/11**, with no frontend edits. |
| Official Meterless conformance | **PASS 8/8** with `WORLD_MODEL_IMPL` set to the pinned implementation. |
| Real local Zetaris preflight, CSV registration and six-page readback | **BLOCKED**: `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, `ZETARIS_API_KEY` are unset; Docker Desktop Linux engine pipe is absent. No real Zetaris query/request ID exists, and injected-transport IDs are not sponsor proof. |
| Private Discovery distributable and public clean-clone v3 scientific execution | **BLOCKED** by PR #22's owner publication/license gate. The API returns `BLOCKED` without the approved local package; v1 fallback remains runnable. |
| Release/merge/deployment | **NO-GO** until live Zetaris and owner rights gates are satisfied and independently reviewed. |

The first local-only HTTP proof JSON SHA-256 is `ea582e018f07b3877e1358e84c6e3eeb218db7da74dc298d9eeebbe03b4fef85`; the second cold/warm/restart timing proof is `a0443790e849518f4771f016d2d5b31b1ddd2634812f3a8f96e263ca8f45d08e`. Both stay outside the public repository. The energy run showed a last-28-day increase of +.3466 and a first-versus-last fixed 30-day difference of −.3548; [the API handoff](SCIENTIFIC_180D_API_HANDOFF_2026-10-23.md) explains the windows. These descriptions do not assert a cause of either change.

## Reproduce without publishing private source

Run from this branch, with Python 3.12 and Node 24. `PHIS_PRIVATE_SRC` is the owner-approved unpublished five-file package's local `src` directory outside this checkout; `PHIS_LOCAL_EVIDENCE` is an external local directory. Neither value should be committed or printed. Do not set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS` until real source prerequisites are present.

```powershell
$env:PYTHONPATH = "src;$env:PHIS_PRIVATE_SRC"
python scripts/export_stochastic_180d.py "$env:PHIS_LOCAL_EVIDENCE\opportunity-4101.local.csv"
python scripts/scientific_180d_http_smoke.py > "$env:PHIS_LOCAL_EVIDENCE\live180-http.local.json"
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
$env:WORLD_MODEL_IMPL = (Resolve-Path 'vendor\meterless-world-model\src\index.ts').Path
node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts
```

The actual local Zetaris next action is to start the authorized daemon without disturbing other services, supply the direct REST URL/org ID/API key through the local environment, stage the fictional CSV at a server-visible path, execute the documented `registration_sql()` statements, then require a real preflight and six-page readback using `read_verified_180d()` before a live v3 HTTP run. Capture **actual** HTTP request/query IDs and Engine receipts, verify their linkage to the 1,080 records, and only then mark the Zetaris gate PASS. The owner must separately approve private source rights, license/NOTICE and any publication, merge or deployment.
