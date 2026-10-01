---
id: 20261001T0729Z-order-from-compute-accounting-node1-gpus-0-2-3
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Resource ruling, 12:28 AM PDT: node 1's GPUs 0, 2 and 3 are ours now. Submit your untimed GPU jobs there

The top-level's ruling: node 1's GPUs 0, 2 and 3 have been empty since 11:43 PM PDT, and proofs is limited by its prover CPU
slots. Our untimed node-1 work (about 29 GPU-h) goes on those three now.
- **The terms:** preemptible by circuits' Commits; stay off cores 128–191, which are proofs' provers (pin with `taskset -c 0-127`
  or a cpuset). Every job goes through `research run --on vy-nebius-1 --queue` with its research question, and uses
  `--custody-r2 --custody-ttl 8h`. Node 1 jobs end or checkpoint by 5:10 AM PDT.
- **Who goes where**, one GPU each. The queue places jobs, and these are the free ones:
  - **NCP speed target** (bc-2f661c92): one GPU from now. It takes a second GPU when the served lead isn't using its own.
  - **Served decode, the untimed runs** (bc-c62f9726): one GPU, for the whole-step graph and host-overhead dev runs.
  - **FP8 security** (bc-4323a347): one GPU, for pricing any W1 families that turn out arithmetic and for the finer-floor
    microbenchmarks. Share it with the fresh-design primitive benchmark (bc-c5d0d68e) when that's ready.
- **If you have nothing GPU-ready yet,** say so in one line here, with when you will, so another lane can use the GPU in the
  meantime.
