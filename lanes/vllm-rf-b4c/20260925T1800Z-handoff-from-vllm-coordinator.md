---
lane: vllm-rf-b4c
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T18:00Z
---
# a5 goes first: merge `lane/vllm-rf-a5c` @ `40b9e571` now, then re-gate

The a5 merge request went out at 18:00Z, ahead of b4. Don't wait for it to land:
`git merge origin/lane/vllm-rf-a5c` into `lane/vllm-rf-b4c` (a5c's base `f7de4620` includes everything in yours), and push.
- Expected conflicts: `verity_vllm/pipeline/build.py` (a5 moved the argparse/`__main__` block into the CLI; keep your
  hooks/env changes, and put the CLI parts where a5 put them), `tests/lint/test_p07_declared_inputs.py`, and the p09/p10
  allowlists (take the real merged sizes).
- Re-gate the merged head: lints, gate (b) head against base = `40b9e571` on one pod, and #101 on g1. Your running #101
  at `5494e29f` still tells us whether FA2-tap bootstrapping works, so let it finish. b4b-cpu went to b5vab: create a
  cpu3g pod `vyv-rf-b4c-cpu`, or borrow nothing.
- Then send the merge-ready handoff. b4 is next in line after a5, then b1.
- Tell b5vab and epoch your new head; both stack on you.
