---
cursor:
  subagentId: "bc-78737627-2532-5e8f-afff-ba092eef123e"
---

lane: coordinator · kind: merge-request · from: continual-learning plan (bc-78737627) · to: the research coordinator
(bc-8ece7cde); cc verity-root · created: 2026-09-29T23:25Z · repo: danielreuter/verity

# Merge request: #454, fix what's clearly yours, ask Daniel near the line and record the ruling, for the next train

- **PR:** [#454](https://github.com/danielreuter/verity/pull/454), `cursor/friction-and-rulings-123e`, head **`294e1992`**, on `main`'s tip
  `33828711`. It's marked ready.
- **Approval:** Daniel approved it, with all four of its defaults, at about 23:20Z. The plan is `docs/continual-learning-plan.md` in the
  Project store.
- **Grant:** none needed. It touches only docs and skills:
  - `AGENTS.md`: about 100 words, in "Working principles", "Where writing goes" (the `friction` note kind) and "Tests" (a one-line
    justification for tests that add over a minute to `check`);
  - the new `.agents/skills/friction/SKILL.md`.

  No code, circuits or Lean, and nothing under `backends/flock/`, so no `lean-agreement` run.
- **Conflicts:** none expected. `git merge-tree` against the heads of every other open PR that edits `AGENTS.md` (#449, #391, #389,
  #380, #367, #364) is clean. The skills that #444, #445, #450, #447 and #425 edit are different files.
- **Local runs:** the root suite (`tests/`) on the head passed 28 and skipped 1. Your train's `check` records it.
- **What changes for you:** nothing in the merge path. Lanes will start filing `kind: friction` notes, which are files, not messages.
  They'll ask near-line questions through their usual handoffs to `lanes/coordinator/`. Answer from the skill's "Rulings so far"
  when one covers the case, and forward the rest to root for Daniel.
