# PHIS Discovery provenance and license scope

The five `discovery_*.py` files in this directory are **PREEXISTING PHIS** code,
copied byte for byte from the private `EnriqueDGProg/PHIS` commit
`516e3388ce67061028c1b1b29afb4a4ed965a2e0`, before the Open Agent
Hackathon 2026 build window. The founder and rights holder authorized release
of exactly these five blobs under MIT in the 24 October 2026 comment on
[PR #22](https://github.com/EnriqueDGProg/PHIS-OpenAgent-2026/pull/22).
The copyright name in this directory's `LICENSE` follows the original commit
author name, `Enrique Diaz`; the five paths' two display names share one Git
email identity. No other private PHIS source or data is included.

| Original file | Original Git blob |
| --- | --- |
| `discovery_features.py` | `add62ef0fe925ac264a1c87672ae2feb56cb235b` |
| `discovery_signals.py` | `94a30eac8ff670653c764f949b32df7e7730849c` |
| `discovery_shapes.py` | `4d455ca190db0affa84e01e6741a1b4478000289` |
| `discovery_temporal.py` | `b3beede8c1ad0f804b29e47b73f5205e86a21694` |
| `discovery_v11.py` | `92ad6ebc98274eb51832426ed6993962963f2aac` |

`__init__.py` is **NEW** public packaging code. The MIT license in this
directory covers this `phis_master` package; it does not change the license of
other first-party files in the repository. The independently vendored
`vendor/meterless-world-model/` remains under its own Apache License 2.0,
including its existing `LICENSE` and upstream attribution.

The original scientific modules were not rewritten for the competition.
The source adapter, plans, orchestration, tests, UI and evidence contracts are
separate new public work. All example observations are fictional and synthetic.
