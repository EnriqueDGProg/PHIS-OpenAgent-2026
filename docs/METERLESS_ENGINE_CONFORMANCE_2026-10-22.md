# Meterless Engine P0 — official contract and local evidence

Implemented 22 October, reverified 23 October 2026. Branch: `codex/meterless-engine-conformance-20261022`, stacked on PR #6 (`74313b4`). This record covers **one local Engine**. It does not combine PR #10 (live Zetaris), PR #9 (English UX), PR #8 (adversarial review), or PR #11 and does not assert overall submission readiness.

## Official sources and interpretation

- The [official event page](https://hackathon.genai.works/event/open-agent-hackathon-2026#rules) now gives a 22–27 October build window and states that existing projects in Wildcard are scored on new work. The requester relayed a moderator clarification: Cursor optional; at least one functional, tested Meterless Engine mandatory. That clarification is recorded as user-supplied moderator guidance; the public collapsed rule page does not independently display its exact wording in this audit.
- The [Meterless engine catalog](https://github.com/Meterless/Meterless#engines), [World Model implementation guide](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/AGENTS.md), [ingest pipeline](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/docs/ingest-pipeline.md), [stable IDs](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/docs/stable-ids.md), [reference API](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/reference/src/index.ts), and [conformance runner](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/conformance/runner.ts) were read from official commit `1742dec56a66e58eef9dda2d2b865823758ca8cd`.
- The upstream [Apache 2.0 license](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/engines/world-model/LICENSE) permits the reference source to be reused with the included license and attribution. This branch makes **no project-wide license selection**.
- The [stack overview](https://github.com/Meterless/Meterless/blob/1742dec56a66e58eef9dda2d2b865823758ca8cd/docs/architecture/stack-overview.md) distinguishes World Model state modeling from the Meterless provider/Runtime and Nightshift. Direct NVIDIA inference is another separate path.

## Audit matrix

| Gate | PR #6 before | This branch | Evidence and boundary |
| --- | --- | --- | --- |
| Actual Meterless Engine in app execution | **FAIL** — original JSONL `SyntheticRunWorldModel` followed selected ideas | **PASS local** — API and CLI use pinned official World Model reference via `MeterlessRunWorldModel` | `vendor/meterless-world-model/src`, `bridge.ts`, `src/phis_open_agent/api.py`, `agent_cli.py` |
| Official World Model conformance runner | **FAIL / unrun** | **PASS 8/8** | Vendored unmodified runner at same upstream commit, `WORLD_MODEL_IMPL` pointed at vendored Engine; all eight named checks passed locally |
| Event → durable persistence → read → changed decision | **PASS as inspiration, FAIL as official Engine proof** | **PASS local** | `scripts/meterless_engine_trace.py`: no prior evidence → BLOCKED; comparison event → `.world` file → fresh Engine read → `get_variable_coverage` and child `coverage, trend` |
| Idempotency and negative cases | Partial original checks | **PASS local** | Same event returns same native Engine receipt; missing provenance, unexpected payload, corrupted persisted event and missing Engine rejected; 7 real Engine tests including the HTTP handler path |
| Synthetic provenance | **PASS local** | **PASS local** | 53 fictional comparison source IDs in canonical Engine event; no raw health observations persisted |
| `investigation.v1` sponsor proof | `meterless_engine: NOT_CONNECTED` | **PASS conditional** | `VERIFIED` only after Engine append and independent durable readback; proof ID must match a returned tool trace. Runtime/NVIDIA/Zetaris remain `NOT_CONNECTED` |
| Meterless Runtime / Power / Nightshift | **FAIL / not connected** | **FAIL / not connected** | No external API, token, Nightshift binary or model inference used; Engine success does not count as these paths |
| NVIDIA direct | **FAIL / not connected** | **FAIL / not connected** | No Nemotron request; no inference claim |
| Combined submission with Zetaris PR #10 | Separate PR | **FAIL / not combined** | PR #10's real Zetaris evidence is independent. Review the stack and rerun end-to-end after an authorized integration; no merge performed here |
| Organizer acceptance of this Engine route | Unverified | **UNVERIFIED** | Technical Engine checks pass. No organizer adjudication of this exact branch was obtained. |

## Reproduce from a clean checkout

Requires Python 3.11+ and Node.js 24 with its built-in TypeScript transform. No npm packages, account, network service, API key, payment or private PHIS source are needed.

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:WORLD_MODEL_IMPL=(Resolve-Path vendor/meterless-world-model/src/index.ts).Path
node --disable-warning=ExperimentalWarning --experimental-transform-types vendor/meterless-world-model/conformance/runner.ts
python -m unittest discover -s tests -q
node --test frontend/tests/*.test.mjs
python scripts/meterless_engine_trace.py
```

Results on this branch: conformance **8/8 PASS**; Python **42/42 PASS**; frontend **7/7 PASS**. Seven Python cases invoke the real local Engine, including the actual API handler with a socketless test transport; this does not claim a browser-to-server HTTP connection. The trace run returned domain event `23c76b52d2b50fa186ff7080337d96ba0af729a5dff20de539316952f35bdffa`, native Engine receipt `evt_16`, `persisted: true`, 53 source IDs, and the child cited the same domain event. It chose `coverage` then `trend` after the parent; without prior evidence it was `BLOCKED`. The separate nonnegative comparison test selected `get_longitudinal_trend`. The content-addressed **domain** event ID is stable; `evt_16` is a sequential native receipt, not a stable cross-store identifier. These IDs arise from fictional input and are not measurements.

The reference's local persistence writes a JSON snapshot of its event log. It was tested across fresh processes, not for crash-atomic writes or multi-process concurrency. Old PR #6 JSONL files are not silently migrated; a new Engine namespace is created under the ignored `.local-state/.world/` directory. The UI's proof is tied to the Engine's canonical log; a missing Node runtime or failed readback returns an error, not a sponsor PASS.
