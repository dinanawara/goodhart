# Contributing to Goodhart

Thanks for helping make rubrics harder to game. Three kinds of contribution matter most.

## 1. A new exploit

An exploit earns a place in the catalog when it is **distinct** from the existing 15 and you can show it **fooled a real rubric**. Open an issue with the "New exploit" template, or a pull request that:

1. Adds a row to `skills/goodhart/references/exploits.md` with the next free ID (E16, E17…), a one-line mechanism, the kinds of criteria it fools, and whether it works on human graders, LLM judges or both.
2. Includes, in the PR description, the rubric it fooled (anonymized is fine), the honest baseline, the gamed probe, the ground-truth note, and the scores.
3. If an existing hardening pattern closes it, says which one. If none does, propose a new pattern in `hardening.md`.

Please don't submit exploits that only work by making content harmful, or injection payloads that do anything beyond asking for a higher score.

## 2. A worked example

Add a folder under `examples/` with the same files as `examples/support-reply/`: `task.md`, `rubric-v1.md`, `probes.md`, `scores-v1.json`, `analysis-v1.md`, `rubric-v2.md`, `scores-v2.json`, `analysis-v2.md` and `report.md`. Regenerate the analysis files with the script rather than editing them by hand. Say in `report.md` how the scoring was done (model, isolated or not, number of runs).

Examples from different domains are especially useful: essay grading, code review, hiring, grant review, research paper review.

## 3. Changes to the skill or the analyzer

- Keep `SKILL.md` focused. Detail belongs in `references/`.
- Keep `scripts/analyze.py` standard-library only, and run the tests:

```bash
python3 -m unittest discover -s tests -v
```

- If you change the plugin manifests, run `claude plugin validate .` from the repo root.

## Exploit and pattern IDs are stable

Reports and issues refer to IDs like E05 and H3, so never renumber. Deprecate instead.
