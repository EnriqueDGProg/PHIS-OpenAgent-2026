# Zetaris local pull checkpoint — 22 October 2026

**State: BLOCKED pending image download and a real SQL response.** This checkpoint supersedes the earlier registry-login failure in [the live-probe audit](SPONSOR_LIVE_PROBE_STATUS_2026-10-22.md). The user completed `docker login` privately; the Docker config contains an entry for the official registry, and the vendor `preflight.sh` now passes every required check. No images were reported complete, no containers were started, and neither `SELECT 1` nor a synthetic query has been sent. The user reports the image download is still in progress. The interrupted Codex turn did not capture its final exit code; **do not start another pull until the existing download's outcome is known**.

## Proven local prerequisites

| Check | Result |
| --- | --- |
| Source | Authenticated Zetaris Cloud Gateway `Run locally` ZIP; 27,996,894 bytes, 19 entries, no unsafe extraction paths. Unpacked under `%LOCALAPPDATA%`, outside Git. Its `.env` and registry credentials remain private. |
| Docker | Signed Docker Inc. Desktop 4.96.2; Linux server 29.9.2, Compose 5.6.1, WSL2 backend, 20 CPUs. The Docker installer matched the winget SHA-256. |
| Vendor preflight after registry login | **6 PASS, 1 WARN, 0 FAIL.** The warning is 7 GiB available to Docker after integer truncation versus 8 GiB recommended; the vendor minimum is 6 GiB. Do not expand memory without first reporting a real failure. The 504 GB disk figure came from Git Bash and may describe the Windows mount rather than Docker's image store. |
| Network exposure | A private local edit binds UI port 3000 to `127.0.0.1`. The validated Compose also binds active API ports 8888/8889, JDBC 10000, Spark UI 4040 and optional ports to loopback. The `tls` profile is inactive. |
| Runtime limits | The private `.env` sets driver memory to 2 GB, driver cores to 2 and API max heap to 1 GB. Telemetry was explicitly set to `false` in that private copy. |
| Synthetic source | A fictional 156-row CSV was generated outside the repository; SHA-256 `7f97f660600fa2fd592b70a707ddf4db94420b4af6ee3ab281b90ddbb61641a5`. It has not been uploaded or queried. |
| Pull | The first attempt failed before download because Docker's credential helper was absent from that shell's `PATH`. A second pull using the installed helper began and was still active at the last observation. Completion remains **unverified**. |

## Resume once the current pull finishes

Work only in `%LOCALAPPDATA%\PHIS-OpenAgent-2026\zetaris-local\zetaris-platform`. Keep this folder and its `.env` out of the public repository.

1. Confirm the **existing** pull ended successfully, then make one `docker compose images` check against the Compose file. Do not launch a duplicate pull while it is active.
2. If the expected Zetaris driver, API and UI images plus `postgres:16-alpine` are present, run `docker compose up -d` once, without the `tls` profile. Inspect `docker compose ps` and the vendor `verify.sh` after startup. If memory or health checks fail, record the failure and stop before increasing resources.
3. Only when API and driver are healthy, obtain local authentication through the documented platform UI/JDBC path without exposing secrets. Run `SELECT 1`, then place only the fictional CSV at a verified server-visible path and run the bounded synthetic query using [the documented REST activation workflow](ZETARIS_REST_ACTIVATION.md). Record request IDs, row count, SQL hash and source IDs, never passwords or raw responses.
4. Keep `investigation.v1` Zetaris status `NOT_CONNECTED` until a real response and readback pass. Local unit tests and a successful Docker preflight are separate evidence classes.

No AWS account, paid deployment, Meterless binary, private PHIS data, merge, or frontend change is part of this checkpoint. Direct NVIDIA and Meterless Power remain blocked on their separate authentication/provenance gates.
