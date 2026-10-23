# Integration visual QA — 2026-10-22

Chrome was pointed at the **running local Python server** on `http://127.0.0.1:4173`; these images are browser captures of executed UI states, not mockups. Every visible value came from the synthetic 84-day Python core through `POST /api/investigations`. Sponsor badges and API proofs remained `NOT_CONNECTED`.

| Capture | Verified state |
| --- | --- |
| [Desktop result](evidence/result-desktop.jpg) | Hero question; 56-day chart with null gaps; 28-day comparison; observation, hypothesis, uncertainty; local tool trace. |
| [Evidence drawer](evidence/evidence-desktop.jpg) | Dataset and window, coverage, source IDs, method and explicit sponsor disconnection. |
| [Mobile result](evidence/result-mobile.jpg) | 390 × 844 viewport, contextual sleep follow-up, stacked cards and chart. DOM width check: viewport 390, document 390, body 390. |
| [Tool error](evidence/tool-error-desktop.jpg) | Synthetic error scenario; no chart or numerical comparison, clear error and abstention. |

## Browser flow checked

1. Hero question returned energy mean 7.0 vs 5.0, with 26 and 27 observed days; these matched the Python core in HTTP E2E tests.
2. Evidence drawer exposed synthetic record IDs, analysis method, blocked Discovery and disconnected sponsors.
3. Follow-up «¿Y cómo cambió mi sueño en ese periodo?» submitted `parent_run_id`, reused the window, executed new sleep tools and showed 7.5 vs 6.5 hours. A browser-discovered ID validation bug was fixed and covered by a client regression test.
4. Medication request showed `BLOCKED` with no series or comparison. Sparse coverage showed `INSUFFICIENT_DATA` and no comparison. Tool error showed `ERROR`, no measurements, and a blocked tool trace.
5. Desktop and 390 px mobile layouts were inspected visually. Mobile had no horizontal overflow. Keyboard focus and chart accessibility are represented in DOM labels; a full assistive-technology audit remains a later release gate.

These screenshots show a **synthetic local integration**. They do not demonstrate Zetaris, Meterless, Nemotron, PHIS private Discovery, or a production agent.
