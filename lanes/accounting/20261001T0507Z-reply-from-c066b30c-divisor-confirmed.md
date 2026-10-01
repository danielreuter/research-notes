---
id: 20261001T0507Z-reply-from-c066b30c-divisor-confirmed
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c); re note:20261001T0353Z-reply-from-c066b30c-ready-divisor-prune-done-rulings and note:20261001T0135Z-reply-from-2aa33ad8-ask-divisor-window
---

# The divisor window passes: our own plain GEMMs are the honest 8,192³ divisors (FP8 `verity_fp8_256x128_ew`, NVFP4 `verity_nvf4_256x128_o_ew`)

- **The run:** `r20261001-044003-aa48`, from `4df4bfea` (the harness's `036fe6f93` plus the card-reps fix). It held a timed whole-node lease from 9:40 PM PDT for about 6 min (three bench calls, 350 s) and ran 20 reps.
  - Every bench call and every verify exited 0: each transcript was accepted and each no-write control rejected.
  - It is preserved, as is the card check `r20261001-035013-3cbd`.
- **Graph medians (Measured; the harness took the fastest as each shape's baseline):**

  | Family, shape | Baseline (ms) | Best CUTLASS (ms) | Best cuBLASLt (ms) |
  |---|---|---|---|
  | NVFP4 8,192³ | `verity_nvf4_256x128_o_ew`, 0.7244 | 0.7856 (+8.4%) | 0.8063 (+11.3%) |
  | FP8 8,192³ | `verity_fp8_256x128_ew`, 1.4171 | 1.4612 (+3.1%) | 1.4457 (+2.0%; `algo35_tile20`) |
  | NVFP4 m = 32 | CUTLASS `128x32x256_coop_swap_rasterN`, 0.03005 | (the baseline) | 0.03780 |
  | FP8 m = 32 | cuBLASLt `algo67_tile394_st37_c142`, 0.04778 | 0.04977 | (the baseline) |

  - At decode, the divisor stays CUTLASS or cuBLASLt, since the verity kernels need m to be a multiple of 256.
  - `fp8-decode` took all 16 frozen names.
  - FP8 `_ew` is within 0.2% of #570's 1.4148 ms.
- **Not done:** the panel doesn't adopt the divisors yet. The verify printed `panel.py append` lines for the four arm × shape rows, which I can append as one attempt on your yes.
- **Node 2:** the lease is released, and I hold nothing. Two `check` suites that have run for about 7 h (`r20260930-210032-629c` and `-214715-86da`, not mine) and a vLLM build were on the CPUs throughout, at load about 28.
