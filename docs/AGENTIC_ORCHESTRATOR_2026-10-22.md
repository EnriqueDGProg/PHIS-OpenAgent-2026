# Bounded synthetic agent over PR #3

This branch is stacked on PR #3. It does not change the frontend, sponsor adapters, or the `investigation.v1` contract. The local flow is **PLAN → TOOLS → EVIDENCE → VERIFY → RESPOND/ABSTAIN**. The plan depends on the question, observed coverage, comparison result, and persisted prior run state. It is a small deterministic policy, not an open-ended medical agent.

## Run without installing anything

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent.agent_cli energy --run-id SYN-RUN-DEMO-1 --state .synthetic-agent-state.jsonl
python -m phis_open_agent.agent_cli followup --run-id SYN-RUN-DEMO-2 --parent-run-id SYN-RUN-DEMO-1 --state .synthetic-agent-state.jsonl
```

The fixture is fictional and 84 days long. The JSONL file contains only synthetic run decisions, source record IDs, and a descriptive difference. Use a disposable path for demo state; do not commit it. No network request is made. Meterless Engine, Nightshift Runtime, Nemotron, and Zetaris remain `NOT_CONNECTED` in this path.

## Decisions and limits

| Input/state | Next action |
| --- | --- |
| Energy question with enough records | Coverage → recent trend → two 28-day comparison; if the difference is negative, inspect recent sleep coverage. |
| Sleep question | Coverage → recent trend; no energy comparison. |
| Follow-up after a verified prior energy response | Read persisted comparison and response events. Negative difference selects sleep coverage; nonnegative difference selects energy trend. |
| Unsupported question or missing prior run | Block and abstain before tools. |
| Weak coverage or comparison | Abstain; later tools are skipped. |
| Tool error, missing provenance or invalid output | Record an `ERROR` trace and abstain without echoing exception text. |

The operational gate is 14 observed days per 28-day window; it is a demo completeness rule, not scientific significance. At most four deterministic tool calls are allowed. Comparison is descriptive only. The agent does not infer causes, confidence, treatment, or association from simultaneous data. Null points and their absent source IDs remain in the trend evidence. Raw question text and raw observations are not written to the World Model.

`SyntheticRunWorldModel` records hashed, append-only `agent_state` events with bounded fields. A follow-up uses a fresh read of the persisted parent run. The optional `claim_selector` may return only IDs of deterministic, cited claims; invalid selections are rejected and recorded, with the verified fallback text. It is an interface for future synthesis, not a Meterless or Nemotron integration. The preexisting inference probes are connectivity checks only. World Model is original work **inspired by** Meterless; official Engine conformance and integration remain blocked pending vendor access and proof.

## Connection to `investigation.v1`

1. Keep the Python engine as the sole producer of coverage, series, comparison and findings. Adapt each `evidence` item to the existing `Coverage`, `Series`, or `Comparison` shape; preserve its `source_record_ids` and null trend points.
2. Map `PASS`, `INSUFFICIENT_DATA`, `BLOCKED`, and `ERROR` directly to `RunStatus`. Map verified claims to `Finding.kind='observation'` and all abstentions to `Finding.kind='abstention'`. Do not map the descriptive comparison to causation or hypothesis.
3. Map tool phase events to `ToolTrace` using the event hash as `trace_id`. The current contract has no planning/verification event type or parent event reference; expose those in a separate optional agent trace extension after contract review. Until then, retain them in the Python result and World Model.
4. Use `mode='SYNTHETIC_LOCAL_ONLY'` and set all sponsor proofs to `NOT_CONNECTED`. Do not infer `VERIFIED` from local or simulated tests. Keep the 84-day fixture windows consistent with the backend contract.
5. The existing frontend/API adapter can call this orchestrator after a reviewed contract change. This branch deliberately leaves that adapter untouched.

## Known gaps

This is a bounded policy with keyword routing for three demo intents. It has no production identity, concurrency lock, consent workflow, health interpretation, or live provider synthesis. JSONL integrity hashes detect accidental edits, not malicious rewriting. These are explicit boundaries, not sponsor-compliance claims.
