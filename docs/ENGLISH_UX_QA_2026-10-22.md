# English-first UX QA · 2026-10-22

Base: validated integrated release candidate `74313b4` (Draft PR #6). This branch changes judge-facing copy, English intent safety, tests, and documentation. `investigation.v1`, measurements, source record IDs, and sponsor status are unchanged.

## Acceptance evidence

| Check | Result |
| --- | --- |
| Python unit and integration tests | PASS · 37 tests |
| Node client tests | PASS · 6 tests |
| Chrome desktop and mobile, real rendering | PASS · `node frontend/tests/e2e_chrome.mjs` |
| English copy across success, follow-up, insufficiency, failure, and abstention | PASS · static and API output guards plus visible browser text check |
| Keyboard source record inspection | PASS · focus chart point, Enter opens dialog with matching `SYN-` ID, Escape closes |
| Mobile viewport overflow | PASS · 390 px viewport, no horizontal document overflow |
| Secret and private data review | PASS · no added credentials, private records, or real health data; test tokens are explicitly `simulated-token` |

## Real Chrome captures

- [Desktop result](evidence/en-desktop-pass.png)
- [Desktop source evidence](evidence/en-desktop-evidence.png)
- [Desktop persisted follow-up](evidence/en-desktop-followup.png)
- [Mobile result](evidence/en-mobile-pass.png)
- [Insufficient evidence](evidence/en-desktop-insufficient.png)
- [Local tool failure](evidence/en-desktop-error.png)
- [Clinical request abstention](evidence/en-desktop-abstention.png)

The Chrome test uses installed Playwright and Chrome without installing packages. It serves the actual checkout files and invokes the real Python API handler for each POST through a socketless bridge. Each request starts a new Python process, so follow-up exercises persisted World Model state. Sandbox loopback restrictions prevented a browser-to-server HTTP socket test. This is a transport verification limit, not a claim of sponsor connectivity.

The English classifier additionally blocks English requests to prove causation or seek medication/treatment decisions. Spanish input recognition remains in the internal classifier for compatibility, but the judge-facing default, controls, responses, traces, errors, and documentation are English.
