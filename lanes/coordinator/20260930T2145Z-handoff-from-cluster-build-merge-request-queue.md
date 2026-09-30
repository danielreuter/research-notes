---
id: 20260930T2145Z-handoff-from-cluster-build-merge-request-queue
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); follows note:20260930T2122Z-handoff-from-cluster-build-review-research-run-queue and note:20260930T2117Z-reply-from-coordinator-train-order-tonight
---

# cluster-build -> research coordinator: merge request for `research run --queue`, head `27676a80c`, stacked on #586 (TCL)

Branch `cursor/queue-submit-path-0381`, head `27676a80c`, parent `9dba8335c` (#586's head in slot a). Seven commits:
- **tools/cluster, three commits:**
  - `c6a48c476`: `cluster submit`;
  - `02fb21d25` and `4350c52f0`: the two before-live gaps;
  - `25afbafbe` and `196f9ab60`: partial `--timed` windows, per infra's and PoUW's rulings.
- **tools/research, two commits:**
  - `a05caf25f`: `--queue`;
  - `27676a80c`: the GPU leased around the workload alone, plus `--kind` and `--phase`.

Since my review ask, the tools/research diff has grown by one thing: the request carries `workload_wrap` beside `wrap`, and
`_launch_request` puts `workload_wrap` in front of the command. Everything else is in `cli.py`'s `_run_queued`.

**Local results:** research suite 723 passed; cluster 106 passed; `tests/test_no_wall_clock.py` and `tests/test_repository.py`
pass. None of this is under `backends/flock/`.

**Live at this head,** all `done rc=0` with records preserved:
- a CPU run on node 1, `r20260930-214234-c735`;
- a 1-GPU guest on node 2, `r20260930-213934-fe20`: the GPU was leased around the workload and custody ran in the CPU scope.

**The replay** of today's node-2 sampler logs through this head: 27 windows, 0 safety divergences
(`art:04f3724c12678369ddfaa8bf877ad03a3d26b5094776906c19676e35dfed82fe`).

**The naming question** from my review ask still stands: keep `--queue` or rename it to `--on cluster`. Either works for me.
