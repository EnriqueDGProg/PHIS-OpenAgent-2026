# Reproducible local example inputs and outcomes

Run the [README](../README.md) setup with default `SYNTHETIC_LOCAL_ONLY` mode. These are real localhost outcomes recorded on 25 October 2026 against PR #43 application code, with a local Engine state namespace. Run IDs change on replay; statuses, source mode and boundaries are what the example illustrates. No sponsor API was called.

| Input | Observed output |
| --- | --- |
| “What patterns are associated with my energy over the last 180 days?” | `SYN-RUN-1a14ebc22035`: `PASS`, Energy family, Energy measured 170/180 days, Sleep measured 169/180; Zetaris/Nemotron `NOT_CONNECTED`, Meterless Engine `VERIFIED`. |
| “What should we investigate next?” with prior Energy run `SYN-RUN-1a14ebc22035` | `SYN-RUN-a1524327e732`: `PASS`, parent ID preserved, Sleep selected from World Model context; Zetaris/Nemotron `NOT_CONNECTED`. |
| “Can you diagnose my illness?” | `SYN-RUN-9ba0ef0d3d59`: `BLOCKED`, reason `unsupported_question`; no investigation family, measured coverage or clinical answer. |

These local examples do not demonstrate authenticated Zetaris or hosted NVIDIA; see the [separate actual combined receipt](FINAL_COMBINED_RECEIPT.md). Exact JSON values and scientific details come from the API, not this summary.
