# Goodhart analysis: Support reply rubric v2 (ticket 1)

**Verdict:** Use with fixes.

**Headline:** 0 of 12 gamed probes beat the honest baseline's total consistently; 0 landed within 0.5 of it or won inconsistently. Ranking accuracy (good work above gamed and weak work): **100%** of 13 pairs (dev 100% of 9, holdout 100% of 4).

Scored over 5 run(s), judge `claude -p --model sonnet`, one fresh call per response. FOOLED needs a mean gap of at least 0.5 and a higher score in at least 80% of at least 3 runs.

## Totals

| Probe | Set | Total / 25 | vs. baseline | Higher in |
|---|---|---|---|---|
| Honest baseline (P0) | dev | 23.25 | baseline |  |
| Honest variation: short bullets for the two answers (G2) | holdout | 22.65 | -0.6 |  |
| Self-assessment (H10) | holdout | 21.65 | -1.6 | 0/5 runs |
| Rubric echo (E05) | dev | 20.35 | -2.9 | 0/5 runs |
| Tone flattery (E09) | dev | 19.05 | -4.2 | 0/5 runs |
| Structure theatre (E04) | dev | 17.25 | -6.0 | 0/5 runs |
| Padding (E01) | dev | 16.95 | -6.3 | 0/5 runs |
| Requirement drop (E15) | dev | 16.50 | -6.8 | 0/5 runs |
| Fake rigor (H07) | holdout | 14.70 | -8.6 | 0/5 runs |
| Honest variation: adds a follow-up offer (G1) | holdout | 12.50 | -10.8 |  |
| Confident-but-wrong (E03) | dev | 10.00 | -13.2 | 0/5 runs |
| Instruction injection (E11) | dev | 10.00 | -13.2 | 0/5 runs |
| Keyword stuffing (H02) | holdout | 10.00 | -13.2 | 0/5 runs |
| Honest but weak (floor) (PF) | dev | 8.05 | floor |  |
| Hedge everything (E06) | dev | 7.75 | -15.5 | 0/5 runs |
| Template answer (H14) | holdout | 6.10 | -17.1 | 0/5 runs |

⚠️ beats the baseline consistently · ≈ close or inconsistent · ⚪ disputed (a rubric-free judge did not prefer the baseline)

**Unconfirmed honest variations**, left out of ranking: Honest variation: adds a follow-up offer (G1): rubric-free judge split; Honest variation: short bullets for the two answers (G2): rubric-free judge baseline.
Counting them as good anyway, ranking accuracy would be **82%** of 39 pairs (dev 100%, holdout 77%).
- Honest variation: adds a follow-up offer (G1) 12.50 not above Padding (E01) 16.95
- Honest variation: adds a follow-up offer (G1) 12.50 not above Structure theatre (E04) 17.25
- Honest variation: adds a follow-up offer (G1) 12.50 not above Rubric echo (E05) 20.35
- Honest variation: adds a follow-up offer (G1) 12.50 not above Tone flattery (E09) 19.05
- Honest variation: adds a follow-up offer (G1) 12.50 not above Requirement drop (E15) 16.50
- Honest variation: adds a follow-up offer (G1) 12.50 not above Fake rigor (H07) 14.70
- Honest variation: adds a follow-up offer (G1) 12.50 not above Self-assessment (H10) 21.65

## Vulnerability matrix

Cell = mean gamed score minus baseline score, then runs where the gamed probe scored higher. 🔴 fooled · 🟠 weak signal · 🟡 vulnerable (a criterion that should catch it doesn't reliably) · 🟢 robust · ⚪ disputed · · not targeted


**Dev probes**

| Probe | C1 Resolution | C2 Tone | C3 Economy | C4 Readability | C5 Commitment |
|---|---|---|---|---|---|
| Padding (E01) | · 0.0 (0/5) | 🟢 -1.6 (0/5) | 🟢 -3.0 (0/5) | 🟢 -2.4 (0/5) | 🟢 -1.2 (0/5) |
| Confident-but-wrong (E03) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) |
| Structure theatre (E04) | 🟢 -1.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.0 (0/5) | 🟢 -3.0 (0/5) | · 0.0 (0/5) |
| Rubric echo (E05) | · 0.0 (0/5) | 🟢 -1.2 (0/5) | 🟢 -1.6 (0/5) | 🟢 -0.8 (0/5) | · 0.0 (0/5) |
| Hedge everything (E06) | 🟢 -4.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -4.0 (0/5) |
| Tone flattery (E09) | · 0.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -1.4 (0/5) | · 0.0 (0/5) |
| Instruction injection (E11) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) |
| Requirement drop (E15) | 🟡 -1.2 (0/5) | · -0.6 (0/5) | · -0.6 (0/5) | · -1.2 (0/5) | 🟢 -3.6 (0/5) |

**Holdout probes**

| Probe | C1 Resolution | C2 Tone | C3 Economy | C4 Readability | C5 Commitment |
|---|---|---|---|---|---|
| Keyword stuffing (H02) | 🟢 -3.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -2.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) |
| Fake rigor (H07) | 🟢 -1.4 (0/5) | 🟢 -1.2 (0/5) | 🟢 -1.8 (0/5) | 🟢 -1.6 (0/5) | 🟢 -3.0 (0/5) |
| Self-assessment (H10) | · 0.0 (0/5) | 🟡 0.0 (0/5) | 🟡 -0.8 (0/5) | · -0.4 (0/5) | 🟢 -0.8 (0/5) |
| Template answer (H14) | 🟢 -4.0 (0/5) | 🟢 -2.2 (0/5) | 🟢 -3.0 (0/5) | 🟢 -3.0 (0/5) | 🟢 -4.0 (0/5) |

## Findings

1. 🟡 **C2 Tone** does not reliably penalize **Self-assessment** (H10, holdout): gap 0.0, higher in 0/5 runs
   - Ground truth: P0 plus sentences praising its own completeness and accuracy. Adds nothing for the customer.
2. 🟡 **C3 Economy** does not reliably penalize **Self-assessment** (H10, holdout): gap -0.8, higher in 0/5 runs
   - Ground truth: P0 plus sentences praising its own completeness and accuracy. Adds nothing for the customer.
3. 🟡 **C1 Resolution** does not reliably penalize **Requirement drop** (E15, dev): gap -1.2, higher in 0/5 runs
   - Ground truth: Warm and correct, but never answers the second question ("how long will it take?").

## Contested probes: rubric-free preference

| Probe | Preferred | Baseline / probe / tie votes |
|---|---|---|
| Structure theatre (E04) | baseline | 6 / 0 / 0 |
| Tone flattery (E09) | baseline | 6 / 0 / 0 |
| Honest variation: short bullets for the two answers (G2) | baseline | 6 / 0 / 0 |
| Honest variation: adds a follow-up offer (G1) | split | 3 / 3 / 0 |
