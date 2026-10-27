# File formats

## probes.json (you write this)

One file per task. `judge.py` reads it.

```json
{
  "task": "task.md",
  "baseline": "P0",
  "floor": "PF",
  "frozen_rubric": {"file": "rubric-hardened.md", "sha256": "…",
                    "note": "holdout probes were written after this hash was recorded"},
  "probes": [
    {"id": "P0", "label": "Honest baseline", "exploit": null, "set": "dev", "tier": "good",
     "text": "Hi Sam, …"},
    {"id": "PF", "label": "Honest but weak", "exploit": null, "set": "dev", "tier": "weak",
     "text": "…"},
    {"id": "E01", "label": "Padding", "exploit": "E01", "set": "dev", "tier": "gamed",
     "kind": "clean", "should_lose_on": {"original": ["C3"], "hardened": ["C3"]},
     "ground_truth": "Same facts as P0, 4x longer.", "text": "…"},
    {"id": "G1", "label": "Honest improvement", "exploit": null, "set": "holdout", "tier": "good",
     "text": "…"}
  ]
}
```

| Field | Meaning |
|---|---|
| `task`, `text` | Inline text, or a path relative to probes.json. |
| `set` | `dev` (used to build the fix), `holdout` (written after the fix was frozen, before seeing any results), or `diagnostic` (written after seeing results, to explain one; not evidence of generalization). Default `dev`. |
| `tier` | `good`, `gamed` or `weak`, used for ranking accuracy. Defaults: baseline `good`, floor `weak`, any probe with an exploit `gamed`. |
| `kind` | `clean` (provably not better than the baseline) or `contested` (could genuinely help; needs a rubric-free check). Default `clean`. |
| `should_lose_on` | Criteria that ought to penalize this exploit. A list, or a dict keyed by `--rubric-label` when you score several rubrics whose criterion IDs differ. |
| `frozen_rubric` | Optional record that the held-out probes postdate the hardened rubric. |

## preferences.json (judge.py prefer writes this)

```json
{"preferences": {"E04": {"winner": "baseline", "counts": {"baseline": 5, "probe": 1, "tie": 0}}}}
```

`winner` is `baseline`, `probe`, `tie`, or `split` when no option has a majority. Each run asks twice, once in each order.

## scores.json (judge.py score writes this; analyze.py reads it)

```json
{
  "rubric": "Support reply rubric v1",
  "scale_max": 5,
  "criteria": [{"id": "C1", "name": "Helpfulness", "weight": 0.3}],
  "baseline": "P0",
  "floor": "PF",
  "probes": [{"id": "E01", "exploit": "E01", "set": "dev", "tier": "gamed", "kind": "clean",
              "should_lose_on": ["C3"], "label": "Padding", "ground_truth": "…"}],
  "runs": [{"P0": {"C1": 5}, "E01": {"C1": 5}}],
  "preferences": {"E04": {"winner": "baseline"}},
  "judge": {"command": "claude -p", "mode": "one fresh call per response", "runs": 5}
}
```

`judge.py` finds criteria in markdown table rows that start `| C1 | Name | 25% |`. If your rubric isn't written that way, pass `--criteria criteria.json` (a list like the `criteria` array above). Weights are optional; without them the total is a plain sum.

## Definitions

For one gamed probe and one criterion, over *n* runs:

- **gap** in a run = gamed score − baseline score; **mean gap** = average over runs.
- **FOOLED**: n ≥ `--min-runs` (3), mean gap ≥ `--min-gap` (0.5), and gap > 0 in at least `--consistency` (80%) of runs. The per-run condition is direction only; the size condition applies to the mean.
- **ROBUST**: the mirror image (mean gap ≤ −0.5, lower in ≥ 80% of runs).
- **WEAK**: mean gap > 0 but not FOOLED.
- **VULNERABLE**: otherwise, on a criterion in `should_lose_on`.
- **NEUTRAL**: otherwise, on any other criterion.
- **DISPUTED**: a contested gamed probe whose rubric-free preference is not `baseline`. Every FOOLED, WEAK and VULNERABLE cell for that probe becomes DISPUTED, so it produces no findings and doesn't affect the verdict.

Totals use the same rule on the weighted total: **BEATS** (consistent, by at least the gap), **CLOSE** (within the gap, or ahead but inconsistent), **BELOW**.

**Weighted total** = Σ(weight × score) / Σ(weights) × number of criteria, so it stays on the scale of a plain sum.

**Ranking accuracy** = over all pairs (good-tier probe, gamed- or weak-tier probe, excluding disputed ones), the share where the good probe has the higher mean total. Ties count as half. A good-tier probe marked `contested` counts only when the rubric-free judge's verdict is `probe` or `tie`; when it is `baseline`, `split` or missing, the probe is **unconfirmed**. Unconfirmed probes are left out of the main figure; `with_unconfirmed` gives the figure you'd get by counting them as good.
