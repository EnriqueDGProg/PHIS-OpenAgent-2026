# Meterless Power and Nemotron activation — 22 October 2026

## Authority and current state

The authenticated **Participant Setup Guide**, last updated 21 October, describes two distinct Meterless obligations: **Build** uses a working Meterless Engine in an application feature, with a reproducible demonstration and conformance/evaluation evidence; **Power** uses Nightshift Runtime as the application's primary AI provider and proves an actual request/response. The [live event rules](https://hackathon.genai.works/event/open-agent-hackathon-2026#rules) §5.1 require actual Zetaris, Meterless and Cursor use. The guide is operational help, not a replacement for those rules. The [organizer's Help Meterless replies](https://hackathon.genai.works/messages?c=01a11579-d1c7-70c6-b29e-7133f7aac65e) confirm Build plus Power and say the free web edition has no external-application API. One reply phrases provider code integration as enough, but the guide and [Meterless provider contract](https://meterless.ai/engines.html) require a working response; this repo uses the stricter proof gate.

| Obligation | State | Evidence required to change it |
| --- | --- | --- |
| Meterless Build | PARTIAL locally / BLOCKED for full claim | Synthetic append-only World Model-inspired run-state is exercised in this repo; official World Model conformance is not run and no Engine-backed feature is proven. |
| Meterless Power | BLOCKED | Nightshift `GET /v1/models` exposes `meterless/*`, followed by a real `POST /v1/chat/completions` response through the Runtime and a feature using it as primary provider. |
| NVIDIA Nemotron via Nightshift | BLOCKED | Nightshift provider configured with the human's NVIDIA developer key, plus a real Runtime request and receipt identifying the Nemotron lane/model. `meterless/auto` alone cannot prove its chosen backend. |
| Direct NVIDIA API | PARTIAL code / BLOCKED real call | A real response from NVIDIA's free trial endpoint is useful development evidence, but does not establish Meterless Power. |

The LLM modules in `src/phis_open_agent/inference.py` only send a fixed **synthetic connectivity** prompt and check for `READY`. They never calculate health statistics, create findings, or alter the deterministic scientific core. The CLI suppresses prompt, answer and credentials in its output. A local trace ID is only a run correlation marker, **not** a vendor receipt. Injected transport tests are marked `SIMULATED` and produce no trace ID. No sponsor proof in `investigation.v1` should become `VERIFIED` from these tests.

## Official transport contracts and free route

The [Meterless Runtime provider contract v4](https://meterless.ai/engines.html) documents base `http://127.0.0.1:8088/v1`, bearer token, `meterless-app` on every request, `meterless-scope:user` on chat, `GET /v1/models` and `POST /v1/chat/completions`. It says 401/403 means unauthorized, `GET /healthz` proves only a process exists, and chat can take 180 seconds. Our minimal adapter implements discovery and a fixed text probe; it does not claim full provider settings, auto-detection or a production feature yet.

The [NVIDIA Nemotron Lightning build page](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b/build) labels the hosted endpoint **Free Endpoint** and documents model `nvidia/nemotron-3.5-lightning-30b-a3b` at `https://integrate.api.nvidia.com/v1/chat/completions`. This avoids local 30B model download or renting GPU. Trial credits and rate limits apply; free endpoint availability does not prove this account has access. The [NVIDIA model page](https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b) says trial inputs/outputs may be recorded, so probes contain fictional text only. No paid/partner deployment is authorized. NVIDIA's key belongs in Nightshift's Providers settings for the Power path; `NVIDIA_API_KEY` is used only by the **direct fallback** CLI.

The [Meterless home page](https://meterless.ai/) offers free in-browser generation, but explicitly reserves the external-app hotspot for Mac, Windows and DGX editions. The newest Help Meterless Linux/cloud discussion did not provide a sponsored hosted Runtime. Thus no verified free remote Nightshift endpoint exists for this team; a teammate's Nightshift endpoint over a trusted HTTPS connection could work only after actual access and auth details exist. The available Windows laptop has RTX 3050 4 GB VRAM. The [Windows page](https://meterless.ai/windows.html) lists a dedicated GPU, but its measured examples use 8–24 GB; the 4 GB behavior is unverified. NVIDIA-hosted inference through Nightshift would avoid loading Nemotron locally, provided Nightshift itself runs.

## Windows provenance gate — no installation

The [official Windows directory](https://meterless.ai/Nightshift/WIN/) currently lists release files, [build information](https://meterless.ai/Nightshift/WIN/APP_BUILD_INFO.txt), [SHA256SUMS](https://meterless.ai/Nightshift/WIN/SHA256SUMS) and [manifest](https://meterless.ai/Nightshift/WIN/manifest.json). The build information identifies `Nightshift_1.2.1_x64-setup.exe` as **NotSigned**, reports 652,773,354 bytes and SHA-256 `4b7e858f2b044c929b93455a607e90fb99804bbe502460818cbcf9c7c9e62a0c`. The same official directory's checksum file gives that filename SHA-256 `03fd720f65617ff1bb90efaf433b64b65bf6248d5704169c4ad3343821bd1c1f`; the manifest repeats the latter and reports 652,839,099 bytes. These are materially inconsistent. Help Meterless acknowledges the Windows build is unsigned and checksum guidance needs correction. **No Windows installer was downloaded or executed.** A TLS origin plus one matching checksum is insufficient while the release metadata disagree and Authenticode is absent. Wait for corrected, consistent vendor provenance (and preferably a signed build) before installation; do not bypass SmartScreen for this artifact.

## Reproduce safely

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent.inference_cli meterless
python -m phis_open_agent.inference_cli nvidia
```

With no credentials, both CLIs return `BLOCKED` before any HTTP call. Once a trusted Nightshift instance is running, set `METERLESS_BASE_URL`, `METERLESS_RUNTIME_TOKEN` (the real Runtime token, never `rt-local`) and optionally `METERLESS_MODEL=meterless/auto` in the local process environment, then rerun the Meterless CLI. The Runtime token is separate from a NVIDIA provider key. For the partial direct path, obtain a free trial `NVIDIA_API_KEY` in the NVIDIA account, set it locally and rerun the NVIDIA CLI. Never add keys or the Runtime token to a command transcript, public issue, PR, test fixture or repository file. A real response should be followed by a sanitized vendor receipt and a feature-level test before changing compliance status.

## Minimum human actions

1. Meterless must correct the contradictory Windows 1.2.1 checksum/size metadata or supply a trustworthy signed build (or a verified hosted Runtime). Until then, do not install this Windows artifact.
2. The account holder must sign in to NVIDIA Build, accept any applicable trial terms personally and create a free developer API key. Enter it privately into Nightshift's NVIDIA Providers settings when Nightshift is trusted; direct fallback uses a local `NVIDIA_API_KEY` environment variable.
3. If a trusted Runtime becomes available, its operator must share its **base URL and Runtime token privately** with the person running the probe. No token should be sent to this chat or committed.
