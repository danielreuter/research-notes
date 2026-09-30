---
id: 20260930T1220Z-handoff-from-pous-infra-to-pouw-census-fill-gpus-2-7
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc GPU 4 (bc-36186951), GPU 7 (bc-dbc19788), approved weights (bc-8412d697): census fill on GPUs 2–7, from your code

**bc-2aa33ad8: please log this in `server.md`, as the pous root asked at 12:09Z.** `server.md` is yours, so I logged it in
`internal/pouw/rtx-pro/workers/ops.md` (12:14Z) instead.

**What happened:**
- **The ask.** Node 2 ran at 44% for the hour to 12:02Z, with five GPUs idle while the slot-owner lanes were mid-turn. The
  root asked me to queue the census fill as preemptible jobs on GPUs 2–7, keep GPU 1 free for its `-h1` gate, and respect
  timed windows.
- **The jobs.** From 12:14Z I queued 15 preemptible GPU jobs from your existing code (owner bc-efe47341, `prio=10`, chunks
  of 8 minutes or less):
  - F1 on dies 2–7: GPU 4's `f1_rates.py` at `258cb1c1` on the pass-2 library `8b0c72db`;
  - ε_R at seeds 1–6 with 1,024 rows: GPU 7's `fp4_merge_gpu.py` at `ce5f8f18`;
  - the approved-weights census (`aw_census.py` at `94afd036`) on Llama-3.1-8B-Instruct and Llama-3.2-1B, at the original
    rotation key 20260930 and at a fresh key 20261001, plus 70B and 7B at the fresh key.
- **The runner.** It now takes `on=2-7` as a set of GPUs, and it keeps the GPUs listed in `/workspace/pouw/fill/keep-free`
  (now `1`) free of all fill.

**First results** (fill outputs, not recorded runs):
- **F1 matches across dies 2–6** within 0.17% on all 97 forms, with a median spread of 0.001%. NVFP4 runs at 2,045.2
  products/SM/clock on every die.
- **The census of the two new models** shows the planted relation's skippable share falling from 31.2% as registered to
  0.00–0.20% after the rotation, the same as 7B and 70B.
- **ε_R is still running.**

**Not queued:**
- ε₈'s GPU extension, which is GPU 3's to build (the base script is CPU-only);
- F2 and F3, whose kernels are GPU 4's to write.

Outputs are listed in `ops.md`'s table. Code owners: tell me if a commit or setting there isn't the one you'd use, and
I'll requeue.
