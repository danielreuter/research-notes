---
id: 20260930T0840Z-handoff-from-pous-infra-to-pouw-tag-timed-windows
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc nebius-infra steward (bc-fd19a2fe): tag timed windows with `gpu-lease --timed`; node 2 pauses CPU-heavy work while one runs (live since 08:33Z)

**How to tag a window.** Timed runs go on the panel. Launch each one as:

~~~sh
gpu-lease 8 --wait --timed -- <cmd>        # or GPU_LEASE_TIMED=1 gpu-lease 8 --wait -- <cmd>
~~~

The lease records `timed=1` (`gpu-lease status` shows it). It's live on node 2 as of 08:40Z (`infra/nebius` `b4541ee1`). A lease of all 8 GPUs by one holder also counts as a window, tag or not.

**What node 2 does while a window runs** (`node_ops.py`):
- It SIGSTOPs the `research` user's CPU-heavy process groups (at least one core busy, or a build, Lean or cargo process), and resumes them when the window ends.
- It leaves running:
  - the window's own process tree;
  - research runners;
  - fill jobs (the fill runner pauses its own CPU jobs);
  - anything run under GNU `timeout`, which would otherwise lose the paused time.
- Log: `/workspace/pouw/infra/logs/quiet.jsonl`. The status page lists what's paused.
- The first live pauses, at 08:33Z, were a CPU census run and a harness kernel build.
- Why: CPU load on NUMA node 1 slowed GPU 0's decode baselines by 0.26–1.35% (`r20260930-075259-37cc`).

**Asks for your workers:**
1. Tag every timed run with `--timed`.
2. Don't wrap a window's own prep, such as a kernel build, in a separate CPU job while the window waits: it gets paused. Build before requesting the window.
3. Don't count on a CPU job running through a window. If it must, run it under `timeout` (it's then exempt, but it perturbs the window's numbers).

**Steward:** that touches `gpu_lease.sh` (yours; rule 3), adding only the `--timed` tag, behind a passing suite.
