# Three-minute demo — narration and second-by-second production storyboard

**Target cut: 03:00 (180 seconds). Script status: CONDITIONAL.** Record a real final run after the final backend and browser gates. Every proposed on-screen trace is a shot instruction, not an assertion that footage exists. Use the exact dataset/window shown by the accepted run. Never composite a sponsor success badge onto an unrelated scientific result. The authenticated [Demo Video Guide](https://hackathon.genai.works/resources?id=01a08ff1-562f-733f-9ae0-baf2c7ac152b) recommends 2:30–3:30, a running system, real sponsor work, readable screen text and a trace, and allows cutting wait time if input/output are real.

## Narration master (~380 words; rehearse to 180 seconds)

**00:00–00:20 — Problem.** “Why has my energy changed lately? For a person looking back over months of fragmented observations, a neat answer can be more dangerous than an honest one. Our proposed entry for *The Agent That Can Explain Why* is PHIS Open Agent. Today the entire demo uses fictional, labeled data.”

**00:20–00:42 — What PHIS does.** “PHIS makes the investigation visible. It shows the longitudinal pattern and missing days, selects which evidence to inspect, and separates an observation from a hypothesis. The goal is a bounded, traceable answer—or an explicit abstention.”

**00:42–01:10 — Genuine agentic workflow.** “The planner interprets the question and coverage. A source tool retrieves the records. Specialized PHIS Discovery tests a predeclared family. The verifier checks whether source IDs, scientific gates and trace agree before response. If evidence is weak, the response says so. The official Meterless World Model Engine stores an event that a later follow-up can read, so the next decision can differ.”

**01:10–01:43 — Real run and science.** “Here is the actual run on the synthetic energy question. Watch the selected tools and source IDs, then the energy timeline and its gaps. A raw correlation is not a verdict: Discovery checks aligned dates, coverage, block stability, multiplicity and temporal validity. In our 84-day local evaluation, strong raw associations did **not** qualify, so PHIS withheld a contributing-factor claim.”

**01:43–02:07 — Sponsor proof.** “Zetaris is the data-access layer: in the verified fallback, a real local query returned fictional records with request and source IDs. The 180-day scientific live path is shown only if its own query-to-Discovery trace is verified. The World Model stores the decision and the follow-up recovers it after restart. These are separate proofs; we do not call an injected fixture a sponsor query.”

**02:07–02:31 — Follow-up and differentiation.** “Now ask the follow-up. The persisted state changes which family PHIS examines. Compare that with a general language model receiving a single prompt: PHIS exposes the plan, deterministic test, source lineage, verification and reason for abstention. It does not invent measurements or convert correlation into cause.”

**02:31–03:00 — Honest outcome and vision.** “The final view tells the user what changed, what remains uncertain, and what evidence supports each statement. The stochastic benchmark reports an opportunity seed, a held-out failure and negative controls; we show all three rather than selecting only the pleasing case. A future consented system could ingest data automatically and help people understand patterns in daily life. That is a roadmap, not a clinical outcome or a capability claimed for this demo. PHIS makes the limits inspectable.”

**Conditional edit before recording:** If final 180-day live Zetaris → authentic Discovery → Meterless proof passes, replace the fallback sentence at 01:43 with the exact verified window, row count and trace IDs. If Nightshift remains unproven, do **not** record this as a submission-ready sponsor demo; the current HackOS checklist expects Nightshift as primary AI provider. If the final scientific result differs, replace the 84-day example with the actual returned state and retain the full limitation.

## Second-by-second storyboard

Each range specifies exact **in/out seconds**, transition and proof artifact. The editor may hold a single real shot across several rows; the table is a timing plan, not fabricated footage.

| Seconds | Frame / action | Audio and verification instruction |
| --- | --- | --- |
| 000–005 | Title: PHIS Open Agent; proposed track and “synthetic demo” label. | Start the user question. Confirm track after founder decision. |
| 005–012 | Show the question in the actual UI at readable zoom. | State user/problem; no health record from a real person. |
| 012–020 | Empty or initial investigation state, not a staged result. | Clarify the harm of an ungrounded neat answer. |
| 020–027 | User starts the longitudinal energy investigation. | Show actual input/click. |
| 027–035 | Timeline enters loading state; missing days visible when returned. | Explain observation versus hypothesis. |
| 035–042 | UI status/evidence affordance. | Introduce abstention; keep synthetic label visible. |
| 042–050 | Actual plan/tool trace begins. | Planner role and conditional choice. |
| 050–058 | Actual source retrieval trace, with safe IDs. | Source tool role; do not expose secrets or raw private paths. |
| 058–066 | Actual Discovery family call and verifier state. | Scientific tool and verification; use only executed trace. |
| 066–070 | Engine event in actual trace. | World Model persistence statement only if receipt visible. |
| 070–079 | Run starts or continues in real browser/API. | Show a real input-to-output sequence; cuts may compress waiting only. |
| 079–090 | Longitudinal chart and gap treatment. | Describe the observed pattern without a fabricated statistic. |
| 090–101 | Discovery evidence panel with real family/child IDs. | Explain why raw association is not qualification. |
| 101–103 | Display actual abstention/uncertainty state. | Use the 84-day local result only if footage belongs to that run. |
| 103–114 | Actual Zetaris query/request proof for chosen run. | For fallback, label “156-row local synthetic proof”; never imply 180-day science. |
| 114–122 | Source record IDs linked to evidence. | Show provenance from query to output. |
| 122–127 | Official World Model event/receipt. | Distinguish Engine from Nightshift inference. |
| 127–135 | Submit a real follow-up. | Contrast with a single prompt, without showing a fake LLM comparison run. |
| 135–144 | After restart, recovered prior Engine state in actual trace. | Show changed family/decision; if restart proof unavailable, omit the restart claim. |
| 144–151 | Verifier or abstention event with source link. | Explain no invented metrics or causal leap. |
| 151–161 | Final answer, limitations and evidence drawer. | Allow reading time; cite exact run IDs on screen if safe. |
| 161–170 | Compact benchmark panel: opportunity, held-out miss, control. | Label **offline benchmark**; no live badge. |
| 170–176 | Roadmap text: consented automated ingestion. | Future tense; no clinical/quality-of-life improvement claim as a measured fact. |
| 176–180 | Closing title, repository URL and synthetic disclaimer. | End exactly within four minutes; target 03:00. |

## Capture and edit rules

- Use authentic Chrome desktop capture of the final integrated app; inspect mobile separately for the deck, not as a substitute for desktop proof.
- Put the exact mode, dataset/window and sponsor status in a visible lower-third only when it agrees with the run trace. Never overlay “live” on local/offline footage.
- Reserve **actual on-screen proof** for Zetaris query/request IDs, Discovery family/child/source IDs, Engine event/receipt and a state-dependent follow-up after restart. Hide credentials, `*.env`, provider dashboards and private source paths.
- Use a clean real run. If two takes are stitched, maintain run continuity or explicitly label the cut. Do not combine a 156-row sponsor call with a 180-day scientific output as though they were one execution.
- Do a read-through with a stopwatch, then shorten narration rather than speeding it until evidence becomes unreadable. Export MP4 with clear audio; test full playback and link access in a private browser window.
