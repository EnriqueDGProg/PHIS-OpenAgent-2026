# Execution gate and call evidence — 22 October 2026

This is the evidence state for [draft PR #3](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/3). `PASS` means the named check passed; it does not imply submission readiness. No credentials, private observations or PHIS source were used.

## Binding rules and reuse

The [organizer's live ten-section event rules](https://hackathon.genai.works/event/open-agent-hackathon-2026#rules) were expanded and read again on 22 October, rather than using the `Official Rules (WORKING DRAFT)` file in HackOS Resources. Sections 4.1–4.2 establish the 22–27 October build window and declaration of pre-existing components; §5.1 requires **Zetaris, Meterless and Cursor** for every submission; §5.2 says NVIDIA where it contributes; §5.4 requires declaring pre-existing product code. §6 requires the public repo/README, 1–4 minute real demo video, deck and sponsor explanation.

[Track 02](https://hackathon.genai.works/event/open-agent-hackathon-2026#tracks) describes evidence-backed investigation across data sources. Wildcard expressly covers existing projects extended with sponsor tools and scores new work. The binding ten sections do **not** explicitly say that declared prior components force Wildcard. Therefore Track 02 is provisionally suitable for this new public work, while any later PHIS code reuse stays on hold pending owner rights review and organizer interpretation. The public branch imports **zero** private PHIS modules. Its private baseline reference is an audit SHA, not copied code or data. No license is selected here.

## PASS / FAIL / BLOCKED

| Check | State | Verifiable evidence and limit |
| --- | --- | --- |
| Branch and review | PASS | `codex/build-window-audit-20261022` published; draft PR #3 targets `main`, no merge. |
| Initial synthetic core | PASS | Six original unit tests passed; expanded local suite passes nine tests; 84 fictional calendar days and two source types. |
| Secret/PII/private-code boundary | PASS for PR diff | Changed files reviewed; pattern scan for common tokens, keys, email addresses and database filenames returned no hits. No specialized scanner installed. Public code has no private imports. |
| Binding sponsor rule | PASS | Live §5.1 requires Zetaris, Meterless, Cursor. |
| Track 02 eligibility with PHIS reuse | BLOCKED | No explicit forced-Wildcard clause found; owner/organizer ruling for any private-code reuse still absent. Current branch uses none. |
| Zetaris login | PASS | Cloud Gateway dashboard accessible, zero active computes, zero usage and $0 cost. |
| Zetaris real query | BLOCKED | No active compute, query endpoint or team namespace; `SELECT 1` and synthetic data query **not executed**. Local `docker` command unavailable. [Zetaris install guide](https://zetaris.github.io/getting-started/docs/install/choose-install.html) says local needs Docker with ~8 GB RAM and 4 CPUs; AWS incurs AWS resource charges unless this account's credits cover them. [Help Zetaris](https://hackathon.genai.works/messages?c=01a11576-b53e-7d46-8e41-db35dc58fa4a) sponsor reply says a team needs its own instance, not a general hosted/shared free instance. No paid deployment authorized. |
| Synthetic Zetaris input | PASS locally | `zetaris_export.export_csv` writes only allowlisted fictional columns; its test checks schema, two fictional source types and overwrite refusal. No Zetaris table created. |
| Meterless Build slice | PASS locally / full integration BLOCKED | Original append-only run-state slice based on [Meterless World Model specification](https://github.com/Meterless/Meterless/tree/main/engines/world-model) was tested producer→persist→read→consumer, idempotency and provenance rejection. No official conformance suite run; this is not full engine certification. |
| Meterless Power / Nightshift | BLOCKED | [Help Meterless](https://hackathon.genai.works/messages?c=01a11579-d1c7-70c6-b29e-7133f7aac65e) organizer reply says Build and Power both required, with Nightshift as primary provider. It also says the web edition has no external-app API, Windows 1.2.1 is unsigned and checksum guidance needs correction. No trusted local runtime, endpoint, token or real inference call available here. No unsigned installer executed. |
| Nemotron | BLOCKED | Direct NVIDIA use is allowed for development/testing per organizer support; no key is configured in this checkout and no model request was sent. No Nemotron module or mock call is presented as working. |
| Cursor | BLOCKED | Effective entitlement and material use in this branch were not verified. Coding in Codex does not satisfy the Cursor rule. |
| Frontend contract | PASS as proposal | `contracts/investigation.v1.schema.json` and `.d.ts` define modes, null gaps, provenance, run/tool states and honest sponsor proof statuses. Sent to the separate frontend worker for review; the 42-day UI fixture and 84-day backend fixture remain distinct local demos. No frontend worktree was modified. |

## Calls actually made

| System | Operation | Result |
| --- | --- | --- |
| Public organizer page | Read and expand all ten rule sections | Real page read; clauses listed above. |
| Authenticated HackOS Resources | Open `Official Rules` | Real page read; file explicitly says WORKING DRAFT, so not used as binding authority. |
| Authenticated Help channels | Read Zetaris and Meterless sponsor replies | Real support messages; clarified own instance and Build+Power, respectively. |
| Zetaris Cloud Gateway | Read dashboard | Real account page: 0 active computes and no query. |
| Python local core | Execute unit suite and synthetic CLI | Real local process; test count and output recorded below. |
| Zetaris SQL, Meterless Runtime, NVIDIA API | No call | BLOCKED; no request ID or returned row/model output exists. |

The local World Model event digest and follow-up selection are reproducible **local execution evidence**, not proof of Nightshift, a hosted Meterless API or a scientific association. No sponsor mock is labeled as real.

## Reproduction and next gate

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m phis_open_agent
python -c "from phis_open_agent.zetaris_export import export_csv; print(export_csv('synthetic_observations.csv'))"
```

The CSV command is optional preparation and creates a fictional local file; do not commit it as a live query trace. A real Zetaris proof requires an approved no-charge instance or explicit cost approval, then documented `SELECT 1`, data registration, bounded query over that synthetic file, sanitized result and returned row IDs. A real Meterless Power proof requires a trusted runtime build, working endpoint/token and observed model response. Keep both blocked until those operations complete.

## Access recheck during the build window

This recheck used the authenticated sponsor pages and read-only local inspection. Environment variables named for Zetaris, NVIDIA, Meterless and AWS were checked for **presence only**; none was present. No credential value was printed or saved. No AWS account is configured in the Zetaris Cloud Gateway, and no compute is active. Its AWS Accounts page warns that account setup creates network and storage resources with estimated ongoing charges (about USD $0.045/hour in its example) even without a running cluster. A free Zetaris Hobby subscription therefore does not establish zero AWS cost. The [sponsor's support answer](https://hackathon.genai.works/messages?c=01a11576-b53e-7d46-8e41-db35dc58fa4a) offers an eligible AWS Free Tier account, a team-controlled local/server installation or joining a team with an instance; it does not offer a general shared instance.

The authenticated Gateway's **Run locally** page gives a no-Zetaris-fee Docker Compose route, requiring Docker Desktop, 8 GB allocated to Docker, four CPUs and 15 GB disk, with about 4 GB of images. Its connection proof is JDBC `SELECT 1` at `localhost:10000` after `./verify.sh`. The machine has 15.7 GB physical RAM, 20 logical processors and 443 GB free on C:, but neither Docker Desktop nor WSL is installed. `wsl.exe --install` was attempted after owner authorization; the non-administrator invocation made no change, and the elevated Windows launch returned “operation cancelled.” `localhost:10000` and `localhost:8888` are not serving Zetaris. The [official getting-started preflight](https://github.com/zetaris/getting-started/blob/main/scripts/preflight.py) can verify REST/JDBC `SELECT 1` once the platform is live; its own documentation says it reads credentials without printing them. **No Zetaris SQL was executed in this recheck.**

The [Meterless web edition](https://meterless.ai/Nightshift/WEB/) loaded without an account or paid resource. Its in-tab endpoint test reported `/v1/models` online and 64 model IDs, but explicitly states other applications cannot reach that in-tab endpoint. A real synthetic connectivity job, `job_mvj4ejka01`, completed on 22 October at 05:51 UTC with **16/16 generation attempts failed, zero usable text and no verifier verdict**. Thus web access is **PARTIAL**, generation is **FAIL**, and application-level Meterless Power remains **BLOCKED**. No local Nightshift process or API token was present on ports 8088, 8090, 8787 or 11434. The [Windows edition](https://meterless.ai/windows.html) is offered for dedicated GPUs; installing it has not occurred. The machine's RTX 3050 Laptop GPU has 4 GB VRAM, below the 8/12/24 GB cards discussed in its published performance measurements, so no claim about local model performance is made.

The [NVIDIA build site](https://build.nvidia.com/) displayed a login form and terms acceptance, with no signed-in account or local `NVIDIA_API_KEY`. Its [Nemotron model catalog](https://build.nvidia.com/search?q=Nemotron) advertises free trial endpoints; none was called. Cursor 3.19.7 was installed from the verified official `Anysphere.Cursor` winget package in user scope and launched with this repository. Account sign-in, entitlement and material Cursor development remain unverified. Coding in this PR remains Codex work and is not Cursor evidence.

### Indispensable human interventions

1. **Local Zetaris prerequisite:** an administrator must install/enable WSL2 and reboot Windows if requested. The owner authorized the free local route; the current non-administrator process could not perform that OS step and its elevated launch was cancelled by Windows. After restart, this task can continue with Docker Desktop and the official Zetaris bundle, subject to any installer terms or sign-in that the owner must personally accept. Keep the bundle and credentials outside the public repository.
2. **NVIDIA:** the account holder must sign in to build.nvidia.com, decide whether to accept its displayed Developer Program/Technology Access terms, and make an API key available through a local secret store or environment variable. Do not send the key in chat or commit it.
3. **Cursor:** the account holder must sign in to the installed Cursor and carry out material build work there. Installation alone cannot prove the competition's use requirement.

After a Zetaris instance is running, the next automated gate is official preflight, `SELECT 1`, registration of the fictional CSV, a bounded SQL query, and a sanitized row/trace record. Keep sponsor status BLOCKED until that call succeeds.

### Local setup continuation

On recheck, `wsl --status` still reports that WSL is not installed. The authenticated Gateway's **Run locally** page confirms the Windows/WSL prerequisite, a ~28 MB platform ZIP, ~4 GB of container images, `./preflight.sh`, `./verify.sh`, and JDBC `SELECT 1` at `localhost:10000`. A download attempt from that page returned **Unauthorized**; no `zetaris-platform.zip` appeared in Downloads. No bundle was unpacked, no container was started, and no SQL was sent. The account holder must restore Gateway download authorization if the page continues to reject the request. This is separate from the administrator action needed to enable WSL2.

## Meterless Power / Nemotron continuation

The [Power activation guide](METERLESS_NVIDIA_ACTIVATION_2026-10-22.md) records the 21 October Participant Setup Guide, sponsor support, official Runtime v4 contract, NVIDIA hosted trial route and Windows release provenance. Five new transport tests pass with an injected **SIMULATED** transport; no test can mark Meterless or NVIDIA `VERIFIED`. The complete local suite passes **20** tests. Both production probe CLIs return `BLOCKED` before an HTTP call because the Runtime token and NVIDIA key are absent. Ports 8088, 8090, 8787 and 11434 do not respond on this machine. No Nightshift/NVIDIA inference request, vendor receipt or model output exists.

The official Windows 1.2.1 installer metadata is contradictory: `APP_BUILD_INFO.txt` reports an unsigned 652,773,354-byte setup executable with SHA-256 `4b7e858f2b044c929b93455a607e90fb99804bbe502460818cbcf9c7c9e62a0c`; `SHA256SUMS` and `manifest.json` report SHA-256 `03fd720f65617ff1bb90efaf433b64b65bf6248d5704169c4ad3343821bd1c1f`, and the manifest reports 652,839,099 bytes. No installer was downloaded or run. Direct NVIDIA via its official free trial endpoint is prepared as **partial development fallback**, never as Meterless Power proof. The application still lacks a feature-level Runtime call, and the local Engine slice lacks official conformance evidence. Build, Power and Nemotron therefore remain blocked for competition compliance.

## Direct REST adapter preparation

The [activation guide](ZETARIS_REST_ACTIVATION.md) records the official direct REST paths and file registration syntax used by the new adapter. The local `prepare` command emitted 156 fictional rows with SHA-256 `7f97f660600fa2fd592b70a707ddf4db94420b4af6ee3ab281b90ddbb61641a5`; the CSV is ignored by Git. The registration command was run **without** `--execute` and printed two CREATE statements for review. No Zetaris SQL was sent. The local preflight returned `BLOCKED` before any network request because `ZETARIS_REST_URL`, `ZETARIS_ORG_ID` and `ZETARIS_API_KEY` are absent. The full local suite now passes 15 tests; six new tests use a **simulated transport**, including a guard that refuses `VERIFIED` for a mock. This is code readiness, not sponsor integration proof.
