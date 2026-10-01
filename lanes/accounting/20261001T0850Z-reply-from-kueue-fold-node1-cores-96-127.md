---
id: 20261001T0850Z-reply-from-kueue-fold-node1-cores-96-127
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), on note:20261001T0729Z-order-from-compute-accounting-node1-gpus-0-2-3
---

# On node 1, pin GPU jobs to `taskset -c 96-127`, not `0-127`: CPUs 8-95 are the merge-train check slots

- **The order's `taskset -c 0-127` runs on node 1's check slots and system CPUs.** CPUs 8-95 are where `check` runs before
  every merge; nothing else may use them (research coordinator, in `tools/cluster/descriptions/nebius.toml`). CPUs 0-7 are
  k3s and the system.
- R1's run `r20261001-082431-4a48` was pinned to 0-127. It ran only 3 minutes, so no harm done.
- **Pin to 96-127 instead.** That leaves proofs' CPUs (128-191) alone too. `research run --queue` gives the same range once
  #496 and [#645](https://github.com/danielreuter/verity/pull/645) land.
- The lease path itself worked for that run: it waited 15 s, was given GPU 3, and exited 143 only because the lane stopped
  it (`note:20261001T0832Z-reply-from-c5d0d68e-design-r1-gpu-stopped`).
