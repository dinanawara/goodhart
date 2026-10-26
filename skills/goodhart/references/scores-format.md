# scores.json format

`scripts/analyze.py` reads this file. Build it after blind scoring by mapping `R1…Rn` back to probe IDs with `key.json`.

```json
{
  "rubric": "Essay feedback rubric v1",
  "scale_max": 5,
  "criteria": [
    {"id": "C1", "name": "Accuracy", "weight": 0.25},
    {"id": "C2", "name": "Depth",    "weight": 0.25}
  ],
  "baseline": "P0",
  "floor": "PF",
  "probes": [
    {"id": "P0",  "exploit": null,  "label": "Honest baseline"},
    {"id": "PF",  "exploit": null,  "label": "Honest but weak"},
    {"id": "E01", "exploit": "E01", "label": "Padding",
     "ground_truth": "Same content as P0, about 2.5x longer.",
     "should_lose_on": ["C2"]}
  ],
  "runs": [
    {"P0": {"C1": 5, "C2": 3}, "PF": {"C1": 3, "C2": 2}, "E01": {"C1": 5, "C2": 5}},
    {"P0": {"C1": 5, "C2": 3}, "PF": {"C1": 3, "C2": 2}, "E01": {"C1": 5, "C2": 4}}
  ]
}
```

Fields:
- `weight` is optional. Without weights, the total is the plain sum.
- `floor` is optional. Omit it if there is no honest-but-weak probe.
- `should_lose_on` is optional. It lists the criteria that *ought* to penalize this exploit (from your Step 2 hypothesis). A tie on one of these is VULNERABLE; a tie on any other criterion is NEUTRAL and not reported, because padding tying the baseline on "accuracy" is expected. Without the field, every tie counts as VULNERABLE.
- `runs` holds one object per scoring run. Every probe must have a score for every criterion in every run.

## Definitions (for computing by hand)

- **Mean score** of a probe on a criterion: average across runs.
- **Exploit gap** = mean(gamed probe) − mean(baseline), per criterion.
- **Spread** = max − min across runs for one probe on one criterion.
- **Verdict** per cell: FOOLED if gap > 0; VULNERABLE if gap = 0 on a `should_lose_on` criterion (or on any criterion when the field is absent); NEUTRAL if gap = 0 elsewhere; ROBUST if gap < 0; UNSTABLE is added when spread > 1 (the threshold is configurable with `--unstable`).
- **Weighted total** = Σ(weight × mean score) / Σ(weights) × number of criteria, so it stays on the same scale as an unweighted sum.
- **Separation** = total(baseline) − total(floor). If it is small compared with the scale, the rubric struggles to tell good from weak even before anyone games it.
