# PHIS Open Agent — Competition GO/NO-GO and worker orders
Reviewed 2026-10-18. PREBUILD PLANNING ONLY. No feature implementation authorized.

## Sources and authority
Published event page (higher authority than working draft): https://hackathon.genai.works/event/open-agent-hackathon-2026, inspected 2026-10-18.
Earlier user-provided sponsor resources in HackOS, eight sponsor Markdown files, and technical Zetaris links were reviewed on 2026-10-18. Sponsor overview files show Zetaris free instance, NVIDIA model credits, and Cursor team entitlement but onboarding details are TBC before build window.
Limitation: current browser connection does not expose the authenticated HackOS Resources tab. Today’s live changes to private Resources and unexpanded sections 02–10 of public accordion are NOT verified. Do not present this as full binding-rule certification. Ask organizer for interpretation of preexisting PHIS extraction and track eligibility.

## Verified public official facts
- Online, solo participation allowed, team size 1–5.
- Registration closes 2026-10-22 23:59 UTC; build window opens 2026-10-22 00:00 UTC = 02:00 Europe/Madrid.
- Submissions close 2026-10-27 23:45 UTC = 2026-10-28 00:45 Europe/Madrid (DST switched Oct 25). Set internal submission 2026-10-27 20:00 Madrid.
- Tracks: Solving Fragmented Intelligence; The Agent That Can Explain Why; Reasoning Architecture; Wildcard [Tinkerer] Bring Your Own Project.
- Public track description: Explain Why investigates complex questions over multiple data sources, connects findings and produces evidence-backed answers. Tinkerer specifically extends preexisting projects, integrates Zetaris + Meterless, judged on NEW work. The published track descriptions do not alone conclusively settle whether using declared PHIS components forces Tinkerer. Await organizer reply.
- Eligibility visible section: age >=16; no duplicate account; organizer/judging sponsor staff excluded from cash eligibility.
- Scoring: Impact 30; Technical 20; Innovation 15; Demo 15; Product & UX 10; Sponsor Tech 10.

## Compliance matrix
| Topic | State | Evidence or next verification |
|---|---|---|
| Solo eligibility | VERIFIED descriptive | Public event page; 1–5 builders |
| Age/account eligibility | CONDITIONAL | Published section 01, account uniqueness to remain true |
| Build dates/time | VERIFIED | Published Key Dates UTC |
| Submission deadline | VERIFIED | Published Key Dates UTC |
| Explain Why technical fit | YES conceptually | Official track text |
| Prior-component legal reuse/track obligation | BLOCKED | Public track descriptions inconclusive; Help Desk query pending |
| Pre-window permitted prep vs development | UNRESOLVED binding text | Rules section 04/05 must be inspected expanded |
| Submission artifacts, video length, metadata.json, repository/public URL | UNRESOLVED binding text | Rules section 06 and HackOS submission workflow need verification |
| Sponsor exact mandatory technologies across tracks | UNRESOLVED binding text | Tinkerer Zetaris+Meterless explicit; HackOS channels earlier say both mandatory across submissions; official detailed sections must be checked |
| Reuse disclosure and IP | UNRESOLVED binding text | Rules section 05/09 and organizer answer |
| Scoring | VERIFIED | Published weights |
| Data/credential privacy | INTERNAL HARD GATE | PHIS private / synthetic only / logs sanitized |
| Jury reproducibility | INTERNAL HARD GATE | Standalone clean checkout, no private services |
| Public repo governance | VERIFIED planning | Docs in PHIS-OpenAgent-2026; implementation not started |

## Sponsor readiness
Zetaris: technical guides inspected; public getting-started repository supports SQL editor/JDBC/REST; sponsor overview promises participant free instance. Instance URL, assigned namespace, account and query privileges NOT verified. Prefer shared instance and bounded read-only SELECT to self-managed paid AWS.
Meterless: three documented architectures H-MEM, Markovian and World Model are design references, NOT a pip-installed engine. Meaningful integration must demonstrate real state written/read by active agent, with trace. Favor minimal World Model only if nondecorative and feasible. No verified inference-gateway contract for Nemotron.
NVIDIA Nemotron: sponsor overview credits via API key; redemption/model/base URL not yet verified. Separate model-provider adapter, fail closed on unavailable credentials.
Cursor: team access announced; redemption instructions pending. Must be genuinely used for build and recorded in README/development evidence.
DO NOT publish API keys, cloud account IDs, personal records or sponsor tokens.

## Execution schedule and critical path
Critical path: binding rules/track and rights -> sponsor accounts -> synthetic source setup and scoped Zetaris query -> deterministic PHIS science -> model orchestration -> evidence UI -> genuine sponsor trace -> regression/adversarial/cold start -> video/README/metadata/submit.
2026-10-19: planning audit rights/licence, official expanded sections, test commands, fixture/schema finalization.
2026-10-20: sponsor onboarding/documentation changes and judge experience/design QA; product visual signoff if needed.
2026-10-21: readiness refresh, baseline SHA 516e3388ce67061028c1b1b29afb4a4ed965a2e0, owners and GO/NO-GO; authorize only bounded jobs after official opening.
2026-10-22: worker W1 repo/security/approved extraction and synthetic fixtures; W2 sponsor access smoke read-only; stop if prerequisites fail.
2026-10-23: W3 minimal agent orchestration and one actual evidence E2E path; measurable real calls.
2026-10-24: W4 evidence workbench, responsive visual states and contextual follow-up; begin cold-start QA.
2026-10-25: adversarial scientific tests, sponsor trace validation, UX/accessibility; freeze new feature growth.
2026-10-26: feature freeze, reliability repairs, independent judge-run rehearsal, demo screen recording, deck, README/metadata; no optimistic PASS.
2026-10-27: final source/secret/license scan, browser rehearsal and submission by 20:00 Madrid; save submission receipt/screenshots. Preserve remaining 4h45 as contingency.

## Bounded worker orders and acceptance
W1 — Scientific core/source clearance. Only after approved window and reuse authorization: extract approved PREEXISTING files with source SHA; include discovery_features, discovery_signals, discovery_shapes, discovery_temporal, discovery_v11, plan energy if tests show required; no private runner/cloud projection. Worker produces provenance manifest and real unit test logs, comparison to pinned reference; deliver PR, never merge autonomously.
W2 — Zetaris and synthetic sources. Only fictional generated data; choose venue-backed instance. SQL SELECT 1, show databases and bounded data reads; trace IDs, scoped permissions. Avoid AWS charges.
W3 — Agent and model. Nemotron through independently verified official endpoint; allowlisted typed tools, real tool-selection trace, retry/timeout and uncertainty; no free SQL, no invented numbers. Meterless World Model optional conditional, if mandated make meaningful write/read/consumption and fail on fake instrumentation.
W4 — UX/evidence visualization. Implement approved PHIS split-screen, missing-data gaps, status states, evidence drawer, keyboard use and truthful synthetic banner. No placeholder results presented as verified evidence.
W5 — QA/repro. Test three paraphrases, contextual follow-up, abstention, missingness, statistical correction family, variable gate, sponsor outage, prompt injection, clean checkout. Record machine-generated results.
W6 — Submission. Verified demo video, reproducible README, provenance/license docs, metadata JSON if confirmed mandatory, sponsor disclosures, final link and receipt.
Concurrency: at most 2 active technical workers requiring review; none before legal timing/permissions; use cheapest deterministic tests first.

## Contingencies
A: organizer forces Wildcard — enter Tinkerer with no change to hero story, ensure Zetaris+Meterless are REAL, verify award/criteria and reused/new labeling.
B: reuse prohibited or rights unclear — replace private statistical implementation with NEW limited deterministic method or narrower purely descriptive engine; do not copy without clearance. If loses essential science, NO-GO rather than misleading demo.
C: Zetaris credentials late — request Help Zetaris; keep clean synthetic local adapter for development but no sponsor compliance claim; integration must later pass trace gate.
D: Nemotron credits late — alternative authorized model only if rules allow; keep endpoint adapter replaceable; don't mislabel model.
E: Meterless adds risk — minimum meaningful World Model trace vs scope cut; if mandatory and cannot demonstrate, NO-GO.
F: failed scientific association — show truthful descriptive result and abstention, never tune data after result for better-looking finding.
G: late UX — retain one hero path, evidence drill-down, follow-up and abstention; defer dashboards and extra variables.
H: outage during video — retry verified environment and record authentic run; never overlay fabricated sponsor events.

## Decision
PREBUILD PLANNING: GO.
FULL RULE/ELIGIBILITY CERTIFICATION: HOLD.
SPONSOR CONNECTIVITY: HOLD.
PUBLIC SOURCE EXTRACTION / FEATURE BUILD TODAY: NO-GO.
OCT 22 BUILD DISPATCH: CONDITIONAL on verified permitted time, rights, required tools/credits and reproducible sample boundary.

## Next human action
Reopen https://hackathon.genai.works/resources in the connected browser and leave it open; optionally expand public Rules sections 02–10 and open the HackOS #Help desk reply if it has arrived. ChatGPT will inspect the available tab, reconcile newly published information and update this register. Do not send credentials in chat.
