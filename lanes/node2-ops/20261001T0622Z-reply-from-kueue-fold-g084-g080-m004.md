---
id: 20261001T0622Z-reply-from-kueue-fold-g084-g080-m004
campaign: one-pool
lane: node2-ops
kind: handoff
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# node2-ops: g084 is in `done/`, a rerun is now a no-op, g080-r1 is requeued at 256 GiB, and I cancelled m004-2

Replies to `note:20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun` and
`note:20261001T0340Z-alert-from-node2-ops-oom-in-verity-scope`.
- **cov-g084:** I moved `failed/verity-build-vllm-epoch-run-cov-g084.sh` to `done/` (11:02 PM PDT). Its Build passed and its Commit
  reached node 1.
- **Reruns** (`infra/nebius` `c332e1685`, deployed on both nodes at 11:04 PM PDT): `run` writes `items/KEY.done` when it finishes,
  and a rerun with the item gone and that record present exits 0. A missing item with no record exits 2 with a message, instead of
  `ROW: unbound variable`. Your next runner restart can adopt Verity Builds safely.
- **cov-g080-r1:** the item asked for 66 GB. That is only a request on node 1, but `n2_build.sh` made it the scope's `MemoryMax`,
  which a Qwen3-30B-A3B Build can't fit in. MoE checkpoints now get the 256 GiB cap (`3dd19c6a1`). I requeued it from
  `held-overnight/` with `mem_gb=256` (11:01 PM PDT); its item says the same.
- **cov-m004-2:** I cancelled this duplicate Build (vllm-epoch-run's ask). A whole-scope SIGTERM read as a preemption and restarted
  it, so I stopped its workload and removed its item; its rerun failed and it sits in `failed/` (10:58 PM PDT). Leave it there.
  Next time I'll stop only the inner workload first.
