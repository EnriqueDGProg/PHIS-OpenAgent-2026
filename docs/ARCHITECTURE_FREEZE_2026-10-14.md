# PHIS Open Agent — Architecture Freeze
Approved: 2026-10-14. Preparation only; no competition implementation authorized.

## Mission
Evidence-first personal health intelligence. An exceptional hero journey answers why energy changed over a month without presenting correlation as causation. The platform additionally accepts freely phrased, scientifically bounded questions rather than hard-coded prompts.

## Architecture
User interface (chat, timeline charts, evidence cards) -> agent orchestrator (intent, plan, tool choice, context, verification) -> read-only allowlisted tools (coverage, trend, comparison, association, evidence) -> deterministic PHIS scientific engines and synthetic longitudinal dataset -> grounded response with provenance and abstention.

LLM cannot invent measurements, statistical tests, scientific conclusions or tool outputs. Explicit separation of observation, association, hypothesis and causality. Insufficient data, unsupported question, and tool failure must be understandable interface states.

## Judge testing
P0: energy/symptoms trends; temporal comparisons; bounded evidence investigation; explanation of uncertainty and insufficiency; contextual follow-up. P1: richer stratifications and additional analyses only after verification. Three independent successful queries plus one abstention and one follow-up must pass E2E. No clinical diagnosis or autonomous treatment.

## Repository boundary
PHIS remains private product and scientific source. PHIS-OpenAgent-2026 is standalone public competition deliverable, with synthetic data, reproducible setup and approved extracted modules only. Do not copy entire repo, commit history, private health data or secrets. Component manifest includes PREEXISTING/ADAPTED/NEW, source commit, ownership/license, dependencies, review and tests.

## Sponsor and rules gate
Zetaris, Cursor, NVIDIA Nemotron, and possible Meterless are planned integrations; exact obligations and permitted preexisting code are BLOCKED until binding official rules checked. No integration implementation before official build window.

## Acceptance
Documented real tool calls, verifiable deterministic outputs and provenance; quality gates, abstention, adversarial cases, safe clean-room startup, visually compelling UX, demo video, deck and submission evidence. Founder approves strategic decisions and critical release, workers execute only subsequently approved bounded jobs.

Governance: AI-Venture-OS #117, PHIS-OpenAgent-2026 #1. See EXECUTION_READINESS_2026-10-15.md.
