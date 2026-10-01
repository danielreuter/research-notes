---
id: 20261001T0228Z-handoff-from-infra-631-ready-for-a-train
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1), for the PR captain (bc-7ff3de9e)
---

# #631 is ready for a train (owner: infra)

- **PR:** [#631](https://github.com/danielreuter/verity/pull/631), `cursor/sweep-branches-558b` @ **`ae282e728`**. At 02:52Z it moved
  from `1ddca79cd` to `db6d555bf`, adding `research merge --push` and Daniel's sweep ruling in `.agents/skills/friction/SKILL.md`. At 03:44Z
  I merged `main` `ba4311209` into it, resolving the friction SKILL.md conflict by keeping both rulings, newest first. It merges cleanly onto
  `ba4311209` alone, and onto the train #303, #599, #340, #240 (posted 03:42Z) after #240.
- **Train lander:** land the train that carries #631 with `research merge … --push`, so its own sweep runs after the push.
- **What it does:** `research merge --sweep` deletes each closed PR's head branch unless an open PR still uses it or the branch moved
  past the head that landed (a lease on the landed head).
- **Scope:** `tools/research/` (`merge.py`, `README.md`, `tests/test_merge_sweep.py`) and `.agents/skills/friction/SKILL.md`.
  Nothing under `backends/flock/`, so `check` needs no `lean-agreement`.
- **Tests:** `test_merge_sweep.py` and `test_merge_gate.py`, 17 passed; the repository's `tests/`, 33 passed.
