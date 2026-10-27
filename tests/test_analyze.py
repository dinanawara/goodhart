import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "goodhart", "scripts"))
import analyze  # noqa: E402

EXAMPLE = os.path.join(ROOT, "examples", "support-reply")


def make(base_runs, gamed_runs, **probe):
    """Two criteria A and B; base_runs / gamed_runs are lists of (A, B) per run."""
    p = {"id": "E01", "exploit": "E01", "label": "Padding", **probe}
    return {
        "criteria": [{"id": "A"}, {"id": "B"}],
        "baseline": "P0",
        "probes": [{"id": "P0", "exploit": None}, p],
        "runs": [{"P0": dict(zip("AB", b)), "E01": dict(zip("AB", g))}
                 for b, g in zip(base_runs, gamed_runs)],
    }


def cell(result, crit="A"):
    return result["matrix"]["E01"][crit]["verdict"]


class Verdicts(unittest.TestCase):
    def test_consistent_win_is_fooled(self):
        r = analyze.analyze(make([(3, 3)] * 5, [(4, 3)] * 5))
        self.assertEqual(cell(r), analyze.FOOLED)

    def test_inconsistent_win_is_weak(self):
        # higher in 2 of 5 runs only
        r = analyze.analyze(make([(3, 3)] * 5, [(5, 3), (5, 3), (3, 3), (3, 3), (3, 3)]))
        self.assertEqual(cell(r), analyze.WEAK)

    def test_small_gap_is_weak(self):
        # higher in every run? no: +1 in 2 runs => mean 0.4 < 0.5
        r = analyze.analyze(make([(3, 3)] * 5, [(4, 3), (4, 3), (3, 3), (3, 3), (3, 3)]))
        self.assertEqual(cell(r), analyze.WEAK)

    def test_too_few_runs_never_fooled(self):
        r = analyze.analyze(make([(3, 3)] * 2, [(5, 3)] * 2))
        self.assertEqual(cell(r), analyze.WEAK)

    def test_robust_and_vulnerable(self):
        r = analyze.analyze(make([(4, 3)] * 5, [(2, 3)] * 5))
        self.assertEqual(cell(r, "A"), analyze.ROBUST)
        self.assertEqual(cell(r, "B"), analyze.VULNERABLE)

    def test_untargeted_tie_is_neutral(self):
        r = analyze.analyze(make([(3, 3)] * 5, [(2, 3)] * 5, should_lose_on=["A"]))
        self.assertEqual(cell(r, "B"), analyze.NEUTRAL)

    def test_fooled_rule_is_mean_gap_plus_direction(self):
        # The documented rule: mean gap >= 0.5 AND higher in >= 80% of runs.
        # higher in 4/5 runs, mean +0.8 -> FOOLED (one run may tie)
        r = analyze.analyze(make([(3, 3)] * 5, [(4, 3)] * 4 + [(3, 3)]))
        self.assertEqual(cell(r), analyze.FOOLED)
        # one big win, mean +0.6, but higher in only 1/5 runs -> WEAK
        r = analyze.analyze(make([(3, 3)] * 5, [(6, 3)] + [(3, 3)] * 4))
        self.assertEqual(cell(r), analyze.WEAK)
        # higher in 4/5 runs but a big loss pulls the mean to +0.4 -> WEAK
        r = analyze.analyze(make([(3, 3)] * 5, [(4, 3)] * 4 + [(1, 3)]))
        self.assertEqual(cell(r), analyze.WEAK)

    def test_disputed_probe_produces_no_findings(self):
        # contested probe ties on a targeted criterion; rubric-free judge preferred it
        d = make([(3, 3)] * 5, [(3, 4)] * 5, kind="contested", should_lose_on=["A", "B"])
        d["preferences"] = {"E01": {"winner": "probe"}}
        r = analyze.analyze(d)
        self.assertEqual(cell(r, "A"), analyze.DISPUTED)  # would be VULNERABLE
        self.assertEqual(cell(r, "B"), analyze.DISPUTED)  # would be FOOLED
        self.assertEqual(r["findings"], [])
        self.assertEqual(r["overall"]["E01"]["status"], analyze.DISPUTED)
        self.assertNotEqual(r["verdict"], "Use with fixes")
        self.assertNotEqual(r["verdict"], "Do not use as-is")

    def test_contested_needs_independent_preference(self):
        d = make([(3, 3)] * 5, [(4, 3)] * 5, kind="contested")
        self.assertEqual(cell(analyze.analyze(d)), analyze.DISPUTED)  # no preference data
        d["preferences"] = {"E01": {"winner": "probe"}}
        self.assertEqual(cell(analyze.analyze(d)), analyze.DISPUTED)
        d["preferences"] = {"E01": {"winner": "baseline"}}
        self.assertEqual(cell(analyze.analyze(d)), analyze.FOOLED)


class Totals(unittest.TestCase):
    def test_beats_close_below(self):
        beats = analyze.analyze(make([(3, 3)] * 5, [(4, 4)] * 5))
        self.assertEqual(beats["overall"]["E01"]["status"], analyze.BEATS)
        self.assertEqual(beats["verdict"], "Do not use as-is")
        close = analyze.analyze(make([(3, 3)] * 5, [(3, 3)] * 5))
        self.assertEqual(close["overall"]["E01"]["status"], analyze.CLOSE)
        self.assertEqual(close["verdict"], "Use with fixes")
        below = analyze.analyze(make([(4, 4)] * 5, [(2, 2)] * 5))
        self.assertEqual(below["overall"]["E01"]["status"], analyze.BELOW)

    def test_weights(self):
        d = make([(5, 1)] * 3, [(1, 5)] * 3)
        d["criteria"] = [{"id": "A", "weight": 3}, {"id": "B", "weight": 1}]
        r = analyze.analyze(d)
        self.assertGreater(r["totals"]["P0"], r["totals"]["E01"])


class Ranking(unittest.TestCase):
    def test_ranking_accuracy_and_unconfirmed_good(self):
        d = make([(4, 4)] * 3, [(3, 3)] * 3)
        d["probes"] += [{"id": "PF", "exploit": None, "tier": "weak"},
                        {"id": "G1", "exploit": None, "tier": "good"},
                        {"id": "G2", "exploit": None, "tier": "good", "kind": "contested"},
                        {"id": "G3", "exploit": None, "tier": "good", "kind": "contested"},
                        {"id": "G4", "exploit": None, "tier": "good", "kind": "contested"}]
        for run in d["runs"]:
            run["PF"] = {"A": 1, "B": 1}
            run["G1"] = {"A": 2, "B": 2}  # good, but scored below the gamed probe
            run["G2"] = {"A": 1, "B": 1}
            run["G3"] = {"A": 1, "B": 1}
            run["G4"] = {"A": 5, "B": 5}
        d["floor"] = "PF"
        d["preferences"] = {"G2": {"winner": "baseline"}, "G3": {"winner": "split"},
                            "G4": {"winner": "tie"}}
        r = analyze.analyze(d)
        # confirmed good: P0, G1, G4 (tie confirms). pairs vs E01 and PF:
        # P0 2/2, G1 1/2, G4 2/2 -> 5/6; G2 (lost) and G3 (split) are unconfirmed
        self.assertEqual(r["ranking"]["pairs"], 6)
        self.assertAlmostEqual(r["ranking"]["accuracy"], 0.833)
        self.assertEqual(sorted(r["ranking"]["unconfirmed"]), ["G2", "G3"])
        self.assertIn(("G1", "E01"), r["ranking"]["violations"])
        # counting the unconfirmed ones too: G2 and G3 tie PF and lose to E01 -> +1/4
        self.assertEqual(r["ranking"]["with_unconfirmed"]["pairs"], 10)
        self.assertAlmostEqual(r["ranking"]["with_unconfirmed"]["accuracy"], 0.6)


class Validation(unittest.TestCase):
    def test_missing_score(self):
        d = make([(3, 3)], [(3, 3)])
        del d["runs"][0]["E01"]["B"]
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(d)

    def test_unknown_target(self):
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(make([(3, 3)], [(3, 3)], should_lose_on=["Z"]))

    def test_bad_kind(self):
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(make([(3, 3)], [(3, 3)], kind="maybe"))


class CLI(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = analyze.main(list(args))
        return code, out.getvalue()

    def test_example_results(self):
        t1, t2 = EXAMPLE, os.path.join(EXAMPLE, "ticket-2")
        # v1: no gamed reply wins overall, but criteria are repeatably fooled
        self.assertEqual(self.run_cli(os.path.join(t1, "scores-v1.json"), "--fail-on", "total")[0], 0)
        self.assertEqual(self.run_cli(os.path.join(t1, "scores-v1.json"), "--fail-on", "fooled")[0], 1)
        # v2 is clean on the held-out second ticket...
        self.assertEqual(self.run_cli(os.path.join(t2, "scores-v2.json"), "--fail-on", "any")[0], 0)
        # ...and ranks every confirmed pair on ticket 1 correctly; the ambiguous
        # follow-up offer is reported separately, not counted against it
        self.assertEqual(self.run_cli(os.path.join(t1, "scores-v2.json"), "--min-ranking", "0.9")[0], 0)
        r = analyze.analyze(analyze.load(os.path.join(t1, "scores-v2.json")))
        self.assertIn("G1", r["ranking"]["unconfirmed"])
        self.assertLess(r["ranking"]["with_unconfirmed"]["accuracy"], 0.9)

    def test_committed_analyses_are_current(self):
        for folder in (EXAMPLE, os.path.join(EXAMPLE, "ticket-2")):
            for v in ("v1", "v2"):
                _, out = self.run_cli(os.path.join(folder, f"scores-{v}.json"))
                with open(os.path.join(folder, f"analysis-{v}.md"), encoding="utf-8") as fh:
                    self.assertEqual(out, fh.read(), f"{folder}/analysis-{v}.md is stale")

    def test_json_output(self):
        _, out = self.run_cli(os.path.join(EXAMPLE, "scores-v1.json"), "--format", "json")
        self.assertIn("ranking", json.loads(out))

    def test_bad_file_exit_code(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{not json")
        try:
            self.assertEqual(self.run_cli(fh.name)[0], 2)
        finally:
            os.unlink(fh.name)


if __name__ == "__main__":
    unittest.main()
