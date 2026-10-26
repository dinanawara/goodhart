import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "goodhart", "scripts"))
import analyze  # noqa: E402

EXAMPLE = os.path.join(ROOT, "examples", "support-reply")


def tiny(base, gamed, should_lose_on=None, runs=1):
    probe = {"id": "E01", "exploit": "E01", "label": "Padding"}
    if should_lose_on is not None:
        probe["should_lose_on"] = should_lose_on
    return {
        "criteria": [{"id": "A"}, {"id": "B"}],
        "baseline": "P0",
        "probes": [{"id": "P0", "exploit": None}, probe],
        "runs": [{"P0": dict(zip("AB", base)), "E01": dict(zip("AB", gamed))}] * runs,
    }


class Verdicts(unittest.TestCase):
    def test_fooled_vulnerable_robust(self):
        r = analyze.analyze(tiny([3, 3], [4, 3]))
        self.assertEqual(r["matrix"]["E01"]["A"]["verdict"], analyze.FOOLED)
        self.assertEqual(r["matrix"]["E01"]["B"]["verdict"], analyze.VULNERABLE)
        r = analyze.analyze(tiny([3, 3], [2, 2]))
        self.assertTrue(all(c["verdict"] == analyze.ROBUST for c in r["matrix"]["E01"].values()))

    def test_tie_off_target_is_neutral(self):
        r = analyze.analyze(tiny([3, 3], [2, 3], should_lose_on=["A"]))
        self.assertEqual(r["matrix"]["E01"]["B"]["verdict"], analyze.NEUTRAL)
        self.assertEqual(r["findings"], [])

    def test_overall_verdicts(self):
        self.assertEqual(analyze.analyze(tiny([3, 3], [4, 3]))["verdict"], "Do not use as-is")
        self.assertEqual(analyze.analyze(tiny([3, 3], [4, 2]))["verdict"], "Use with fixes")

    def test_weights(self):
        d = tiny([5, 1], [1, 5])
        d["criteria"] = [{"id": "A", "weight": 3}, {"id": "B", "weight": 1}]
        r = analyze.analyze(d)
        self.assertGreater(r["totals"]["P0"], r["totals"]["E01"])

    def test_unstable(self):
        d = tiny([3, 3], [3, 3])
        d["runs"] = [d["runs"][0], {"P0": {"A": 3, "B": 3}, "E01": {"A": 5, "B": 3}}]
        r = analyze.analyze(d)
        self.assertTrue(r["matrix"]["E01"]["A"]["unstable"])


class Validation(unittest.TestCase):
    def test_missing_score(self):
        d = tiny([3, 3], [3, 3])
        del d["runs"][0]["E01"]["B"]
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(d)

    def test_unknown_target(self):
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(tiny([3, 3], [3, 3], should_lose_on=["Z"]))

    def test_bad_baseline(self):
        d = tiny([3, 3], [3, 3])
        d["baseline"] = "nope"
        with self.assertRaises(analyze.ScoresError):
            analyze.validate(d)


class Example(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = analyze.main(list(args))
        return code, out.getvalue()

    def test_v1_is_gameable_v2_is_not(self):
        code, _ = self.run_cli(os.path.join(EXAMPLE, "scores-v1.json"), "--fail-on", "total")
        self.assertEqual(code, 1)
        code, _ = self.run_cli(os.path.join(EXAMPLE, "scores-v2.json"), "--fail-on", "any")
        self.assertEqual(code, 0)

    def test_committed_analysis_is_current(self):
        for v in ("v1", "v2"):
            _, out = self.run_cli(os.path.join(EXAMPLE, f"scores-{v}.json"))
            with open(os.path.join(EXAMPLE, f"analysis-{v}.md"), encoding="utf-8") as fh:
                self.assertEqual(out, fh.read(), f"analysis-{v}.md is stale; regenerate it")

    def test_json_output(self):
        _, out = self.run_cli(os.path.join(EXAMPLE, "scores-v1.json"), "--format", "json")
        self.assertIn("matrix", json.loads(out))

    def test_bad_file_exit_code(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{not json")
        try:
            code, _ = self.run_cli(fh.name)
            self.assertEqual(code, 2)
        finally:
            os.unlink(fh.name)


if __name__ == "__main__":
    unittest.main()
