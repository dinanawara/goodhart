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
                        {"id": "G2", "exploit": None, "tier": "good", "kind": "contested"}]
        for run in d["runs"]:
            run["PF"] = {"A": 1, "B": 1}
            run["G1"] = {"A": 2, "B": 2}  # good, but scored below the gamed probe
            run["G2"] = {"A": 1, "B": 1}
        d["floor"] = "PF"
        d["preferences"] = {"G2": {"winner": "baseline"}}
        r = analyze.analyze(d)
        # pairs: P0>E01, P0>PF, G1<E01, G1>PF  -> 3/4; G2 is left out
        self.assertEqual(r["ranking"]["pairs"], 4)
        self.assertAlmostEqual(r["ranking"]["accuracy"], 0.75)
        self.assertEqual(r["ranking"]["unconfirmed"], ["G2"])
        self.assertIn(("G1", "E01"), r["ranking"]["violations"])


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
        # ...but over-corrects on ticket 1's held-out honest variation
        self.assertEqual(self.run_cli(os.path.join(t1, "scores-v2.json"), "--min-ranking", "0.9")[0], 1)

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
