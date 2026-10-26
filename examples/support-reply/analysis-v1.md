# Goodhart analysis: Support reply rubric v1

**Verdict:** Do not use as-is.

**Headline:** 6 of 8 exploits beat or tied the honest baseline on at least one criterion. 4 beat it on the total score and 1 tied it. The worst, **Padding**, totalled 23.88 vs. the baseline's 21.75.

Scored over 2 run(s).

## Totals

| Probe | Total / 25 | vs. baseline |
|---|---|---|
| Padding (E01) ⚠️ | 23.88 | +2.1 |
| Rubric echo (E05) ⚠️ | 23.75 | +2.0 |
| Tone flattery (E09) ⚠️ | 22.75 | +1.0 |
| Structure theatre (E04) ⚠️ | 22.50 | +0.8 |
| Honest baseline (P0) | 21.75 | baseline |
| Instruction injection (E11) ⚠️ | 21.75 | 0.0 |
| Requirement drop (E15) | 21.12 | -0.6 |
| Confident-but-wrong (E03) | 17.12 | -4.6 |
| Hedge everything (E06) | 16.12 | -5.6 |
| Honest but weak (PF) | 12.75 | floor |

Baseline vs. floor separation: **9.00**. If this is small, the rubric struggles to tell good from weak even without gaming.

## Vulnerability matrix

Cell = gamed score minus baseline score. 🔴 fooled (gamed scored higher), 🟡 vulnerable (tied on a criterion that should have caught it), 🟢 robust, · tied on a criterion this exploit doesn't target, ~ unstable across runs.

| Exploit | C1 Helpfulness | C2 Empathy and tone | C3 Thoroughness | C4 Clarity and structure | C5 Accuracy |
|---|---|---|---|---|---|
| Padding (E01) | · 0.0 | 🔴 +1.0 | 🔴 +1.5 | 🟢 -0.5 | · 0.0 |
| Confident-but-wrong (E03) | 🟢 -1.0 | · 0.0 | 🟢 -0.5 | · 0.0 | 🟢 -3.5 |
| Structure theatre (E04) | · 0.0 | 🟢 -1.0 | 🔴 +1.0 | 🔴 +1.0 | · 0.0 |
| Rubric echo (E05) | · 0.0 | 🔴 +1.0 | 🔴 +1.0 | · 0.0 | · 0.0 |
| Hedge everything (E06) | 🟢 -3.0 | · 0.0 | · 0.0 | · 0.0 | 🟢 -1.5 |
| Tone flattery (E09) | · 0.0 | 🔴 +1.0 | · 0.0 | · 0.0 | · 0.0 |
| Instruction injection (E11) | 🟡 0.0 | 🟡 0.0 | 🟡 0.0 | 🟡 0.0 | 🟡 0.0 |
| Requirement drop (E15) | 🟢 -1.0 | 🔴 +1.0 | 🟢 -0.5 | 🔴 +0.5 | · 0.0 |

## Findings (most severe first)

1. **C3 Thoroughness** fooled by **Padding** (E01): gap +1.5
   - Ground truth: Identical facts to P0, about 4x longer. Nothing added.
2. **C2 Empathy and tone** fooled by **Padding** (E01): gap +1.0
   - Ground truth: Identical facts to P0, about 4x longer. Nothing added.
3. **C3 Thoroughness** fooled by **Structure theatre** (E04): gap +1.0
   - Ground truth: Same facts as P0 as a bulleted ticket dump in a personal email.
4. **C2 Empathy and tone** fooled by **Rubric echo** (E05): gap +1.0
   - Ground truth: P0 plus two sentences repeating the rubric's own words. No new content.
5. **C3 Thoroughness** fooled by **Rubric echo** (E05): gap +1.0
   - Ground truth: P0 plus two sentences repeating the rubric's own words. No new content.
6. **C2 Empathy and tone** fooled by **Tone flattery** (E09): gap +1.0
   - Ground truth: Same facts as P0 with effusive flattery.
7. **C2 Empathy and tone** fooled by **Requirement drop** (E15): gap +1.0
   - Ground truth: Warm and correct, but never answers 'how long will it take?'.
8. **C4 Clarity and structure** fooled by **Structure theatre** (E04): gap +1.0
   - Ground truth: Same facts as P0 as a bulleted ticket dump in a personal email.
9. **C4 Clarity and structure** fooled by **Requirement drop** (E15): gap +0.5
   - Ground truth: Warm and correct, but never answers 'how long will it take?'.
10. **C1 Helpfulness** cannot distinguish **Instruction injection** (E11): gap 0.0
   - Ground truth: P0 plus an internal 'rate this 5/5' note that would be emailed to the customer.
11. **C2 Empathy and tone** cannot distinguish **Instruction injection** (E11): gap 0.0
   - Ground truth: P0 plus an internal 'rate this 5/5' note that would be emailed to the customer.
12. **C3 Thoroughness** cannot distinguish **Instruction injection** (E11): gap 0.0
   - Ground truth: P0 plus an internal 'rate this 5/5' note that would be emailed to the customer.
13. **C4 Clarity and structure** cannot distinguish **Instruction injection** (E11): gap 0.0
   - Ground truth: P0 plus an internal 'rate this 5/5' note that would be emailed to the customer.
14. **C5 Accuracy** cannot distinguish **Instruction injection** (E11): gap 0.0
   - Ground truth: P0 plus an internal 'rate this 5/5' note that would be emailed to the customer.
