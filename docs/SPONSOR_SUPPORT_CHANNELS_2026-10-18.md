# Sponsor support channel audit — 2026-10-18

Status: four authenticated HackOS sponsor channels inspected read-only. Thread replies not expanded unless already inline. No credentials, accounts, SQL or code operated.

## Exact channels inspected
- Help Zetaris: https://hackathon.genai.works/messages?c=01a11576-b53e-7d46-8e41-db35dc58fa4a
- Help Meterless: https://hackathon.genai.works/messages?c=01a11579-d1c7-70c6-b29e-7133f7aac65e
- Help Cursor: https://hackathon.genai.works/messages?c=01a1157c-1d36-7036-b546-844df875788d
- Help NVIDIA Tools: https://hackathon.genai.works/messages?c=01a11575-b197-7667-a174-7eb2f18c444b

## Evidence
Zetaris channel: multiple participants ask whether advertised free shared event instance will be provisioned and if it satisfies mandatory integration; participants also report Docker memory needs and credit-card/AWS limitations. A participant reports working local JDBC queries against own Parquet data; this is a third-party success report, not our tested capability. No organizer shared instance endpoint, namespace, license terms or provision timing visible in main messages. Some messages contain expandable replies not inspected.

Meterless channel: documented dispute between implementing H-MEM/World Model/Markovian reference engines versus use of inference runtime with METERLESS_API_KEY and METERLESS_BASE_URL. Some guides describe Nemotron through Meterless while agent-engine README says provider-agnostic reference services. No authoritative answer, working endpoint, key redemption or model list visible in unexpanded main channel. Several message replies exist but are not expanded. DO NOT claim one path satisfies eligibility.

Cursor channel: an organizer/representative reply on Oct 15 said access would be provided 'soon'; credit and enrollment still unresolved, and users observe placeholder redemption instructions. No proof free tier suffices, nor that our own entitlement is enabled.

NVIDIA Tools channel: participants ask delivery channel and alternatives for phone-restricted countries, including whether Nemotron via another provider counts. No reply or verified provisioning in visible main messages.

## Reconciled constraints
Binding event rules §5.1: REAL Zetaris and Meterless integration mandatory for every submission, and Cursor must be used for development. §5.2: NVIDIA where valuable. Demo video 1–4 min, slide deck, public source/README and sponsor explanations mandatory. PHIS chooses provisional Track 02; track-preexisting-component interpretation unanswered.
Sponsor activation is a blocking external dependency, not yet an individual failure of our team.
Do not pay AWS or install heavy local Zetaris without verified path and resource budget. Architecture keeps bounded provider adapters; Meterless minimum genuine producer/persistence/consumer interaction, with objective runtime trace and no false assertion of eligibility until organizers confirm.

## Updated risk disposition
R1 HIGH CRITICAL PATH — Zetaris access/hosted-vs-local uncertainty. Escalate sponsor channel and inspect official email/updated resources.
R2 HIGH CRITICAL PATH — Meterless qualification/API ambiguity. Inspect reply threads and official docs, ask targeted organizer question if none conclusive.
R3 MED-HIGH — Cursor credits and environment, access promised but undelivered.
R4 MED — NVIDIA key/model, optional under §5.2 but strategically valuable.
R5 HIGH — local Docker RAM+CPU load and/or unapproved AWS charges. No install/cost authorization.
R6 HIGH — start of coding window; no competition implementation until Oct 22 00:00 UTC.

## Next bounded step
Inspect expanded specific Meterless thread replies first (question from Oct 13 and thread from Oct 15), then Zetaris reply dated Oct 15 and Cursor reply dated Oct 16. If no authoritative clarification, draft exact short sponsor-channel questions and wait on organizers, while preparing code-free activation runbook. No secrets.
