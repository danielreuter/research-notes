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

- **PR:** [#631](https://github.com/danielreuter/verity/pull/631), `cursor/sweep-branches-558b` @ **`db6d555bf`** (moved from `1ddca79cd`
  at 02:52Z: `research merge --push`, and Daniel's sweep ruling in `.agents/skills/friction/SKILL.md`), based on `main` `4860d817a`;
  no conflicts with `main` at 02:50Z.
- **Train lander:** land the train that carries #631 with `research merge … --push`, so its own sweep runs after the push.
- **What it does:** `research merge --sweep` deletes each closed PR's head branch unless an open PR still uses it or the branch moved
  past the head that landed (a lease on the landed head).
- **Scope:** `tools/research/` (`merge.py`, `README.md`, `tests/test_merge_sweep.py`) and `.agents/skills/friction/SKILL.md`.
  Nothing under `backends/flock/`, so `check` needs no `lean-agreement`.
- **Tests:** `test_merge_sweep.py` and `test_merge_gate.py`, 17 passed; the repository's `tests/`, 33 passed.
