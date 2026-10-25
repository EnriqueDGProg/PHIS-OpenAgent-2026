# Issue #26: bounded Nightshift planner gate (2026-10-23)

## Scope and result

The backend `investigation.v4` path accepts synthetic 180-day questions, asks Meterless Runtime for a strict plan and evidence critique when an authorized API is available, invokes one allowlisted deterministic tool, and persists plan, tool evidence, and verification events through the pinned Meterless World Model Engine. A critique can trigger a second coverage tool call or abstention. Original PHIS Discovery remains the only authority for scientific comparisons. Model text cannot become a measurement or finding. The fallback is explicitly labeled `LOCAL DETERMINISTIC MODE`; scripted tests are `SIMULATED` and cannot produce sponsor proof.

**P0 sponsor result: BLOCKED.** No authenticated Nightshift inference or provider request ID was obtained. The browser Web edition is not an external Python API, and no desktop/DGX runtime or real bearer token was available. Do not present the scripted planner tests, in-tab sample jobs, or World Model events as Nightshift inference.

## Official sources and observed connection state

- [Open Agent Hackathon published rules](https://hackathon.genai.works/event/open-agent-hackathon-2026), §5.1, require integration with Zetaris and Meterless; §5.4 requires declaration of preexisting product code. The sponsor onboarding checklist described in PR #25 asks for Nightshift as the primary provider. These are different claims: the published rule does not explicitly name Nightshift, while issue #26 applies the stricter sponsor checklist. Eligibility remains subject to organizer confirmation.
- [Meterless provider contract](https://www.meterless.ai/engines.html) describes the desktop Runtime at `http://127.0.0.1:8088/v1`, a real bearer token, `meterless-app`, `meterless-scope: user`, `GET /v1/models`, and `POST /v1/chat/completions`. `rt-local` is an illustrative, rejected placeholder.
- In the owner's [Nightshift Web](https://meterless.ai/Nightshift/WEB/) tab, Setup says: “Nightshift Web is the client here — it does not become a server other apps can call.” Console > Connect says the in-tab engine answers `/v1/models` and `/v1/chat/completions` for that page, and other apps cannot reach `127.0.0.1:8088` from the browser tab. Its shown API key is `in-tab`; its copy controls do not grant a reachable external endpoint. Hotspot mode is disabled in Web. No key was revealed or copied.
- A bounded local `GET http://127.0.0.1:8088/v1/models` returned `SocketException` (no listener). `Requests: 0` in Web. Therefore no authenticated `GET /v1/models` or inference was attempted with a Web-only pseudo-token. No real model result or trace was fabricated.

## Verification matrix

| Gate | State | Evidence |
| --- | --- | --- |
| Backend-only isolated branch | PASS | `codex/nightshift-agent-planner-20261023`, based on PR #24; no `frontend/**` edits. |
| Model-driven plan, tool selection, critique, replan, abstention | PASS in scripted tests | Distinct scripted energy trend and sleep coverage plans; schema and injection rejection; critique causes a persisted coverage replan event. All receipts labeled `SIMULATED`. |
| Original Discovery and World Model | PASS locally | Synthetic energy/sleep fallback calls used the owner-approved local Discovery package; append/readback uses the pinned World Model Engine. No private package files entered Git. |
| Live Nightshift `/v1/models`, inference, request IDs | BLOCKED | Web is in-tab only; local `:8088` connection refused; no authorized desktop endpoint/token. |
| Live Zetaris source | BLOCKED | Separate Zetaris/Docker worker owns this handoff; v4 refuses live mode instead of substituting a fixture. |
| Official eligibility | BLOCKED for final claim | Published §5.1 and the stricter sponsor checklist must be reconciled with organizers before submission. |

Verification run: `python -m unittest discover -s tests -v` completed **85 tests, OK** with the approved private package supplied only on the local import path. A loopback `POST /api/investigations` with `analysis_version=v4` returned HTTP 200, energy Discovery PASS, six official Engine event IDs, `LOCAL DETERMINISTIC MODE`, zero Nightshift receipts, and Meterless Runtime `NOT_CONNECTED`. These results verify backend wiring and honest fallback, not sponsor inference.

Fail-closed check with `PYTHONPATH=src` and no private Discovery package returned `status=BLOCKED`, `scientific_evidence=null`, and Runtime `NOT_CONNECTED`. It did not manufacture a scientific result.

## Reproduction and release procedure

1. Check out this branch in an isolated worktree. Keep an owner-approved Discovery package outside the repository and set `PYTHONPATH` so that package and `src` are importable. Never commit the package, raw health data, or tokens.
2. Run `python -m unittest discover -s tests -v`. Inspect `nightshift_receipts`: scripted transports must say `SIMULATED`; an unavailable provider must say `LOCAL DETERMINISTIC MODE` or `BLOCKED`.
3. For genuine Nightshift proof, install an owner-approved, integrity-verified desktop/DGX Runtime without payment, obtain its local token through its documented connection flow, and pass it to the process as `METERLESS_RUNTIME_TOKEN` without logging it. Run authenticated `GET /v1/models`, select a listed `meterless/*` route, and make one bounded `POST /v1/chat/completions` with the required headers. Capture only provider-issued request/response IDs, route/model, status, and redacted token usage; keep the token and prompt private. Verify the Runtime receipt against those IDs.
4. Run two different v4 questions with the live planner and inspect persisted plan/tool/verification events and actual tool calls. Require an evidence-triggered coverage replan and a refusal on weak or adversarial evidence. A simulated transcript is not sufficient.
5. Integrate the separate verified Zetaris source handoff only after its owner completes it. Then rerun backend tests and a clean-clone check with the approved Discovery package installed out of tree.
6. Obtain owner approval for source reuse, license/publication and final submission; resolve the official-rule/checklist discrepancy with the organizer. Review and merge separately. No deployment or submission is authorized by this document.

**Approval gate:** Request final approval only after the PR shows authenticated Nightshift `GET /v1/models` and inference receipts, two distinct live plans, official World Model events, original Discovery calculations, verified Zetaris source lineage, full test results, public-source audit, and organizer eligibility confirmation. Until then, keep the PR Draft and mark Nightshift sponsor proof `BLOCKED`.
