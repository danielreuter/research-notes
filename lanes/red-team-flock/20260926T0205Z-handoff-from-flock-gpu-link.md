---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:03Z
---

# For review: Chunk(4), bf16-ampere at K = 2048 on the captured #101 set

- **Same code as my 01:59Z note.** This is the first layout with the epilogue: the Y region sits at chunk 3, and three
  committed cross-chunk accumulators chain the four chunks of a VU.
- **Inputs:** captured, art:123dc234. The generator asserts that every recorded y.u16 equals f32_to_bf16 of the model
  chain.
- **Evidence:** run r20260926-014936-28eb, art:0f5e418a. CPU and GPU selftests pass on the A100 at 8 and 64 VUs, including
  `y16_public_forged` and `committed_acc_differs_from_block_acc_out`.
