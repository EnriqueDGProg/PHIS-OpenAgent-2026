# Zetaris direct REST activation — synthetic data only

**State: BLOCKED.** This branch contains a direct REST client and simulated transport tests. There is no Zetaris instance, API response, `SELECT 1` result, registered table, or real query trace from this environment. Do not label a unit-test response as sponsor proof.

## Documented interface

The [Zetaris getting-started connection guide](https://github.com/zetaris/getting-started/blob/main/docs/connections/client-setup.md) distinguishes direct REST at `/api/v1.0` from the web UI proxy. Its [direct REST helper](https://github.com/zetaris/getting-started/blob/main/scripts/zetaris_sql.py) uses `GET /datasource/datasources` and `POST /sql-editor/sqls/run`, with bearer API key, numeric `X-Org-ID`, UUID `X-Request-ID`, and JSON `{queryId, sql, source: "SqlEditor", limit}`. This adapter implements exactly that route family. It sends one SQL statement per request and limits results to at most 200 rows. No endpoint was inferred for file upload.

The [Zetaris SQL manual](https://kbase.zetaris.com/knowledge/sql-manual) and [official file-source recipe](https://github.com/zetaris/getting-started/blob/main/open_data/parquet_csv/HOWTO.md) document `CREATE LIGHTNING DATABASE` and `CREATE LIGHTNING FILESTORE TABLE ... FORMAT CSV OPTIONS (PATH ..., header "true", inferSchema "true")`. The PATH must be accessible **inside the Zetaris server**. A CSV on this Windows checkout alone is not an uploaded or registered Zetaris table. The [official File System UI guide](https://kbase.zetaris.com/knowledge/file-system-overview) documents a manual upload control; this branch does not guess its HTTP route.

## Minimal administrator handoff

1. Enable WSL2 with administrator rights, reboot if Windows requests it, and start the owner's approved no-fee local Zetaris stack following the authenticated Gateway **Run locally** instructions. Keep Docker bundle, volumes and any credentials outside this public repo. Do not create an AWS account or paid resources.
2. Restore Gateway download authorization if its ZIP button still returns `Unauthorized`. In the running Zetaris UI, create an API token and read the numeric organisation ID. Set `ZETARIS_REST_URL`, `ZETARIS_ORG_ID`, and `ZETARIS_API_KEY` in the local process environment or a private secret store. Do not send their values in chat, logs or commits. The local REST base in the sponsor guide is `http://localhost:8888/api/v1.0`; remote URLs must use HTTPS.
3. Make the generated CSV visible at a known absolute POSIX path **inside** the Zetaris server, using the platform's documented file upload UI or a verified local mount. Record that server path privately. Only the fixed fictional dataset may be staged.

No administrator action is needed to run the local preparation and simulated tests below.

## Activation commands

From the repo root, with `PYTHONPATH=src`:

```powershell
python -m phis_open_agent.zetaris_cli prepare --out synthetic_observations.csv
python -m phis_open_agent.zetaris_cli preflight
python -m phis_open_agent.zetaris_cli register --server-path /server/visible/synthetic_observations.csv
python -m phis_open_agent.zetaris_cli register --server-path /server/visible/synthetic_observations.csv --execute
python -m phis_open_agent.zetaris_cli query
```

`prepare` writes an allowlisted fictional CSV and reports row count plus SHA-256. It refuses to overwrite a file. `preflight` is read-only: list datasources, then `SELECT 1`. `register` without `--execute` prints the two documented CREATE statements and sends nothing. Before executing them, verify the server path, target namespace ownership and that the database/table do not already exist; the first CREATE changes the instance and will fail if the name is occupied. `query` issues a bounded SELECT, checks all 156 returned rows against the deterministic fictional fixture and returns request/query IDs, a SQL hash, row count and source record IDs. It must return `VERIFIED` only with the production HTTP transport after real preflight and complete readback. No credential or raw HTTP body is printed.

The source CSV and any instance export stay ignored by Git. If the real response format differs from the documented helper, keep status `BLOCKED` and adapt only from the fresh instance OpenAPI specification (`/redoc/docs.yaml`) or a sanitized response trace.

## `investigation.v1` interface for Producto

No schema change is requested. Until a real query succeeds, keep `mode: "SYNTHETIC_LOCAL_ONLY"`, `sponsor_proofs` entry `{sponsor: "zetaris", status: "NOT_CONNECTED", trace_id: null}` and, when live Zetaris was requested, a `tool_trace` entry with `status: "BLOCKED"` and no source IDs. A simulated transport returns that state even when its unit-test fixture contains rows. Only a production HTTP preflight plus synthetic row readback may supply `mode: "LIVE_SYNTHETIC_ZETARIS"`, Zetaris `VERIFIED`, and a matching trace ID with source record IDs. `coverage`, `series`, `comparison` and `findings` still come from the deterministic tool layer; the REST client supplies source rows and proof, not medical or causal conclusions.

Producto confirmed that its PR #4 version of `investigation.v1` already admits these fields and needs no schema change. Its current frontend validator deliberately accepts only local synthetic mode and unconnected sponsors. Producto will adjust that validator only after a real Zetaris response exists; this branch does not modify the frontend worktree.

## Verification performed in this branch

`tests/test_zetaris_transport_simulated.py` injects a non-network transport and checks the official paths, headers, request body, blocking preflight, registration SQL, source validation and the rule that mocks never become VERIFIED. These are **simulated transport tests**, not a successful Zetaris call. Run `python -m unittest discover -s tests -v` with `PYTHONPATH=src` for the full local suite.
