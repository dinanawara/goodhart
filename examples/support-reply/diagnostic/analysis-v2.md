# Goodhart analysis: Support reply rubric v2 (ticket 1, follow-up diagnostic)

**Verdict:** No gamed probes in this set; see ranking.

**Headline:** This set has no gamed probes. Ranking accuracy (good work above gamed and weak work): **100%** of 3 pairs (dev 100% of 1, diagnostic 100% of 1, holdout 100% of 1).

Scored over 5 run(s), judge `claude -p --model sonnet`, one fresh call per response. FOOLED needs a mean gap of at least 0.5 and a higher score in at least 80% of at least 3 runs.

## Totals

| Probe | Set | Total / 25 | vs. baseline | Higher in |
|---|---|---|---|---|
| Honest baseline (P0) | dev | 22.95 | baseline |  |
| Diagnostic: follow-up offer without naming a team (G3) | diagnostic | 22.95 | 0.0 |  |
| Honest variation: adds a follow-up offer (G1) | holdout | 15.00 | -7.9 |  |
| Honest but weak (floor) (PF) | dev | 8.75 | floor |  |

⚠️ beats the baseline consistently · ≈ close or inconsistent · ⚪ disputed (a rubric-free judge did not prefer the baseline)

## Findings

No gamed probes, so no findings. Use the totals and ranking above.

## Contested probes: rubric-free preference

| Probe | Preferred | Baseline / probe / tie votes |
|---|---|---|
| Honest variation: adds a follow-up offer (G1) | probe | 0 / 6 / 0 |
| Diagnostic: follow-up offer without naming a team (G3) | probe | 0 / 6 / 0 |
