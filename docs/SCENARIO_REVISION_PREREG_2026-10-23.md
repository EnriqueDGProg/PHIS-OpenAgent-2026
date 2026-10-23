# Synthetic scenario revision preregistration

Recorded before evaluating revision 2 with PHIS Discovery. This document defines one generator-only revision, not a search over policy settings or a guaranteed positive result.

## Baseline review

PR #17 fixed-seed revision 1 has first/middle/final 28-day observed energy means 6.579/6.058/6.001 and sleep means 7.242/7.046/6.939. Its latest-versus-middle energy change is −0.056; it cannot support a substantial recent-decline narrative. Same-day sleep versus energy r is +0.869, which may look unusually neat. Fixed-sample lag-1 correlations are energy +0.018, sleep −0.134, stress +0.044. Recorded counts are 78–83 of 84 per series. Prior Discovery results are in PR #17.

## One revision, fixed before evaluation

Keep the 84-day calendar, six variables, independent negative-control stream, explicit missing rows, fixed seed `20261023`, and the **exact PR #17 hypothesis pairs, lags, routes and scientific thresholds**. Give stress, sleep and energy modest persistence; shift recent stress and caffeine exposure; reduce the deterministic sleep coefficient in energy and add independent noise. Use a new dataset ID and source-ID namespace so no record can be mistaken for revision 1. The equations remain in the offline generator and are never passed to the answering agent.

## Acceptance and stopping rules

Evaluate the first fixed-seed revision once. Descriptive plausibility goals: final minus middle 28-day observed energy mean between −0.80 and −0.25 points, sleep between −0.55 and −0.15 hours; energy/sleep values within declared physiological ranges; at least 70% observed per series; lag-1 energy and stress correlations between +0.10 and +0.65; no main pairwise absolute correlation above 0.85. Scientific goals: full 16-child energy and 16-child sleep families run with the original 999-resample policy; negative controls remain unpromoted; at least one energy contributing factor passes the original engine gates if the data warrant it. Failure of a goal is reported as failure or limitation. No further generator tuning within this work packet and no threshold relaxation.

The primary outcome is the latest-versus-middle **observed** energy difference. Discovery results are independently computed and may disagree with designed mechanisms. No causal, adjusted multivariable or clinical claim follows from the design.
