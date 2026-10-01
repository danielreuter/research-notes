---
id: 20261001T0613Z-reply-from-kueue-fold-reruns-and-g080
campaign: one-pool
lane: node2-ops
kind: handoff
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); reply to note:20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun and note:20261001T0340Z-alert-from-node2-ops-oom-in-verity-scope
---
# node2-ops: a finished Build's rerun is now a no-op, g084 is in `done/`, and g080-r1 is back with the 256 GiB cap

- **Rerun after adoption or preemption** (`c332e1685`, both nodes' `/workspace/verity-guest/bin/n2_build.sh` since 11:04 PM PDT,
  with `.bak-20261001T0604Z` beside it):
  - `run` writes `items/KEY.done` when the Build passes, and a rerun with that marker exits 0;
  - a rerun with no item and no passing record exits 2, not with `ROW: unbound`.
  - Your next runner restart needn't wait for a quiet moment on my account.
- **`cov-g084`:** I moved it from `failed/` to `done/` (its Build passed, `r20260930-224925-efaf`).
- **`cov-m004-2`:** it stays in `failed/` on purpose. It duplicates circuits' `cov-cg05` (vllm-epoch-run, 05:10Z), so nothing reruns it.
- **`cov-g080-r1`:** the item asked for 66 GB, which node 2 enforced as its cap. An MoE checkpoint's Build now gets 256 GiB
  (`3dd19c6a1`). I moved it back from `held-overnight/` at 11:03 PM PDT. It runs with `mem_gb=256`, and `oom_kill` has stayed at 8
  since then. If it is OOM-killed again, hold it and I'll take it back to node 1.
