# Build-window audit — 2026-10-22 (Europe/Madrid)

## Evidence and baseline

- Public working branch: `codex/build-window-audit-20261022`, forked from `d0c4e1c2ee02259058f3cf2ab8ebabcdc9055715` (22 Oct, 07:09 Madrid). Working tree was clean before this branch. Earlier repository commits are documentation, not an executable competition entry.
- Private PHIS Discovery baseline recorded in the existing [dependency gate](DISCOVERY_DEPENDENCY_TEST_GATE_2026-10-18.md): `516e3388ce67061028c1b1b29afb4a4ed965a2e0` (13 Oct). No private source or data was copied into this branch. The inventory is read-only and its full import closure and tests remain unverified.
- [Issue #1](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/issues/1) and its [22 Oct execution comment](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/issues/1#issuecomment-6333230383) authorize independent work after opening, require real sponsor evidence, and prohibit unreviewed merges, private publication, and paid provisioning.
- The [live organizer event page](https://hackathon.genai.works/event/open-agent-hackathon-2026) was checked on 22 Oct. Its visible page confirms the build window, deadline, tracks and Wildcard terms. The ten expanded rule sections were previously verified in [OFFICIAL_RULES_VERIFIED_2026-10-18.md](OFFICIAL_RULES_VERIFIED_2026-10-18.md); this run did not independently re-expand every section. Recheck amendments before submission.

## Competition gate matrix

| Gate | Current evidence | State |
| --- | --- | --- |
| Build window | Organizer page: 22 Oct 00:00 UTC to 27 Oct 23:45 UTC | PASS |
| Track | Track 02 fits evidence-backed questions across sources; Wildcard expressly covers extending existing work. Prior PHIS reuse interpretation awaits organizer answer | PROVISIONAL |
| Mandatory technology | Verified expanded §5.1 on 18 Oct: Zetaris + Meterless integration and Cursor development use. Current visible page also names both for Wildcard | RULE PASS / RUNTIME FAIL |
| Pre-existing code | Verified §4.2 and §5.4: declare pre-existing components; score new work. Ownership, reuse rights and exact PHIS extraction manifest not yet approved | HOLD |
| Deliverables | Verified §6: public source and setup README, authentic 1–4 minute video, deck, sponsor explanations | PLANNED |
| Submission fields | Live Submission Hub fields, metadata.json schema, edit behavior not independently verified | UNKNOWN |
| Safety and science | Public branch contains only new synthetic generator and descriptive tools; no private imports or health records | PARTIAL PASS |

`PASS` here describes documentary verification or the narrow local prototype only. It does not mean entry eligibility or final submission readiness.

## Real technical readiness

| Dependency | Observed state | Next proof |
| --- | --- | --- |
| Zetaris | Account dashboard previously reached; zero active compute and no query trace. Cloud compute appears to require AWS credentials. | Authorized instance/namespace, read-only bounded query and sanitized result trace. Verify cost before provisioning. |
| Meterless | Reference engine descriptions reviewed, no installed engine or executed producer→persist→read→consumer loop. | Choose licensed implementation route, persist a real run state, retrieve it for a later decision, record test/trace. |
| Cursor | Sponsor instructions/credits were TBC in reviewed material; effective entitlement and development use not evidenced. | Open project in Cursor, perform a material change, record version/workflow evidence without credentials. |
| Nemotron | Credentials/model call unverified. §5.2 allows contribution where useful according to earlier verified rules. | Safe test invocation, sanitized model/version/latency evidence if access exists. |
| PHIS Discovery | Candidate modules, plans, tests and Python >=3.11 mapped in dependency gate; no executed regression or import-closure proof. | Owner-reviewed file manifest and license/reuse decision, complete import audit, private baseline tests, public synthetic equivalence tests. |
| Public runtime | New stdlib-only synthetic/descriptive core and local unit tests; no agent, LLM, sponsors or UI yet. | Standalone orchestrator, scientific engine gate, sponsor adapters, accessible UI and clean-room E2E. |

## Work started on this branch

`src/phis_open_agent/` is **NEW competition-window code**. It generates a fictional 84-day Europe/Madrid calendar timeline for energy diary and sleep wearable sources. Observations carry synthetic labels, units and stable source record IDs. Read-only coverage, trend and period comparison tools expose actual counts and lineage. Missing days are null; low coverage abstains; comparisons are descriptive only. No statistical or causal claim, medical advice, Zetaris/Meterless/Cursor use, or PHIS engine reuse is implied.

Run from a clean clone with Python 3.11+ and no packages:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent
```

The command labels output `SYNTHETIC_LOCAL_ONLY` and sponsors `NOT_CONNECTED` / `NOT_VERIFIED`. The fixture is a test input, not a sponsor or scientific result.

## Parallel next packets with disjoint boundaries

1. **Rules and access:** recheck expanded live rules, track ruling, Submission Hub fields and sponsor routes. Deliver a dated matrix plus safe PASS/FAIL/UNKNOWN probes. No credential capture.
2. **Scientific boundary:** inspect pinned PHIS code privately, run its own regression suite, resolve reuse/IP, and prepare an approved minimal manifest. Keep private files outside this public checkout until approved.
3. **Zetaris adapter:** after authorized access and cost gate, implement bounded query over synthetic records with sanitized result lineage; own only the data adapter and its contract tests.
4. **Meterless and agent:** select a real engine route, implement state read-after-write that changes a bounded plan, then orchestration and verifier without invented scientific findings; own state/orchestration modules.
5. **UI and judge flow:** build the accessible investigator over schema-validated outputs with visible synthetic disclosure, null gaps, evidence drawer, error/abstention and follow-up; own frontend. Validate actual traces before filming.
6. **Integration owner:** independently run clean-clone E2E for three paraphrases, follow-up, abstention and sponsor outages; assemble true README/video/deck and request founder review before PR merge or submission.

No packet may claim a live sponsor connection from the local synthetic prototype. PR review and final owner approval remain release gates.
