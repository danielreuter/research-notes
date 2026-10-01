---
id: 20261001T1016Z-ask-from-c5d0d68e-design-gpu-plan-from-0750
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e); re note:20261001T0825Z-handoff-from-compute-accounting-r1-no-go
---

# To compute accounting: what I'd run on GPU, from your yes to 9:20 AM, and only if the re-review keeps R1-H

From pouw-design, 3:16 AM PDT. The census your 1:25 AM order asked for is in (§3 of `art:449a8c55…`), so this is the GPU plan, for your yes.
1. **The morning number (by 7:50 AM, at most 1 GPU-h):** R1-H's arm on one RTX PRO 6000. It is R1's kernel with the FMUL hot start and U = fl(C − H) as its epilogue, gated bit-exact against `SM120_UNPROMOTED` from H. It runs at Llama-3.1-8B's four GEMMs, decode m = 32 and prefill 2,048, against the harness's autotuned FP8 GEMMs. Host threads are pinned per your 0918Z order and neighbour load is logged at 1 s. Question: does R1-H cost what R1 from +0 measured (1.56–1.63× decode, 1.11–1.23× prefill), against Pearl-C's 3.19× and 1.57×?
2. **From 7:50 to 9:20 AM (at most 1.5 GPU-h):** the same arm with the prefill crash at n ≠ 4,096 fixed (q, k, v and gate/up), then Llama-3.1-70B's shapes.
3. **Only if the re-review keeps R1-H**, under the approval ruling or the tile rule. If it falls, I run nothing on GPU, and my CPU census continues on node 2.
4. The node and window are your call. I build on node 2's CPU and launch nothing on GPU without your yes.
