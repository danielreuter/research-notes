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

- **PR:** [#631](https://github.com/danielreuter/verity/pull/631), `cursor/sweep-branches-558b` @ `1ddca79cd`, based on `main` `4860d817a`.
- **What it does:** `research merge --sweep` deletes each closed PR's head branch unless an open PR still uses it or the branch moved
  past the head that landed (a lease on the landed head).
- **Scope:** `tools/research/src/research/merge.py` and `tools/research/tests/test_merge_sweep.py` only. Nothing under `backends/flock/`,
  so `check` needs no `lean-agreement`.
- **Tests:** `test_merge_sweep.py` and `test_merge_gate.py`, 15 passed.
