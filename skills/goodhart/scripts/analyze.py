#!/usr/bin/env python3
"""Goodhart analyzer: turn repeated blind rubric scores into a vulnerability report.

Usage:
    python3 analyze.py scores.json [--min-runs 3] [--min-gap 0.5] [--consistency 0.8]
                                   [--format md|json] [--fail-on never|total|fooled|any]
                                   [--min-ranking 0.9]

Reads the scores.json format in references/scores-format.md (judge.py writes it).
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from statistics import mean

FOOLED, WEAK, VULNERABLE, ROBUST, NEUTRAL, DISPUTED = (
    "FOOLED", "WEAK", "VULNERABLE", "ROBUST", "NEUTRAL", "DISPUTED")
ICON = {FOOLED: "🔴", WEAK: "🟠", VULNERABLE: "🟡", ROBUST: "🟢", NEUTRAL: "·", DISPUTED: "⚪"}
BEATS, CLOSE, BELOW = "BEATS", "CLOSE", "BELOW"
EPS = 1e-9


class ScoresError(ValueError):
    pass


# ---------------------------------------------------------------- loading

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
        raise ScoresError("'runs' is empty; score at least 3 times (5 is better)")
    crit_ids = [c["id"] for c in data["criteria"]]
    probe_ids = [p["id"] for p in data["probes"]]
    if len(set(crit_ids)) != len(crit_ids):
        raise ScoresError("duplicate criterion ids")
    if len(set(probe_ids)) != len(probe_ids):
        raise ScoresError("duplicate probe ids")
    if data["baseline"] not in probe_ids:
        raise ScoresError(f"baseline '{data['baseline']}' is not a probe id")
    if data.get("floor") and data["floor"] not in probe_ids:
        raise ScoresError(f"floor '{data['floor']}' is not a probe id")
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
        if p.get("kind", "clean") not in ("clean", "contested"):
            raise ScoresError(f"probe '{p['id']}' kind must be 'clean' or 'contested'")
        if p.get("tier") and p["tier"] not in ("good", "gamed", "weak"):
            raise ScoresError(f"probe '{p['id']}' tier must be good, gamed or weak")


# ---------------------------------------------------------------- analysis

def analyze(data: dict, min_runs: int = 3, min_gap: float = 0.5,
            consistency: float = 0.8) -> dict:
    crits = data["criteria"]
    crit_ids = [c["id"] for c in crits]
    weights = {c["id"]: float(c.get("weight", 1.0)) for c in crits}
    wsum = sum(weights.values()) or 1.0
    runs = data["runs"]
    n = len(runs)
    base = data["baseline"]
    floor = data.get("floor")
    prefs = data.get("preferences", {})
    probes = {p["id"]: p for p in data["probes"]}

    def total(run, pid):
        return sum(weights[c] * run[pid][c] for c in crit_ids) / wsum * len(crit_ids)

    totals_by_run = {pid: [total(r, pid) for r in runs] for pid in probes}
    totals = {pid: mean(v) for pid, v in totals_by_run.items()}
    means = {pid: {c: mean(r[pid][c] for r in runs) for c in crit_ids} for pid in probes}
    spreads = {pid: {c: max(r[pid][c] for r in runs) - min(r[pid][c] for r in runs)
                     for c in crit_ids} for pid in probes}

    def classify(gaps, targeted):
        g = mean(gaps)
        wins = sum(x > EPS for x in gaps) / len(gaps)
        losses = sum(x < -EPS for x in gaps) / len(gaps)
        enough = len(gaps) >= min_runs
        if enough and g >= min_gap - EPS and wins >= consistency - EPS:
            return FOOLED
        if enough and g <= -min_gap + EPS and losses >= consistency - EPS:
            return ROBUST
        if g > EPS:
            return WEAK
        if targeted:
            return VULNERABLE
        return NEUTRAL

    def disputed(p):
        """A contested probe only counts if a rubric-free judge preferred the baseline."""
        if p.get("kind") != "contested":
            return False
        return prefs.get(p["id"], {}).get("winner") != "baseline"

    gamed = [pid for pid, p in probes.items()
             if p.get("exploit") and pid not in (base, floor)]
    matrix, findings, overall = {}, [], {}
    for pid in gamed:
        p = probes[pid]
        targets = p.get("should_lose_on")
        is_disputed = disputed(p)
        row = {}
        for cid in crit_ids:
            gaps = [r[pid][cid] - r[base][cid] for r in runs]
            v = classify(gaps, targets is None or cid in targets)
            if is_disputed and v in (FOOLED, WEAK):
                v = DISPUTED
            cell = {"gap": round(mean(gaps), 2), "verdict": v,
                    "wins": sum(x > EPS for x in gaps), "runs": n}
            row[cid] = cell
            if v in (FOOLED, WEAK, VULNERABLE):
                findings.append({"probe": pid, "label": p.get("label", pid),
                                 "set": p.get("set", "dev"), "criterion": cid,
                                 "weight": weights[cid], "ground_truth": p.get("ground_truth", ""),
                                 **cell})
        matrix[pid] = row

        diffs = [a - b for a, b in zip(totals_by_run[pid], totals_by_run[base])]
        d = mean(diffs)
        wins = sum(x > EPS for x in diffs) / n
        if is_disputed:
            status = DISPUTED
        elif n >= min_runs and d >= min_gap - EPS and wins >= consistency - EPS:
            status = BEATS
        elif d > -min_gap:
            status = CLOSE
        else:
            status = BELOW
        overall[pid] = {"diff": round(d, 2), "wins": sum(x > EPS for x in diffs), "status": status}

    rank = {"good": [], "low": [], "unconfirmed": []}
    for pid, p in probes.items():
        tier = p.get("tier") or ("good" if pid == base else "weak" if pid == floor
                                 else "gamed" if p.get("exploit") else None)
        if tier == "good" and p.get("kind") == "contested" and pid != base \
                and prefs.get(pid, {}).get("winner") == "baseline":
            rank["unconfirmed"].append(pid)  # the rubric-free judge rated it worse than P0
        elif tier == "good":
            rank["good"].append(pid)
        elif tier in ("gamed", "weak") and not disputed(p):
            rank["low"].append(pid)
    pairs, violations = 0, []
    score = 0.0
    per_set = {}
    for g in rank["good"]:
        for low in rank["low"]:
            pairs += 1
            if totals[g] > totals[low] + EPS:
                s = 1.0
            elif abs(totals[g] - totals[low]) <= EPS:
                s = 0.5
            else:
                s = 0.0
            score += s
            if s < 1:
                violations.append((g, low))
            # a pair belongs to the held-out set if either side was written after the freeze
            in_set = "holdout" if "holdout" in (probes[g].get("set"), probes[low].get("set")) \
                else probes[low].get("set", "dev")
            acc = per_set.setdefault(in_set, [0.0, 0])
            acc[0] += s
            acc[1] += 1
    ranking = {"accuracy": round(score / pairs, 3) if pairs else None,
               "pairs": pairs, "violations": violations, "unconfirmed": rank["unconfirmed"],
               "by_set": {k: {"accuracy": round(v[0] / v[1], 3), "pairs": v[1]}
                          for k, v in sorted(per_set.items())}}

    by_set = {}
    for pid in gamed:
        by_set.setdefault(probes[pid].get("set", "dev"), []).append(pid)

    order = {FOOLED: 0, WEAK: 2, VULNERABLE: 1}
    findings.sort(key=lambda f: (order[f["verdict"]], -f["gap"] * f["weight"]))
    beats = [pid for pid, o in overall.items() if o["status"] == BEATS]
    close = [pid for pid, o in overall.items() if o["status"] == CLOSE]
    hard = [f for f in findings if f["verdict"] in (FOOLED, VULNERABLE)]
    if beats:
        verdict = "Do not use as-is"
    elif close or hard:
        verdict = "Use with fixes"
    else:
        verdict = "No exploit in this probe set beat or matched the baseline"

    return {
        "rubric": data.get("rubric", "Untitled rubric"),
        "scale_max": data.get("scale_max"),
        "criteria": crits,
        "probes": data["probes"],
        "baseline": base,
        "floor": floor,
        "n_runs": n,
        "thresholds": {"min_runs": min_runs, "min_gap": min_gap, "consistency": consistency},
        "judge": data.get("judge"),
        "means": means,
        "spreads": spreads,
        "totals": {k: round(v, 2) for k, v in totals.items()},
        "matrix": matrix,
        "overall": overall,
        "by_set": by_set,
        "findings": findings,
        "ranking": ranking,
        "preferences": prefs,
        "verdict": verdict,
    }


# ---------------------------------------------------------------- report

def fmt(x: float) -> str:
    return f"{x:+.1f}" if abs(x) > EPS else "0.0"


def to_markdown(r: dict) -> str:
    crit_ids = [c["id"] for c in r["criteria"]]
    cname = {c["id"]: c.get("name", c["id"]) for c in r["criteria"]}
    pinfo = {p["id"]: p for p in r["probes"]}
    plabel = {pid: p.get("label", pid) for pid, p in pinfo.items()}
    base, n, t = r["baseline"], r["n_runs"], r["thresholds"]
    out = [f"# Goodhart analysis: {r['rubric']}\n", f"**Verdict:** {r['verdict']}.\n"]

    beats = [p for p, o in r["overall"].items() if o["status"] == BEATS]
    close = [p for p, o in r["overall"].items() if o["status"] == CLOSE]
    line = (f"**Headline:** {len(beats)} of {len(r['overall'])} gamed probes beat the honest "
            f"baseline's total consistently; {len(close)} landed within {t['min_gap']} of it or "
            f"won inconsistently.")
    if r["ranking"]["accuracy"] is not None:
        line += (f" Ranking accuracy (good work above gamed and weak work): "
                 f"**{r['ranking']['accuracy']:.0%}** of {r['ranking']['pairs']} pairs")
        sets = r["ranking"]["by_set"]
        if len(sets) > 1:
            line += " (" + ", ".join(f"{k} {v['accuracy']:.0%} of {v['pairs']}"
                                     for k, v in sets.items()) + ")"
        line += "."
    out.append(line)
    judge = r.get("judge") or {}
    how = f"{n} run(s)"
    if judge.get("command"):
        how += f", judge `{judge['command']}`, {judge.get('mode', '')}"
    out.append(f"\nScored over {how}. FOOLED needs a mean gap of at least {t['min_gap']} and a "
               f"higher score in at least {t['consistency']:.0%} of at least {t['min_runs']} runs.")
    if n < 5:
        out.append(f"\n> ⚠️ Only {n} run(s). Treat 🟠 WEAK results as possible noise.")

    out.append("\n## Totals\n")
    max_total = (r["scale_max"] or 0) * len(crit_ids)
    out.append(f"| Probe | Set | Total{' / ' + str(max_total) if max_total else ''} | "
               f"vs. baseline | Higher in |")
    out.append("|---|---|---|---|---|")
    for pid in sorted(r["totals"], key=lambda p: -r["totals"][p]):
        p = pinfo[pid]
        if pid == base:
            tag, wins = "baseline", ""
        elif pid == r["floor"]:
            tag, wins = "floor", ""
        elif pid in r["overall"]:
            o = r["overall"][pid]
            mark = {BEATS: " ⚠️", CLOSE: " ≈", DISPUTED: " ⚪", BELOW: ""}[o["status"]]
            tag, wins = fmt(o["diff"]) + mark, f"{o['wins']}/{n} runs"
        else:
            tag, wins = fmt(r["totals"][pid] - r["totals"][base]), ""
        out.append(f"| {plabel[pid]} ({pid}) | {p.get('set', 'dev')} | "
                   f"{r['totals'][pid]:.2f} | {tag} | {wins} |")
    out.append("\n⚠️ beats the baseline consistently · ≈ close or inconsistent · "
               "⚪ disputed (a rubric-free judge did not prefer the baseline)")

    rk = r["ranking"]
    if rk["unconfirmed"]:
        names = ", ".join(f"{plabel[p]} ({p})" for p in rk["unconfirmed"])
        out.append(f"\nLeft out of ranking: {names}. Written as good, but the rubric-free judge "
                   "preferred the baseline, so its tier is unconfirmed.")
    if rk["violations"]:
        out.append("\n**Ranking violations** (good work not scored above gamed or weak work):\n")
        for g, low in rk["violations"]:
            out.append(f"- {plabel[g]} ({g}) {r['totals'][g]:.2f} vs. "
                       f"{plabel[low]} ({low}) {r['totals'][low]:.2f}")

    out.append("\n## Vulnerability matrix\n")
    out.append("Cell = mean gamed score minus baseline score, then runs where the gamed probe "
               "scored higher. 🔴 fooled · 🟠 weak signal · 🟡 vulnerable (a criterion that "
               "should catch it doesn't reliably) · 🟢 robust · ⚪ disputed · · not targeted\n")
    for set_name in sorted(r["by_set"], key=lambda s: (s != "dev", s)):
        out.append(f"\n**{set_name.capitalize()} probes**\n")
        out.append("| Probe | " + " | ".join(f"{c} {cname[c]}" for c in crit_ids) + " |")
        out.append("|---|" + "---|" * len(crit_ids))
        for pid in r["by_set"][set_name]:
            cells = []
            for cid in crit_ids:
                c = r["matrix"][pid][cid]
                cells.append(f"{ICON[c['verdict']]} {fmt(c['gap'])} ({c['wins']}/{c['runs']})")
            out.append(f"| {plabel[pid]} ({pid}) | " + " | ".join(cells) + " |")

    out.append("\n## Findings\n")
    if not r["findings"]:
        out.append("No criterion was fooled, weakly fooled or blind to its exploit in this probe "
                   "set. That means none of these exploits worked, not that the rubric is "
                   "ungameable.")
    words = {FOOLED: "fooled by", WEAK: "weakly rewards", VULNERABLE: "does not reliably penalize"}
    for i, f in enumerate(r["findings"], 1):
        out.append(f"{i}. {ICON[f['verdict']]} **{f['criterion']} {cname[f['criterion']]}** "
                   f"{words[f['verdict']]} **{f['label']}** ({f['probe']}, {f['set']}): "
                   f"gap {fmt(f['gap'])}, higher in {f['wins']}/{f['runs']} runs")
        if f["ground_truth"]:
            out.append(f"   - Ground truth: {f['ground_truth']}")

    if r["preferences"]:
        out.append("\n## Contested probes: rubric-free preference\n")
        out.append("| Probe | Preferred | Baseline / probe / tie votes |")
        out.append("|---|---|---|")
        for pid, pr in r["preferences"].items():
            c = pr.get("counts", {})
            out.append(f"| {plabel.get(pid, pid)} ({pid}) | {pr.get('winner')} | "
                       f"{c.get('baseline', 0)} / {c.get('probe', 0)} / {c.get('tie', 0)} |")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scores", help="path to scores.json")
    ap.add_argument("--min-runs", type=int, default=3,
                    help="runs needed before anything is called FOOLED or ROBUST (default 3)")
    ap.add_argument("--min-gap", type=float, default=0.5,
                    help="smallest mean gap that counts as a real difference (default 0.5)")
    ap.add_argument("--consistency", type=float, default=0.8,
                    help="share of runs that must agree in direction (default 0.8)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--fail-on", choices=("never", "total", "fooled", "any"), default="never",
                    help="exit 1 for CI: 'total' if a gamed probe consistently beats the baseline "
                         "total, 'fooled' if any criterion is FOOLED, 'any' if any finding")
    ap.add_argument("--min-ranking", type=float,
                    help="also exit 1 if ranking accuracy falls below this (0 to 1)")
    args = ap.parse_args(argv)
    try:
        result = analyze(load(args.scores), args.min_runs, args.min_gap, args.consistency)
    except (OSError, ScoresError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        sys.stdout.write(to_markdown(result))
    statuses = [o["status"] for o in result["overall"].values()]
    failed = {
        "never": False,
        "total": BEATS in statuses,
        "fooled": any(f["verdict"] == FOOLED for f in result["findings"]),
        "any": bool(result["findings"]) or BEATS in statuses or CLOSE in statuses,
    }[args.fail_on]
    acc = result["ranking"]["accuracy"]
    if args.min_ranking is not None and acc is not None and acc < args.min_ranking:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
