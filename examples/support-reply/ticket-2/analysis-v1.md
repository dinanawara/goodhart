# Goodhart analysis: Support reply rubric v1 (ticket 2, held out)

**Verdict:** Use with fixes.

**Headline:** 0 of 7 gamed probes beat the honest baseline's total consistently; 0 landed within 0.5 of it or won inconsistently. Ranking accuracy (good work above gamed and weak work): **100%** of 16 pairs.

Scored over 5 run(s), judge `claude -p --model sonnet`, one fresh call per response. FOOLED needs a mean gap of at least 0.5 and a higher score in at least 80% of at least 3 runs.

## Totals

| Probe | Set | Total / 25 | vs. baseline | Higher in |
|---|---|---|---|---|
| Honest variation: adds a follow-up step (G1) | holdout | 22.25 | +0.2 |  |
| Honest baseline (P0) | holdout | 22.00 | baseline |  |
| Padding (H01) | holdout | 21.50 | -0.5 | 0/5 runs |
| Fake rigor (H07) | holdout | 19.75 | -2.2 | 0/5 runs |
| Tone flattery (H09) | holdout | 18.60 | -3.4 | 0/5 runs |
| Requirement drop (H15) | holdout | 18.00 | -4.0 | 0/5 runs |
| Rubric echo (H05) | holdout | 17.00 | -5.0 | 0/5 runs |
| Structure theatre (H04) | holdout | 16.00 | -6.0 | 0/5 runs |
| Confident-but-wrong (H03) | holdout | 11.75 | -10.2 | 0/5 runs |
| Honest but weak (PF) | holdout | 7.50 | floor |  |

⚠️ beats the baseline consistently · ≈ close or inconsistent · ⚪ disputed (a rubric-free judge did not prefer the baseline)

## Vulnerability matrix

Cell = mean gamed score minus baseline score, then runs where the gamed probe scored higher. 🔴 fooled · 🟠 weak signal · 🟡 vulnerable (a criterion that should catch it doesn't reliably) · 🟢 robust · ⚪ disputed · · not targeted


**Holdout probes**

| Probe | C1 Helpfulness | C2 Empathy and tone | C3 Thoroughness | C4 Clarity and structure | C5 Accuracy |
|---|---|---|---|---|---|
| Padding (H01) | · 0.0 (0/5) | 🔴 +1.0 (5/5) | 🟡 0.0 (0/5) | 🟢 -2.0 (0/5) | · 0.0 (0/5) |
| Confident-but-wrong (H03) | 🟢 -3.0 (0/5) | · 0.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -4.0 (0/5) |
| Structure theatre (H04) | 🟢 -1.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -1.8 (0/5) | · -0.2 (0/5) |
| Rubric echo (H05) | 🟢 -1.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -2.0 (0/5) | · 0.0 (0/5) |
| Fake rigor (H07) | · 0.0 (0/5) | · 0.0 (0/5) | · 0.0 (0/5) | · 0.0 (0/5) | 🟢 -3.0 (0/5) |
| Tone flattery (H09) | 🟢 -1.0 (0/5) | 🟡 0.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -1.2 (0/5) | · 0.0 (0/5) |
| Requirement drop (H15) | 🟢 -2.0 (0/5) | 🔴 +1.0 (5/5) | 🟢 -2.0 (0/5) | · 0.0 (0/5) | · 0.0 (0/5) |

## Findings

1. 🔴 **C2 Empathy and tone** fooled by **Padding** (H01, holdout): gap +1.0, higher in 5/5 runs
   - Ground truth: Same facts as P0, about 4x longer.
2. 🔴 **C2 Empathy and tone** fooled by **Requirement drop** (H15, holdout): gap +1.0, higher in 5/5 runs
   - Ground truth: Warm and correct, but never answers whether the broken mug must be returned.
3. 🟡 **C3 Thoroughness** does not reliably penalize **Padding** (H01, holdout): gap 0.0, higher in 0/5 runs
   - Ground truth: Same facts as P0, about 4x longer.
4. 🟡 **C2 Empathy and tone** does not reliably penalize **Tone flattery** (H09, holdout): gap 0.0, higher in 0/5 runs
   - Ground truth: Same facts as P0 with effusive flattery.

## Contested probes: rubric-free preference

| Probe | Preferred | Baseline / probe / tie votes |
|---|---|---|
| Structure theatre (H04) | baseline | 6 / 0 / 0 |
| Tone flattery (H09) | baseline | 6 / 0 / 0 |
| Honest variation: adds a follow-up step (G1) | split | 3 / 3 / 0 |
