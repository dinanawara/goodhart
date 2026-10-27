# Report template

Fill this in for `goodhart-run/report.md`. Keep the top section readable in under a minute. Every sentence must be backed by a measured result; if you didn't test it, don't claim it.

---

# Goodhart report: {rubric name}

**Verdict:** {Do not use as-is / Use with fixes / No exploit in this probe set beat or matched the baseline}. {One sentence on the biggest repeatable problem.}

**Headline:** On the original rubric, {N} gamed probes beat the honest baseline consistently and {M} were close. {Worst probe} scored {x} vs. {y}, higher in {k}/{n} runs. Ranking accuracy: {a}% → {b}% after hardening (held-out: {c}% → {d}%).

**How this was scored:** {judge command and model}, one fresh call per response, {n} runs. Contested probes checked by a rubric-free judge. {Anything less rigorous, stated plainly, e.g. "scored by the probe author; preliminary".}

**Scope:** {task(s) tested; for contested-judgment domains: "not validated for this domain"}

## Original rubric: dev results

{Totals table and vulnerability matrix from analyze.py}

## Findings

FOOLED and VULNERABLE only, most severe first. Mention WEAK results in one line as possible noise.

### F{n}. {Criterion} {is fooled by / does not reliably penalize} {exploit}
- **Evidence:** {probe} vs. baseline: gap {g}, higher in {k}/{n} runs. {Ground truth: why the probe is not better.}
- **Why it works:** {the meant-vs-observed gap from Step 1}
- **Fix ({pattern ID and name}):** {exact new wording}

## Hardened rubric

Frozen at SHA-256 `{hash}` before any held-out probe was written. {Link to rubric-hardened.md and a short table of what changed and why.}

## Verification

| Probe set | Ranking accuracy, original | Ranking accuracy, hardened | Clean probes that beat or are close to the baseline (original → hardened) |
|---|---|---|---|
| Dev | | | |
| Held-out, same task | | | |
| Held-out, second task | | | |

{Did any held-out exploit get through the hardened rubric? Did an honest improvement score below the baseline? Report failures as prominently as successes.}

## Disputed and weak results

{Contested probes the rubric-free judge didn't find worse; WEAK cells that may be noise.}

## What this test does not cover

{Exploits not tried, LLM-vs-human caveats, number of tasks, the single-author limitation.}
