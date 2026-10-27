# Contributing to Goodhart

Thanks for helping make rubrics harder to game. Three kinds of contribution matter most.

## 1. A new exploit

An exploit earns a place in the catalog when it is **distinct** from the existing 15 and you can show it **fooled a real rubric**. Open an issue with the "New exploit" template, or a pull request that:

1. Adds a row to `skills/goodhart/references/exploits.md` with the next free ID (E16, E17…), a one-line mechanism, the kinds of criteria it fools, and whether it works on human graders, LLM judges or both.
2. Includes, in the PR description, the rubric it fooled (anonymized is fine), the honest baseline, the gamed probe, the ground-truth note, and the scores.
3. If an existing hardening pattern closes it, says which one. If none does, propose a new pattern in `hardening.md`.

Please don't submit exploits that only work by making content harmful, or injection payloads that do anything beyond asking for a higher score.

## 2. A worked example

Add a folder under `examples/` laid out like `examples/support-reply/`:

- `task.md`, `rubric-v1.md` (original) and `rubric-v2.md` (hardened, with no notes about exploits in it, since the judge reads it)
- `probes.json` with dev probes and held-out probes, and a `frozen_rubric` hash showing the held-out probes were written after v2 was final. A commit history that shows the same order is even better.
- ideally a second task in a subfolder, all held-out
- `preferences.json`, `scores-v1.json` and `scores-v2.json` from `judge.py` (at least 5 runs), and `analysis-*.md` from `analyze.py`
- `report.md` that says which judge and model scored it, and claims nothing the scores don't show

Never edit scores or analysis files by hand; regenerate them. Results where the hardened rubric still fails on held-out probes are just as welcome as clean wins.

The most useful new domains are other LLM-as-judge setups: code review, summarization, RAG answers, agent transcripts. Rubrics for contested human judgments (hiring, essays, grants) need more than this tool checks, so please open an issue to discuss before adding one.

## 3. Changes to the skill or the analyzer

- Keep `SKILL.md` focused. Detail belongs in `references/`.
- Keep `scripts/analyze.py` and `scripts/judge.py` standard-library only, and run the tests (they use a fake judge, so they need no API access):

```bash
python3 -m unittest discover -s tests -v
```

- If you change the plugin manifests, run `claude plugin validate .` from the repo root.

## Exploit and pattern IDs are stable

Reports and issues refer to IDs like E05 and H3, so never renumber. Deprecate instead.
