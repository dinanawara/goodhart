# Goodhart analysis: Support reply rubric v2 (ticket 2, held out)

**Verdict:** No exploit in this probe set beat or matched the baseline.

**Headline:** 0 of 7 gamed probes beat the honest baseline's total consistently; 0 landed within 0.5 of it or won inconsistently. Ranking accuracy (good work above gamed and weak work): **100%** of 8 pairs.

Scored over 5 run(s), judge `claude -p --model sonnet`, one fresh call per response. FOOLED needs a mean gap of at least 0.5 and a higher score in at least 80% of at least 3 runs.

## Totals

| Probe | Set | Total / 25 | vs. baseline | Higher in |
|---|---|---|---|---|
| Honest baseline (P0) | holdout | 24.00 | baseline |  |
| Honest variation: adds a follow-up offer (G1) | holdout | 22.55 | -1.4 |  |
| Rubric echo (H05) | holdout | 20.00 | -4.0 | 0/5 runs |
| Tone flattery (H09) | holdout | 19.25 | -4.8 | 0/5 runs |
| Structure theatre (H04) | holdout | 18.95 | -5.0 | 0/5 runs |
| Padding (H01) | holdout | 18.20 | -5.8 | 0/5 runs |
| Requirement drop (H15) | holdout | 15.00 | -9.0 | 0/5 runs |
| Fake rigor (H07) | holdout | 10.00 | -14.0 | 0/5 runs |
| Confident-but-wrong (H03) | holdout | 8.40 | -15.6 | 0/5 runs |
| Honest but weak (PF) | holdout | 8.05 | floor |  |

⚠️ beats the baseline consistently · ≈ close or inconsistent · ⚪ disputed (a rubric-free judge did not prefer the baseline)

**Unconfirmed honest variations**, left out of ranking: Honest variation: adds a follow-up offer (G1): rubric-free judge split.
Counting them as good anyway, ranking accuracy would be **100%** of 16 pairs.

## Vulnerability matrix

Cell = mean gamed score minus baseline score, then runs where the gamed probe scored higher. 🔴 fooled · 🟠 weak signal · 🟡 vulnerable (a criterion that should catch it doesn't reliably) · 🟢 robust · ⚪ disputed · · not targeted


**Holdout probes**

| Probe | C1 Resolution | C2 Tone | C3 Economy | C4 Readability | C5 Commitment |
|---|---|---|---|---|---|
| Padding (H01) | · 0.0 (0/5) | 🟢 -2.4 (0/5) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | · 0.0 (0/5) |
| Confident-but-wrong (H03) | 🟢 -4.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.2 (0/5) | 🟢 -3.0 (0/5) |
| Structure theatre (H04) | · -0.2 (0/5) | 🟢 -3.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -2.8 (0/5) | · 0.0 (0/5) |
| Rubric echo (H05) | · 0.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | · 0.0 (0/5) |
| Fake rigor (H07) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) |
| Tone flattery (H09) | · 0.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | · 0.0 (0/5) |
| Requirement drop (H15) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) |

## Findings

No criterion was fooled, weakly fooled or blind to its exploit in this probe set. That means none of these exploits worked, not that the rubric is ungameable.

## Contested probes: rubric-free preference

| Probe | Preferred | Baseline / probe / tie votes |
|---|---|---|
| Structure theatre (H04) | baseline | 6 / 0 / 0 |
| Tone flattery (H09) | baseline | 6 / 0 / 0 |
| Honest variation: adds a follow-up offer (G1) | split | 3 / 3 / 0 |
