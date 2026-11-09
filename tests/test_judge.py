"""judge.py tests with a fake judge command, so they run offline and for free."""
import json
import re
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "goodhart", "scripts")
sys.path.insert(0, SCRIPTS)
import judge  # noqa: E402

# Fake judge: longer responses get higher scores (a deliberately gameable judge),
# and for pairwise prompts it always picks response A.
FAKE = r'''
import sys, json, re
p = sys.stdin.read()
if "<response_A>" in p:
    print(json.dumps({"winner": "A", "reason": "fake"}))
else:
    resp = re.search(r"<response>\n(.*?)\n</response>", p, re.S).group(1)
    ids = re.search(r"Criteria: ([^.]*)\.", p).group(1).split(", ")
    s = 5 if len(resp) > 40 else 3
    print("Sure! " + json.dumps({"scores": {c: s for c in ids}, "note": "fake"}))
'''


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.fake = os.path.join(self.dir, "fake_judge.py")
        with open(self.fake, "w") as fh:
            fh.write(FAKE)
        with open(os.path.join(self.dir, "rubric.md"), "w") as fh:
            fh.write("| ID | Criterion | Weight |\n|---|---|---|\n"
                     "| C1 | Accuracy (H1) | 60% |\n| C2 | Tone | 40% |\n")
        probes = {"task": "Answer briefly.", "baseline": "P0", "probes": [
            {"id": "P0", "text": "Short answer."},
            {"id": "E01", "exploit": "E01", "kind": "contested",
             "should_lose_on": {"v1": ["C1"]},
             "text": "A much longer answer that says the same thing at length."},
        ]}
        self.probes = os.path.join(self.dir, "probes.json")
        with open(self.probes, "w") as fh:
            json.dump(probes, fh)
        self.cmd = f"{sys.executable} {self.fake}"

    def test_skill_md_prompts_match_script(self):
        """Portable mode uses the prompts written in SKILL.md; they must match judge.py."""
        with open(os.path.join(ROOT, "skills", "goodhart", "SKILL.md"), encoding="utf-8") as fh:
            blocks = re.findall(r"```text\n(.*?)\n```", fh.read(), re.S)
        self.assertEqual(len(blocks), 2, "expected two ```text prompt blocks in SKILL.md")
        score = judge.SCORE_PROMPT.format(
            task="{task}", rubric="{rubric}", response="{response}", scale_max="{scale_max}",
            criteria="{criteria}", example='"C1": n, "C2": n, …')
        prefer = judge.PREFER_PROMPT.format(task="{task}", a="{a}", b="{b}")
        self.assertEqual(blocks[0], score)
        self.assertEqual(blocks[1], prefer)

    def test_skill_md_rules_use_analyzer_defaults(self):
        import analyze
        import inspect
        sig = inspect.signature(analyze.analyze).parameters
        self.assertEqual(sig["min_runs"].default, 3)
        self.assertEqual(sig["min_gap"].default, 0.5)
        self.assertEqual(sig["consistency"].default, 0.8)
        with open(os.path.join(ROOT, "skills", "goodhart", "SKILL.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn("Defaults: minimum runs 3, minimum gap 0.5, consistency 80%.", text)

    def test_parse_criteria(self):
        crits = judge.parse_criteria("| C1 | Accuracy (H1) | 60% | x |\n| C2 | Tone | 40% |")
        self.assertEqual(crits, [{"id": "C1", "name": "Accuracy", "weight": 0.6},
                                 {"id": "C2", "name": "Tone", "weight": 0.4}])
        with self.assertRaises(judge.JudgeError):
            judge.parse_criteria("no table here")

    def test_first_json_skips_chatter(self):
        self.assertEqual(judge.first_json('ok {"a": {"b": 1}} trailing'), {"a": {"b": 1}})

    def test_score_end_to_end(self):
        out = os.path.join(self.dir, "scores.json")
        code = judge.main(["score", "--probes", self.probes, "--rubric",
                           os.path.join(self.dir, "rubric.md"), "--rubric-label", "v1",
                           "--runs", "3", "--workers", "2", "--judge-cmd", self.cmd, "-o", out])
        self.assertEqual(code, 0)
        with open(out) as fh:
            s = json.load(fh)
        self.assertEqual(len(s["runs"]), 3)
        self.assertEqual(s["runs"][0]["E01"], {"C1": 5, "C2": 5})
        self.assertEqual(s["runs"][0]["P0"], {"C1": 3, "C2": 3})
        e01 = [p for p in s["probes"] if p["id"] == "E01"][0]
        self.assertEqual(e01["should_lose_on"], ["C1"])
        self.assertNotIn("text", e01)

    def test_prefer_counts_both_orders(self):
        out = os.path.join(self.dir, "prefs.json")
        code = judge.main(["prefer", "--probes", self.probes, "--runs", "2",
                           "--judge-cmd", self.cmd, "-o", out])
        self.assertEqual(code, 0)
        with open(out) as fh:
            prefs = json.load(fh)["preferences"]
        # the fake always picks A, so each side wins once per run: a split
        self.assertEqual(prefs["E01"]["counts"], {"baseline": 2, "probe": 2, "tie": 0})
        self.assertEqual(prefs["E01"]["winner"], "split")


if __name__ == "__main__":
    unittest.main()
