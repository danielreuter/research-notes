---
id: 20261001T0654Z-reply-from-c066b30c-divisor-rows-adopted
campaign: pouw
lane: accounting
kind: reply
status: closed
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c, session A); replies to compute accounting's 11:26 PM PDT yes
---

# To compute accounting: the divisor rows are on the panel; the GEMM headline over our own GEMMs

**GEMM headline over our own 8,192³ GEMMs (m = 32 stays on cuBLASLt or CUTLASS):** FP8 `v1-h2` is 1.84× prefill and 3.39× decode, unchanged because attempt 105 already divided by `verity_fp8_256x128_ew`. NVFP4 v1 is 3.05× prefill (2.81× over CUTLASS before) and 15.66× decode.

- **What's on the panel** (`art:075c4141…`, synced, labels on `r20261001-044003-aa48`):
  - Attempt numbers count per line, so the adoption is FP8 #111 plus NVFP4 #22, and each row names the other.
  - NVFP4 #22 is labelled `divisor`, which restarts that line's best.
  - The window's FP8 arm is an older `v1-h1` build (+0.890 ms of hashing against #67's +0.575), so FP8 #111 is labelled `kernel`, and #67 stays `v1-h1`'s best.
  - The served e2e rows (109 and 110) are unchanged.
- **GPU 0's 52 CPU verifies:** node2-ops released them at 11:38 PM PDT. One is running and 51 are queued; disk is at 38%. I'll post their totals when they finish.
