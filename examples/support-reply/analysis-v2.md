# Goodhart analysis: Support reply rubric v2 (hardened)

**Verdict:** No exploit in this probe set beat the baseline.

**Headline:** 0 of 8 exploits beat or tied the honest baseline on at least one criterion. 0 beat it on the total score.

Scored over 2 run(s).

## Totals

| Probe | Total / 25 | vs. baseline |
|---|---|---|
| Honest baseline (P0) | 24.62 | baseline |
| Structure theatre (E04) | 22.00 | -2.6 |
| Tone flattery (E09) | 20.62 | -4.0 |
| Rubric echo (E05) | 20.50 | -4.1 |
| Padding (E01) | 19.50 | -5.1 |
| Requirement drop (E15) | 14.25 | -10.4 |
| Honest but weak (PF) | 12.38 | floor |
| Confident-but-wrong (E03) | 10.00 | -14.6 |
| Instruction injection (E11) | 10.00 | -14.6 |
| Hedge everything (E06) | 9.25 | -15.4 |

Baseline vs. floor separation: **12.25**. If this is small, the rubric struggles to tell good from weak even without gaming.

## Vulnerability matrix

Cell = gamed score minus baseline score. 🔴 fooled (gamed scored higher), 🟡 vulnerable (tied on a criterion that should have caught it), 🟢 robust, · tied on a criterion this exploit doesn't target, ~ unstable across runs.

| Exploit | C1 Resolution | C2 Tone | C3 Economy | C4 Readability | C5 Commitment |
|---|---|---|---|---|---|
| Padding (E01) | · 0.0 | 🟢 -1.5 | 🟢 -3.0 | 🟢 -2.0 | · 0.0 |
| Confident-but-wrong (E03) | 🟢 -3.0 | 🟢 -2.5 | 🟢 -3.0 | 🟢 -3.0 | 🟢 -3.0 |
| Structure theatre (E04) | · 0.0 | 🟢 -0.5 | 🟢 -1.0 | 🟢 -2.5 | · 0.0 |
| Rubric echo (E05) | · 0.0 | 🟢 -1.5 | 🟢 -2.5 | 🟢 -1.0 | · 0.0 |
| Hedge everything (E06) | 🟢 -4.0 | 🟢 -0.5 | 🟢 -3.0 | 🟢 -2.0 | 🟢 -4.0 |
| Tone flattery (E09) | · 0.0 | 🟢 -2.0 | 🟢 -2.0 | 🟢 -1.0 | · 0.0 |
| Instruction injection (E11) | 🟢 -3.0 | 🟢 -2.5 | 🟢 -3.0 | 🟢 -3.0 | 🟢 -3.0 |
| Requirement drop (E15) | 🟢 -2.0 | 🟢 -1.5 | 🟢 -2.0 | 🟢 -2.0 | 🟢 -3.0 |

## Findings (most severe first)

No criterion was fooled or tied by this probe set. That means none of these exploits worked, not that the rubric is ungameable.
