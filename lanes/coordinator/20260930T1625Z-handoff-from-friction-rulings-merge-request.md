---
cursor:
  subagentId: "bc-bae5e52c-4820-5cd5-bd6a-9eeb1a6856f0"
id: coordinator/20260930T1625Z-handoff-from-friction-rulings-merge-request
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-bae5e52c)
---

# friction pass -> RC: merge request for #571, Daniel's two 2026-09-30 rulings in the friction skill

- **PR:** [#571](https://github.com/danielreuter/verity/pull/571), branch `cursor/friction-rulings-56f0`, head
  **`98a36aa2d302fdb4442316f781bc95b5168e3712`**. It's ready for review, out of draft, one commit on `main` `fadd2e23` (train TLT).
- **Approval:** Daniel ruled on both at 16:22Z. The questions and recommendations are in the Project store's
  `internal/friction/20260930-pass.md`.
- **What it changes:** two bullet points under "Rulings so far" in `.agents/skills/friction/SKILL.md`, newest first:
  - a lane fixes a bug it hits in `tools/research` in a small PR of its own, and you only review and merge it; when an open
    PR already changes the same function, the fix goes to that PR's owner;
  - a run's author declares what custody persists, through a small trim API, never a size-cap heuristic; how to declare it
    is the `writing-runs` skill (`.agents/skills/writing-runs/`), which a separate worker is building. Until it lands, the
    line points at a path that doesn't exist yet. No test checks skill links.
- **Grants: none needed.** It's docs only: no code, tests, circuits or Lean, no `lean-audit.json`, and nothing under
  `backends/flock/` or `integrations/vllm/`.
- **Tests on the head:** the root suite (`uv run python -m pytest tests`) passed 32. Your train's `check` records it.
- **Conflicts:** none. The only other open PRs that show the skill file in their diff, #540 and #483, got it by merging
  `main`. `git merge-tree` against #540 is clean. #483 conflicts only in its own vLLM files (`rows.py`, `targets.py`), and it
  conflicts with `main` there too.
- **What changes for you:** the first ruling moves `tools/research` bug fixes off your queue. My 16:15Z handoff
  (`20260930T1615Z-handoff-from-verity-root-friction-run-on-late-failures.md`: `--timeout` units, `fetch` hiding a dead
  launcher, the resolved cwd, the multipart stall) can go back to the lanes that hit those bugs, or to a worker root assigns.
  Its custody-cap item is settled by the second ruling: no size cap.
