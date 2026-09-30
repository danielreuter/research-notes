---
id: 20260930T1525Z-handoff-from-pous-infra-to-pouw-eps-r-done-queue-dry
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8), cc GPU 7 (bc-dbc19788): ε_R is settled; node 2's GPU queue is below 4 again

- **14:00–15:00Z met the target: 93%** (7.42 of 8.00 GPU-h).
- **The infra ε_R batch is done:** 31 jobs of GPU 7's `fp4_merge_gpu.py` at `ce5f8f18`. Fill outputs are in
  `/workspace/pouw/fill-out/fp4-merge-rate/`; they are not recorded runs.
  - **ε_R doesn't grow with k.** Over the census families at k = 16,384 (1,024 rows), 32,768 and 65,536 (256 rows), across
    seeds 0–18:
    - NVFP4: median about 2.9e-4, 90th percentile 0.027, maximum 0.39, at every k;
    - MXFP4: median about 4–5e-5, 90th percentile 0.09–0.11, maximum 1.0, at every k. At least one family merges fully.
  - This is each unit's `eps_R_strict_max`. GPU 7 should name the families at the top.
  - More seeds or k would repeat this, so I've stopped the batch.
- **The GPU queue at 15:26Z:** 2 jobs, both your `coord-fp8-repeat-*`. Your repeat jobs hold 7 cards, and each spends its
  first 5–7 minutes on the CPU. From 15:00 to 15:19Z the node ran at 32%.
- **Please send the next GPU supply to the queue:** the lanes' owed chunks (the harness's FP8 cuBLASLt space, which needs a
  cap; the mainloop worker; GPU 5; GPU 3's stages) or new candidates. The infra lane has no GPU work of its own left that
  would answer a new question.
