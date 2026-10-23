# Proposed PHIS Discovery NOTICE and MIT license text — review only

**Status: proposal, not a license selection or publication grant.** No `LICENSE` file or SPDX header is added by this branch. The copyright holder, rights scope and exact publication set require the owner's written decision. Replace the bracketed field only after that decision. This document must not be treated as permission to publish the five private files or their archive.

## Proposed provenance NOTICE for an approved later release

> PHIS Discovery scientific modules: `discovery_features.py`, `discovery_signals.py`, `discovery_shapes.py`, `discovery_temporal.py`, `discovery_v11.py`.
>
> Status: **PREEXISTING PHIS**. Original private repository: `EnriqueDGProg/PHIS`, commit `516e3388ce67061028c1b1b29afb4a4ed965a2e0` (before the Open Agent Hackathon 2026 build window). Original Git blob IDs, in the order above: `add62ef0fe925ac264a1c87672ae2feb56cb235b`, `94a30eac8ff670653c764f949b32df7e7730849c`, `4d455ca190db0affa84e01e6741a1b4478000289`, `b3beede8c1ad0f804b29e47b73f5205e86a21694`, `92ad6ebc98274eb51832426ed6993962963f2aac`.
>
> If released unchanged, each public file should retain byte identity with its stated original blob. Any later modification must identify the changed public commit and must not be represented as original PHIS code.
>
> The package initializer, packaging metadata, release gates, synthetic datasets and tests, competition-specific adapters, evidence contracts, plans, orchestration and UI are **NEW** work in the public repository during the competition window. Cite their actual public commits at release review. The existence of a preexisting statistical engine does not make new integration code preexisting, and new integration does not make the five algorithms new.
>
> The separately vendored Meterless World Model in public RC PR #13 carries Apache License 2.0 and its own license file. Retain that license and any applicable upstream notices. Do not relabel the vendor subtree as PHIS or MIT-only work.
>
> All public example observations are fictional and synthetic. No private PHIS health data, SQLite database, personal export, report or credential is part of this release.

The exact public NOTICE should be shortened or expanded after a reviewer checks the actual approved release tree, upstream vendor notices and final file-level provenance.

## Proposed MIT text if the owner selects MIT

The owner must decide whether this covers the five extracted files alone or the first-party public repository as a whole. The separately Apache-2.0 licensed vendor subtree keeps its own license. Replace `[OWNER-CONFIRMED COPYRIGHT HOLDER]` with the legally correct name and confirm the year before creating a real `LICENSE` file.

```text
MIT License

Copyright (c) 2026 [OWNER-CONFIRMED COPYRIGHT HOLDER]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Approval requested later:** exact five blob IDs; legal copyright holder and contributor/third-party provenance; MIT or another chosen license and its scope; final NOTICE and vendor obligations; resolved wheel/Python 3.11 or approved zipimport alternative; public PR head SHA; independent clean-clone verification. No one of these alone authorizes merge, deployment or submission.
