# English + Zetaris release candidate consolidation · 2026-10-22

Base: PR #6 (`74313b4`). Applied PR #9 English-first UX (`7e6a479`), PR #10 live synthetic Zetaris path (`a4bbc6e`), and the test-only adversarial commit from PR #8 (`08c2d95`) on an independent branch. No merge to `main`, deployment, private PHIS data, or Meterless work.

## Gates

| Gate | Result | Evidence and limit |
| --- | --- | --- |
| Python unit, handler, and adversarial tests | **PASS** | `python -m unittest discover -s tests -q` · 55 tests. |
| PR #8 adversarial battery alone | **PASS** | `python -m unittest discover -s tests -p test_adversarial_battery.py -q` · 14 tests. Its standalone response builder is a separate test model; this is not live Zetaris proof. |
| Frontend contract tests | **PASS** | `node --test frontend/tests/*.test.mjs` · 8 tests, including proof mismatch and source failure. |
| Chrome desktop/mobile and accessibility checks | **PASS** | Existing socketless E2E: English copy, keyboard access to source records, mobile overflow, error and abstention states. |
| Native HTTP API investigation | **PASS** | `python tests/native_http_e2e.py` over real `127.0.0.1` sockets; 84-day local synthetic result. |
| Native HTTP follow-up after API restart | **PASS** | New server instance recovered the previous World Model decision from disk. |
| Native HTTP live-mode failure | **PASS** | With no Zetaris configuration: `source_error`, abstention, zero coverage/series, null comparison, `NOT_CONNECTED`; no fixture fallback. |
| Native HTTP Chrome desktop/mobile | **PASS** | Chrome loaded PHIS static assets and POSTed to Python over actual loopback HTTP. Follow-up after restart and live-source failure were checked. |
| Verified live Zetaris read in this worktree | **BLOCKED** | The local Zetaris endpoint answers HTTP but this process has no `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, or `ZETARIS_API_KEY`. No positive `VERIFIED` proof or live-success screenshot is claimed for this consolidation run. PR #10 documents an earlier successful live probe, which is upstream evidence rather than an independently repeated result here. |
| Secrets/private data review | **PASS** | No credentials, tokens, raw responses, private SQLite files, or real health records added. Browser captures show only synthetic IDs. |

The default sandbox blocked loopback sockets (WinError 10013). The two native HTTP commands passed with a local-only sandbox exception. No external connection or paid service was used for those tests. Zetaris service availability was checked read-only on localhost; its API returned HTTP 400 without authentication.

## Real Chrome screenshots

- [Native HTTP desktop result](evidence/consolidated-http-desktop.png)
- [Native HTTP follow-up](evidence/consolidated-http-followup.png)
- [Native HTTP mobile result](evidence/consolidated-http-mobile.png)
- [Native HTTP unverified Zetaris abstention](evidence/consolidated-http-source-error.png)
- [Keyboard source evidence](evidence/en-desktop-evidence.png)

The unverified screenshot explicitly says no records were published. The mode badge says Zetaris is required and unverified. The UI does not claim a query took place when the source failed.

## Run and clear the remaining gate

For the runnable local mode:

```powershell
$env:PYTHONPATH='src'
python -m phis_open_agent.api
```

Open `http://127.0.0.1:4173`. The local mode uses only fictional fixtures and identifies every sponsor as disconnected.

For live Zetaris, provision the already documented local service with the synthetic CSV. Set `PHIS_DATA_MODE=LIVE_SYNTHETIC_ZETARIS`, `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, and `ZETARIS_API_KEY` only in the PHIS process environment. Keep their values out of transcripts, source files, browser URLs, and screenshots. Then run `python tests/native_http_e2e.py --live` and `node frontend/tests/e2e_http_chrome.mjs --live` with an existing Playwright installation. These commands require a `PASS` response with `zetaris: VERIFIED`, a matching request ID in `zetaris.synthetic_query`, 156 fictional source IDs, and a verified follow-up after restart. Until that gate passes in the consolidation environment, this branch remains a Draft PR.

See [frontend instructions](../frontend/README.md) for prerequisites and commands. The `investigation.v1` extension adds only the distinct live mode and optional query metadata. Deterministic calculations still run in Python on returned rows; no frontend calculation or silent local fallback was added.
