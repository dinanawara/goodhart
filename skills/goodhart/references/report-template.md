# Report template

Fill this in for `goodhart-run/report.md`. Keep the top section short enough to read in under a minute.

---

# Goodhart report: {rubric name}

**Verdict:** {Safe to use / Use with fixes / Do not use as-is}. {One sentence on the single biggest problem.}

**Headline:** {N} of {M} exploits beat or tied the honest baseline on at least one criterion. {The worst one} scored {x} vs. the baseline's {y} overall.

**Assumptions:** {task inferred? judge type assumed? scoring context-isolated or not? number of runs}

## Vulnerability matrix

{Paste the matrix from analyze.py: rows = exploits, columns = criteria, cells = gap and verdict.}

## Findings

For each FOOLED or VULNERABLE finding, most severe first:

### F{n}. {Criterion} is fooled by {exploit}
- **Evidence:** {probe ID} scored {a} vs. baseline {b}. {Ground-truth note: why the probe is not better.}
- **Why it works:** {the gap from Step 1, in one or two sentences}
- **Fix ({pattern ID and name}):** {exact new wording}

## Hardened rubric

{Full revised rubric, or a link to rubric-hardened.md}

## Before vs. after

| Probe | Total before | Total after |
|---|---|---|
| P0 Honest baseline | | |
| {each gamed probe} | | |

{One line: did the baseline keep its score? If it dropped, say which fix over-corrected.}

## What this test does not cover

{Exploits not tried, LLM-vs-human caveats, sample size.}
