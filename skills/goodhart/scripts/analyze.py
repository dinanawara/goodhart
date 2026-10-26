#!/usr/bin/env python3
"""Goodhart analyzer: turn blind rubric scores into a vulnerability report.

Usage:
    python3 analyze.py scores.json [--unstable 1.0] [--format md|json]

Reads the scores.json format described in references/scores-format.md and
prints a Markdown report (default) or JSON. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from statistics import mean

FOOLED, VULNERABLE, ROBUST, NEUTRAL = "FOOLED", "VULNERABLE", "ROBUST", "NEUTRAL"
ICON = {FOOLED: "🔴", VULNERABLE: "🟡", ROBUST: "🟢", NEUTRAL: "·"}


class ScoresError(ValueError):
    pass


def load(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ScoresError(f"{path} is not valid JSON: {exc}") from exc
    validate(data)
    return data


def validate(data: dict) -> None:
    for key in ("criteria", "probes", "runs", "baseline"):
        if key not in data:
            raise ScoresError(f"missing required field '{key}'")
    if not data["runs"]:
        raise ScoresError("'runs' is empty; score at least once (twice is better)")
    crit_ids = [c["id"] for c in data["criteria"]]
    probe_ids = [p["id"] for p in data["probes"]]
    if len(set(crit_ids)) != len(crit_ids):
        raise ScoresError("duplicate criterion ids")
    if len(set(probe_ids)) != len(probe_ids):
        raise ScoresError("duplicate probe ids")
    if data["baseline"] not in probe_ids:
        raise ScoresError(f"baseline '{data['baseline']}' is not a probe id")
    floor = data.get("floor")
    if floor and floor not in probe_ids:
        raise ScoresError(f"floor '{floor}' is not a probe id")
    for i, run in enumerate(data["runs"], 1):
        for pid in probe_ids:
            if pid not in run:
                raise ScoresError(f"run {i} has no scores for probe '{pid}'")
            for cid in crit_ids:
                if cid not in run[pid]:
                    raise ScoresError(f"run {i}, probe '{pid}' is missing criterion '{cid}'")
                if not isinstance(run[pid][cid], (int, float)):
                    raise ScoresError(f"run {i}, probe '{pid}', '{cid}' is not a number")
    for p in data["probes"]:
        for cid in p.get("should_lose_on") or []:
            if cid not in crit_ids:
                raise ScoresError(f"probe '{p['id']}' should_lose_on unknown criterion '{cid}'")


def analyze(data: dict, unstable: float = 1.0) -> dict:
    crits = data["criteria"]
    crit_ids = [c["id"] for c in crits]
    weights = {c["id"]: float(c.get("weight", 1.0)) for c in crits}
    wsum = sum(weights.values()) or 1.0
    runs = data["runs"]
    base = data["baseline"]
    floor = data.get("floor")

    def cell(pid, cid):
        vals = [run[pid][cid] for run in runs]
        return mean(vals), max(vals) - min(vals)

    means, spreads, totals = {}, {}, {}
    for p in data["probes"]:
        pid = p["id"]
        means[pid], spreads[pid] = {}, {}
        for cid in crit_ids:
            means[pid][cid], spreads[pid][cid] = cell(pid, cid)
        totals[pid] = sum(weights[c] * means[pid][c] for c in crit_ids) / wsum * len(crit_ids)

    findings, matrix = [], {}
    for p in data["probes"]:
        pid = p["id"]
        if pid in (base, floor) or not p.get("exploit"):
            continue
        row = {}
        targets = p.get("should_lose_on")
        for cid in crit_ids:
            gap = means[pid][cid] - means[base][cid]
            if gap > 1e-9:
                verdict = FOOLED
            elif gap < -1e-9:
                verdict = ROBUST
            elif targets is None or cid in targets:
                verdict = VULNERABLE
            else:
                verdict = NEUTRAL  # tie on a criterion this exploit doesn't touch

            is_unstable = spreads[pid][cid] > unstable or spreads[base][cid] > unstable
            row[cid] = {"gap": round(gap, 2), "verdict": verdict, "unstable": is_unstable}
            if verdict in (FOOLED, VULNERABLE):
                findings.append({
                    "probe": pid,
                    "exploit": p.get("exploit"),
                    "label": p.get("label", pid),
                    "criterion": cid,
                    "verdict": verdict,
                    "gap": round(gap, 2),
                    "weight": weights[cid],
                    "unstable": is_unstable,
                    "ground_truth": p.get("ground_truth", ""),
                })
        matrix[pid] = row

    findings.sort(key=lambda f: (f["verdict"] != FOOLED, -f["gap"] * f["weight"], -f["weight"]))
    beat_overall = [pid for pid in matrix if totals[pid] > totals[base] + 1e-9]
    tied_overall = [pid for pid in matrix if abs(totals[pid] - totals[base]) <= 1e-9]
    exploits_hit = sorted({f["probe"] for f in findings})

    if beat_overall:
        verdict = "Do not use as-is"
    elif tied_overall or exploits_hit:
        verdict = "Use with fixes"
    else:
        verdict = "No exploit in this probe set beat the baseline"

    unstable_cells = [
        (pid, cid) for pid in means for cid in crit_ids if spreads[pid][cid] > unstable
    ]

    return {
        "rubric": data.get("rubric", "Untitled rubric"),
        "scale_max": data.get("scale_max"),
        "criteria": crits,
        "probes": data["probes"],
        "baseline": base,
        "floor": floor,
        "n_runs": len(runs),
        "means": means,
        "spreads": spreads,
        "totals": {k: round(v, 2) for k, v in totals.items()},
        "matrix": matrix,
        "findings": findings,
        "beat_overall": beat_overall,
        "tied_overall": tied_overall,
        "exploits_hit": exploits_hit,
        "separation": round(totals[base] - totals[floor], 2) if floor else None,
        "unstable_cells": unstable_cells,
        "verdict": verdict,
    }


def fmt(x: float) -> str:
    return f"{x:+.1f}" if x else "0.0"


def to_markdown(r: dict) -> str:
    crit_ids = [c["id"] for c in r["criteria"]]
    cname = {c["id"]: c.get("name", c["id"]) for c in r["criteria"]}
    plabel = {p["id"]: p.get("label", p["id"]) for p in r["probes"]}
    base = r["baseline"]
    n_exploit = len(r["matrix"])
    max_total = (r["scale_max"] or 0) * len(crit_ids)
    out = []

    out.append(f"# Goodhart analysis: {r['rubric']}\n")
    out.append(f"**Verdict:** {r['verdict']}.\n")
    headline = (
        f"**Headline:** {len(r['exploits_hit'])} of {n_exploit} exploits beat or tied the "
        f"honest baseline on at least one criterion. "
        f"{len(r['beat_overall'])} beat it on the total score"
        + (f" and {len(r['tied_overall'])} tied it." if r["tied_overall"] else ".")
    )
    if r["beat_overall"]:
        worst = max(r["beat_overall"], key=lambda p: r["totals"][p])
        headline += (
            f" The worst, **{plabel[worst]}**, totalled {r['totals'][worst]:.2f} vs. the "
            f"baseline's {r['totals'][base]:.2f}."
        )
    out.append(headline)
    out.append(f"\nScored over {r['n_runs']} run(s).")

    out.append("\n## Totals\n")
    scale = f" / {max_total}" if max_total else ""
    out.append(f"| Probe | Total{scale} | vs. baseline |")
    out.append("|---|---|---|")
    order = sorted(r["totals"], key=lambda p: -r["totals"][p])
    for pid in order:
        diff = r["totals"][pid] - r["totals"][base]
        tag = "baseline" if pid == base else ("floor" if pid == r["floor"] else fmt(round(diff, 2)))
        flag = " ⚠️" if pid in r["beat_overall"] or pid in r["tied_overall"] else ""
        out.append(f"| {plabel[pid]} ({pid}){flag} | {r['totals'][pid]:.2f} | {tag} |")
    if r["separation"] is not None:
        out.append(
            f"\nBaseline vs. floor separation: **{r['separation']:.2f}**. "
            "If this is small, the rubric struggles to tell good from weak even without gaming."
        )

    out.append("\n## Vulnerability matrix\n")
    out.append("Cell = gamed score minus baseline score. 🔴 fooled (gamed scored higher), "
               "🟡 vulnerable (tied on a criterion that should have caught it), 🟢 robust, "
               "· tied on a criterion this exploit doesn't target, ~ unstable across runs.\n")
    out.append("| Exploit | " + " | ".join(f"{cid} {cname[cid]}" for cid in crit_ids) + " |")
    out.append("|---|" + "---|" * len(crit_ids))
    for pid, row in r["matrix"].items():
        cells = []
        for cid in crit_ids:
            c = row[cid]
            cells.append(f"{ICON[c['verdict']]} {fmt(c['gap'])}{' ~' if c['unstable'] else ''}")
        out.append(f"| {plabel[pid]} ({pid}) | " + " | ".join(cells) + " |")

    out.append("\n## Findings (most severe first)\n")
    if not r["findings"]:
        out.append("No criterion was fooled or tied by this probe set. "
                   "That means none of these exploits worked, not that the rubric is ungameable.")
    for i, f in enumerate(r["findings"], 1):
        verb = "fooled by" if f["verdict"] == FOOLED else "cannot distinguish"
        line = (f"{i}. **{f['criterion']} {cname[f['criterion']]}** {verb} "
                f"**{f['label']}** ({f['probe']}): gap {fmt(f['gap'])}")
        if f["unstable"]:
            line += " (unstable)"
        out.append(line)
        if f["ground_truth"]:
            out.append(f"   - Ground truth: {f['ground_truth']}")

    if r["unstable_cells"]:
        out.append("\n## Unstable scores\n")
        out.append("These probe/criterion pairs moved by more than the threshold between runs. "
                   "Consider pattern H9 (distinct levels).\n")
        for pid, cid in r["unstable_cells"]:
            out.append(f"- {plabel[pid]} ({pid}) on {cid} {cname[cid]}: "
                       f"spread {r['spreads'][pid][cid]:.1f}")

    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scores", help="path to scores.json")
    ap.add_argument("--unstable", type=float, default=1.0,
                    help="flag cells whose run-to-run spread exceeds this (default 1.0)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--fail-on", choices=("never", "total", "fooled", "any"), default="never",
                    help="exit 1 for CI: 'total' if a gamed probe beats or ties the baseline "
                         "total, 'fooled' if any criterion is fooled, 'any' if any finding")
    args = ap.parse_args(argv)
    try:
        result = analyze(load(args.scores), unstable=args.unstable)
    except (OSError, ScoresError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        sys.stdout.write(to_markdown(result))
    fooled = any(f["verdict"] == FOOLED for f in result["findings"])
    failed = {
        "never": False,
        "total": bool(result["beat_overall"] or result["tied_overall"]),
        "fooled": fooled,
        "any": bool(result["findings"] or result["beat_overall"] or result["tied_overall"]),
    }[args.fail_on]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
