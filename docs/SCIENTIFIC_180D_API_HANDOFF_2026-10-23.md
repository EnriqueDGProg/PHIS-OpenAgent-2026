# 180-day scientific API handoff

For the Antigravity frontend worker. No files under `frontend/**` are changed by this PR. The v1 default and PR #18 v2 route remain available. This document describes the separately opted-in v3 route and an actual localhost run using the original PR #21 fictional OPPORTUNITY case, seed 4101. Its Zetaris status was **NOT_CONNECTED**, so the example is not live sponsor proof.

## Request

`POST /api/investigations` with `Content-Type: application/json`:

```json
{"analysis_version":"v3","question":"Why has my energy changed?"}
```

The optional `scenario` may only be `"opportunity"`. The 180-day case spans 2026-04-25 through 2026-10-21, six variables and 1,080 explicitly synthetic date-variable slots. Set server `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS` only after actual local Zetaris is configured and the CSV is registered and read back. That mode rejects fixture and injected-transport fallback.

## Executed local response excerpt

From the actual localhost HTTP run with authentic local PHIS Discovery and official Meterless World Model Engine. Numbers below are computed results for the **fictional** source, not UI constants:

```json
{
  "contract_version": "investigation.v3",
  "run_id": "SYN-RUN-953d45739183",
  "dataset_id": "PHIS-SYN-180D-opportunity-4101",
  "mode": "SYNTHETIC_LOCAL_ONLY",
  "status": "PASS",
  "family": "energy",
  "comparison": {
    "variable": "energy_central",
    "baseline": {"start": "2026-08-27", "end": "2026-09-23", "mean": 5.567576923076923},
    "comparison": {"start": "2026-09-24", "end": "2026-10-21", "mean": 5.9142222222222225},
    "difference": 0.3466452991452993,
    "method": "arithmetic_mean_observed_days"
  },
  "longitudinal": {
    "variable": "energy_central",
    "method": "arithmetic_mean_observed_days",
    "first_to_last_difference": -0.3548288177339902,
    "inference": "descriptive_only"
  },
  "scientific_evidence": {
    "hypothesis_count": 16,
    "record_digest_sha256": "fbc8653d5f0d8aeb84c65d06607d7821fbf1c3195088c6d023f17ae2c32a7cea",
    "plan_sha256": "243c769261d158793db1c0a16a784994de45fa5f8cbdcbed27980f6278555cb8",
    "temporal_policy_sha256": "d708d6113ac1c503cd06aaf8f9f5db184136ad65c56d2429fbb21da4d402f460"
  },
  "sponsor_proofs": [
    {"sponsor": "zetaris", "status": "NOT_CONNECTED"},
    {"sponsor": "meterless_engine", "status": "VERIFIED"}
  ]
}
```

This is an excerpt; the actual response additionally contains all six 30-day `longitudinal.windows`, `coverage`, source-linked daily `series`, `findings`, all 16 scientific `signals`, `tool_trace` and complete sponsor proof objects. Each signal has its own classification, effect, 95% CI, raw/effective N, corrected selection q values, temporal state/reasons, 3/7/14-day block checks, flags and exact paired source IDs. The `comparison` also includes its source IDs. The official Engine evidence event persisted all **1,080** unique source IDs. The full local-only HTTP proof JSON has SHA-256 `ea582e018f07b3877e1358e84c6e3eeb218db7da74dc298d9eeebbe03b4fef85` and stays outside the public repository.

## Qualified and exploratory findings

Display `candidate_contributor` only for engine `candidate_signal` classifications, with the visible caveat that these are pairwise observational associations, not proven causes. Energy's executed family returned three qualified levels associations: same-day sleep r=+.5604 (N=159, 95% CI [.4211,.6742]), prior-day stress r=−.5168 (N=163, CI [−.6480,−.3342]) and same-day stress r=−.4390 (N=164, CI [−.5523,−.2785]). Their worst-block child/parent BY q values were .00417/.01667, temporal state `temporally_compatible`, and all three block lengths supported inference. Other tested hypotheses remain in `scientific_evidence.signals`; `association` or `unsupported_hypothesis` findings must stay visually distinct and cannot be promoted by UI text. No negative control was promoted.

The latest 28-day energy mean **increased** by +.3466 even though the first-to-last fixed 30-day energy mean changed by −.3548. Show dates and method for each descriptive comparison so the two windows are not confused. Neither difference explains its own cause.

## Persisted follow-up

After a local API/Engine restart, the executed request was:

```json
{"analysis_version":"v3","question":"What should we investigate next?","parent_run_id":"SYN-RUN-953d45739183"}
```

The official Engine read the parent's `scientific_evidence_180d` event and selected **sleep**; response `SYN-RUN-20c63e51aaa9` passed with `parent_run_id` set, `family: "sleep"` and a `meterless.world_model.read` trace showing `selected_family: "sleep"`. Its 16-child family had two qualified levels associations: prior-day late caffeine r=−.5546 (N=160, CI [−.6437,−.4412]) and prior-day stress r=−.5158 (N=161, CI [−.6409,−.3453]); corrected child/parent BY q .00417/.01667 and 3/7/14-day blocks supported both. Its latest-versus-previous sleep mean difference was −.0077 hours, a negligible descriptive change. The prior evidence changes which family the agent executes; the follow-up is not selected from question keywords alone.

## Failure and sponsor states

- `status: "ERROR", reason_code: "source_error"`: malformed/incomplete source, failed Zetaris preflight/readback, or attempted simulated transport in live mode. No scientific evidence; `comparison` and `longitudinal` are null. No fixture fallback.
- `status: "BLOCKED", reason_code: "tool_error"`: approved local Discovery package or frozen plan unavailable. No computed scientific claim.
- `status: "BLOCKED", reason_code: "comparison_unavailable"`: parent run lacks verified v3 evidence. No follow-up analysis.
- `status: "INSUFFICIENT_DATA", reason_code: "weak_coverage"`: the predeclared comparison lacks observed support.
- In local synthetic mode, Zetaris is `NOT_CONNECTED`; the official Engine can independently be `VERIFIED`. Do not imply Meterless Runtime, Nightshift, NVIDIA inference or live Zetaris from an Engine receipt.

For actual live mode, use `sponsor_proofs` plus matching `tool_trace` request IDs, query IDs and SQL hashes to present Zetaris proof. Local injected-transport tests return `SIMULATED` and are not sponsor evidence.
