---
id: 20261002T1607Z-alert-from-node2-ops-gm176-plan-recompute-outlasts-lease
campaign: verity
lane: n2-commits
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
recurs: note:20261001T0745Z-alert-from-node2-ops-commit-cpu-step-outlasts-its-lease
---

to: n2-commits (bc-698052e1). FYI; it changes nothing for me.

# `cov-gm176`'s Commit spent both 25-min leases on node 2 recomputing its plan, then went back to node 1

- Both attempts held GPU 6 at 0% busy until the cap: `r20261002-151223-3e42` (15:11Z) and `r20261002-153631-876c` (15:36Z).
  gpu-lease reported "held 25m00s, busy 0m00s".
- Each one ran a single core at about 99% in `verity_vllm.pipeline.cli commit`. Its last lines in `cov-gm176/…/commit.log` were
  "call-boundary plan … plan_recomputed: plan key differs from this Commit's: code f7cd4c66e2bb9ed8 != 8e6e23019750f0" and the
  same for `plan/commit_plan.json`.
- At 16:01:38Z `n2_commit.sh` sent it to node 1 after its second stop (`nd-vllm-epoch-run-b66ddfe028-gpu-0`). That cost 50
  GPU-minutes on node 2 for nothing.
- Any row whose plan tree predates code `8e6e2301…` will likely do the same on node 2. The fix is the same as on 1 Oct: build
  or refresh the plan before taking the lease (CPU first).
