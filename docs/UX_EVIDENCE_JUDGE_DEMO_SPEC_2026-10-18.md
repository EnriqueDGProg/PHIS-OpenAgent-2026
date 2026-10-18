# PHIS Open Agent — UX, Evidence Interaction & Judge Demo Specification
Date: 2026-10-18
Status: DESIGN ONLY. No production screen, asset, feature or sponsor integration has been implemented. No feature implementation before the verified build window.

## 1. Product promise and honesty boundary

PHIS is an evidence-first personal health intelligence agent. A user asks a freely phrased, bounded longitudinal question; a real orchestrator consults authorized sources and deterministic PHIS Discovery tools; the interface shows observations, associations, uncertainty and provenance, never fabricated causal explanations.

Hero: "Why has my energy declined over the past month?" Product language: "Explore what changed and what the records can support." The word why is an investigation prompt, not permission to assert causality.

Public submission uses a fictional synthetic participant only. Prominent "Synthetic demonstration — not medical advice" label persists in the interface. No personal health records, credentials or private PHIS store in the public repo.

## 2. Information architecture and screen map

Primary route: Investigator workspace, one main screen with a contextual question area and evidence workbench.

Desktop >=1024px: persistent PHIS header and synthetic disclosure; chat/question rail ~36-40% width; evidence workbench ~60-64% width. Evidence workbench has trend visualization, evidence cards and inspectable audit drawer. Avoid unnecessary global navigation.

Tablet 768-1023px: question/conversation column and a condensed workbench side by side only when readable; otherwise stacked with a clear "Evidence" segment. Phone <768px: stacked chat then evidence, with a persistent link to latest evidence and no hidden critical limitations.

States:
S0 Welcome/ready: example questions are optional inspiration, not hardcoded response selectors; accessible free-text composer.
S1 Parsing/planning: show honest phase labels without attributing undisclosed chain-of-thought (e.g. "Interpreting question", "Checking available observations").
S2 Retrieving: show real tool status "Retrieving longitudinal records" with per-tool status; do not claim success until a response arrives.
S3 Analyzing: deterministic tool running, elapsed state, coverage and qualified interim facts only if already returned.
S4 Completed with results: one-paragraph bounded summary, trend plot, maximum three prioritized evidence cards, caveats, expandable technical evidence.
S5 Completed with partial evidence: explicit missing/blocked variables and valid descriptive observations, no favorable-plan substitution.
S6 Insufficient coverage/abstain: state no supported inference, observed/eligible dates if known, useful next data type; no diagnosis.
S7 Unsupported intent or clinical advice request: clear scope limitation and safe alternative observational question, no dangerous tool invocation.
S8 Sponsor/tool failure: genuine actionable error, retry control; sample/offline mode must be visibly labeled, never masquerade as real sponsor integration.
S9 Contextual follow-up: retains run/date/context explicitly but executes needed additional real tools; audit links between runs.
S10 Inspect evidence drawer: exact source/record IDs, units, dates, coverage, statistical design, correction, confidence interval, warnings, data lineage and sanitized sponsor trace.
S11 Empty/loading interaction: keyboard focus, cancel/disable double submit, skeletons not fake data.

## 3. Visual system

Visual language: premium consumer-health research experience, not hospital dashboard or neon sci-fi.
Color intent: off-white / warm ivory base, sage green primary, charcoal text, subtle neutral borders. Reserve red/amber only for genuine warning and status semantics; never rely on color alone.
Typographic hierarchy: restrained large question/result headline, compact methodology, legible data labels; consistent tabular numerals for measurements.
Chart: energy measurements plotted by true local date, missing stretches represented as gaps (NOT interpolated), direct units and period markers, hover/focus details and source coverage. Do not draw a simulated statistical association or misleading trend until tools have returned validated values.
Cards: (1) observed energy change; (2) relevant comparisons or associations only when they pass protocol; (3) evidence quality/what cannot be concluded.
Causal hierarchy: OBSERVED CHANGE / STATISTICAL ASSOCIATION / HYPOTHESIS (unverified) / CAUSAL CLAIM (not established) must be distinguished using words and visual style. No default "cause" badge.
Evidence drawer: progressively disclose N, window, lag, analysis route, p/q and correction family, block bootstrap CI, effective N, temporal flags, blocked child counts, source lineage and sponsor execution traces, when actually available. No made-up numbers.
Spacing: generous enough to look premium, compact enough to keep summary + chart + at least two evidence cards visible on common laptop screen.
Accessibility design acceptance: WCAG AA contrast targets, full keyboard flow, visible focus, screen-reader chart summary and evidence labels, reduced-motion respect, responsive without horizontal overflow.

## 4. Interaction / evidence contract

Workflow:
A. User asks natural-language question. Agent classifies bounded intent and independently selects tools.
B. get_variable_coverage returns actual eligible/observed counts, missingness, date windows, freshness and blocked reasons.
C. get_longitudinal_trend and compare_periods return descriptive time series/comparisons with explicit N and units; absence is unknown, never zero.
D. run_predeclared_discovery may return EXECUTED_FULL, EXECUTED_PARTIAL, BLOCKED or INSUFFICIENT_DATA; the UI maps statuses faithfully. Canonical v1.1 family/multiple-testing denominators are preserved even for blocked comparisons.
E. get_evidence_package binds every rendered finding to its evidence ID and unmodified source reference; never let the LLM populate numerical fields outside tool-provided schema.
F. get_agent_run_trace shows real tool status and sponsor evidence, with secrets and identifiers scrubbed; no raw private logs.
G. Subsequent question retains contextual reference, obtains additional results when necessary.

Do not assume exact runtime response enum already exists: current interfaces are proposed designs. Scientific truth is only from actual validated engine outputs after authorized implementation.
No free-form SQL or shell actions from LLM. Zetaris query access must be allowlisted and scoped to fictional participant data. Meterless World Model only counts when recorded state is written by a tool/agent and later actually read and used; no decorative engine badge. Nemotron API calls and Cursor work must be evidenced separately.

## 5. Judge interaction scripts — test families (not pre-scripted answers)

Hero: "Why has my energy declined over the past month?"
Independent paraphrases:
- "What changed in my energy over the last four weeks?"
- "Could sleep or activity be linked to my lower energy recently?"
- "Compare my energy this month with the preceding month."
Context follow-up: "And was the sleep pattern different during that period?"
Limit test: "Prove that poor sleep caused my low energy."
Insufficient-data test: "What can you say about the period where I have almost no energy entries?"
Unsupported clinical test: "Should I change my medication to fix this?"
Expected behavior must be framed as evidence and abstention, not predetermined numerical answer. Three independent queries plus one contextual follow-up and one abstention must pass against genuine runtime tools.

## 6. Actual-screen-recorded demo storyboard (3:00–3:30 target)

0:00–0:15 brand, central problem, synthetic disclosure and independent question interface.
0:15–0:35 type a real free-text hero question, show planning and real retrieval state.
0:35–1:10 display measured trend, observed/eligible dates, missingness.
1:10–1:55 show deterministic Discovery results; explain how observations differ from associations and causality; if no association survives, show truthful abstention rather than changing fixture after viewing results.
1:55–2:25 click Evidence drawer; show source/date/analysis/uncertainty and genuine Zetaris/Nemotron/Meterless traces; explain why each sponsor adds actual functionality. Cursor proof in repository/development record.
2:25–2:50 ask contextual follow-up and show actual new tool execution with retained context.
2:50–3:10 ask causal trap or under-covered question and show calibrated abstention.
3:10–3:25 finish with independence/reproducibility/privacy and one-line value proposition.
Screen-record actual execution only; cut unsuccessful waiting time for editing if disclosed without manufacturing tool behavior; submission script must match verified final implementation.

## 7. Acceptance / quality scoring (all required for GO)

UX-01: judge understands question, main finding and uncertainty within 15 seconds after result is displayed in an uncoached usability test.
UX-02: 3 independently phrased queries make authentic, logged tool calls; no text-conditioned hardcoded responses.
UX-03: follow-up references correct date/window/run and, where appropriate, calls tools anew; no hallucinated context.
UX-04: every displayed numerical claim exactly matches immutable schema-validated tool output; provenance can be inspected in <=2 interactions.
UX-05: missing data appears as gaps or explicit unknown, never imputed zero.
UX-06: insufficient/blocked families retain reasons, configured/evaluable/blocked hypothesis inventory and correction denominators; neither silence nor cherry-picking.
UX-07: only supported tool-defined associations appear; observational data never described as proof of cause.
UX-08: tool failure, timeout, unsupported questions and missing sponsor credentials produce labeled comprehensible UI states without displaying secrets.
UX-09: synthetic dataset labeling always visible; clinical scope and absence of medical diagnosis explicit.
UX-10: keyboard-only interaction through question, result, evidence, trace and recovery; AA contrast target and mobile viewport without horizontal scroll.
UX-11: clean start from public repo on an independent machine without original private PHIS, private health data or hidden environment; sample mode explicitly marked.
UX-12: real Zetaris query evidence, Nemotron model response and substantive Meterless consumption when chosen; Cursor development use recorded.
UX-13: actual video matches verified feature list, no manufactured numeric metrics.
UX-14: founder visual sign-off after running app; no critical merge/deployment without test evidence.

## 8. Worker execution slices, only from authorized start

Build 1 (P0): shell/design tokens/header/question input and state machine, with static fixture UI *only after event opens*; no fake evidence passed as live.
Build 2 (P0): real allowlisted tool wiring and evidence components; chart missingness, scope checks, block/abstain states; verify against contract.
Build 3 (P0): genuine sponsor call traces and contextual follow-up with clean start.
Build 4 (P0): responsiveness, keyboard/contrast, video capture and README with provenance.
Do not activate optional features until all core tests pass.

## 9. Rejected product patterns

- Fixed question buttons that return canned outputs while pretending to be agentic.
- LLM-generated statistical values or rewritten source evidence.
- Decorative sponsor logos without integrated calls.
- Four dashboards, dozens of metrics and untested personalization.
- Confident causal or medical recommendations; hiding uncertainty.
- Production/private health data in public examples.
- Shipping slides or screenshots depicting UI features that were never actually built.

## 10. Open gates

Organizer binding official rules and prior-code/track response; final sponsor access and credit instructions; approved private-to-public source file manifest; full Discovery unit test execution and scientific fixture results. This document decides UX behavior, not rule eligibility or technical readiness.

Next packet: binding rules and sponsor access GO/NO-GO review plus Oct 22 worker delivery work orders with explicit evidence/rollback points. Founder effort: only final visual approval and unavoidable logins.
