# Source ledger and editorial guardrails

This ledger records what the submission-production workstream actually inspected by 23 October 2026. It is a source map, not a substitute for a fresh final run. Internal PR reports are claims by their authors unless independently re-executed at the release SHA.

## Official organizer material

| Source | What it supports | Limitation / conflict |
| --- | --- | --- |
| [Public event page and official rules](https://hackathon.genai.works/event/open-agent-hackathon-2026), browsed 23 Oct | Build window 22–27 Oct, hard deadline 27 Oct 23:45 UTC; Track 02 wording, Wildcard wording, 100-point scoring, eight deck subjects through expanded §6 as recorded in the repository audit. | Dynamic sections should be re-opened before final submit; the page is binding over support guides. |
| [Current Academy event page](https://academy.genai.works/courses/open-agent-hackathon-2026/details), browsed 23 Oct | Current overview says Cursor **or any AI coding tool**, Meterless Engine, Nightshift/Nemotron; video, deck, repository/README. | The Academy overview is not itself the binding rule text. Search snippets may show stale versions; use the live page. |
| [Authenticated HackOS Submission Form Preview](https://hackathon.genai.works/resources?id=01a08ff1-55f6-7358-9501-cb7f1883e33c), read 23 Oct | Preparation list for name, description, one track, roster, public repo, 1–4 minute video, eight-subject deck, sponsors and preexisting declaration. Says team locks when first submission is created. | Preview explicitly says current form and Official Rules prevail. It still says project was developed in Cursor. |
| [Authenticated live HackOS Submission Hub](https://hackathon.genai.works/submissions), inspected 23 Oct | `Track*`, auto team name, `Description*` 150–2000 chars, `Video*`, `Github Solution*`, `Pitch Deck (Optional)`; 0/3 submissions. Unsaved form was cancelled and returned to “No submissions yet.” | Does not expose separate name, long description, sponsor or preexisting fields in current UI. They may be added or appear later; keep prepared copy and reinspect. |
| [Authenticated Demo Video Guide](https://hackathon.genai.works/resources?id=01a08ff1-562f-733f-9ae0-baf2c7ac152b), read 23 Oct | 1–4 minutes; recommended 2:30–3:30; actual running agent, agent interaction, Zetaris and Meterless; clear audio, readable 16:9 screen, permissionless access, no keys. | Examples claim every model call through Meterless, which PHIS has not proven. Do not copy example claims. |
| [Authenticated Disqualification Checklist](https://hackathon.genai.works/resources?id=01a08ff1-54d4-7755-a317-3c4167175ef8), read 23 Oct | Zetaris as data layer; working Meterless Engine feature **and Nightshift as primary AI provider**; Cursor optional; clean clone, programmatic path, sample mode, generated traces and outputs, no secrets, 1–4 minute video, deck. | Its own preface says Official Rules govern conflicts. This Nightshift gate is materially stricter than the older local status reports; mark blocked until proven or organizer clarifies. |

## Project evidence

| Source | Exact claim used in this pack |
| --- | --- |
| [Issue #1, latest director allocation](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/issues/1#issuecomment-6369620404) | Submission worker restricted to `submission/**`; track recommendation provisional; PR #23 browser QA pending; live 180-day backend concurrently owned; screenshots pending; Cursor/NVIDIA claims must be earned. |
| [Issue #1, scientific audit](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/issues/1#issuecomment-6368899368) | PR #21 benchmark PASS with limitations; PR #22 public-safe prep PASS but no source publication; PR #18 504-slot route not real Zetaris proof; PR #13 different 156-row scenario is prior live proof. |
| [PR #13 and final integration report](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/13) | Local live 156-row Zetaris and official Engine readback/restart; no Nightshift/Runtime/NVIDIA. Real installed Chrome reports exist for that RC. |
| [PR #18 and scientific v2 report](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/18) | Authentic local Discovery v1.1 on synthetic 84-day data, 0 promoted candidates in both families; local Engine follow-up; live 504-slot Zetaris blocked in that PR. |
| [PR #21](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/21) | Predeclared stochastic cases and seeds, 180-day opportunity and held-out failure, negative controls; offline benchmark only. |
| [PR #22 and safe-release report](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/22) | Five-file private baseline manifest, exact-hash packaging guard and rights/license/publication blockers. |
| [PR #23](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/23) | Premium frontend Draft; real final desktop/mobile browser acceptance and integrated screenshots pending per issue #1. |

## Editorial rules for final production

1. Attach every screenshot to its actual run mode, dataset/window, timestamp, commit and trace; otherwise leave the placeholder.
2. Never label a PR #13 live sponsor query as PR #18 or PR #21 scientific validation. Avoid adding the row counts together.
3. Never say “PHIS explains the cause.” Use “investigates associated factors and explains what evidence supports or fails to support.”
4. If the final candidate abstains, make that result central: it shows the verifier working.
5. The simulated equations are generator knowledge, not inference available to the agent. Do not reveal them as if discovered.
6. “Preexisting” and “new” refer to the official 22 Oct 00:00 UTC boundary, not to whether a file was first pushed to the public repo.
7. Keep Meterless World Model Engine, Nightshift Runtime/Power, and NVIDIA model inference as separate proof lanes.
