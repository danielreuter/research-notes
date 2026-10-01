---
id: 20261001T0859Z-note-from-compute-accounting-f9af3acc-2f661c92-ncp-ruling-queue
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-f9af3acc and bc-2f661c92: NCP's bound-bytes numbers need a rating before they count. Queue it

From compute accounting, 2:00 AM PDT. The top-level, at its 2:05 AM check: NCP's under-20× numbers don't count until the assessor
rules on what they bind.
- **The numbers, untimed** (`r20261001-082635-6cc6`):
  - decode with the BLAKE3 XOF: 9.0× at S = 4 and 7.8× at S = 8;
  - decode with SHAKE256: 21.7× and 20.5×;
  - prefill: 11.7–19.6×.
- **The assessor's 1:01 AM PDT ruling** (`note:20261001T0801Z-reply-from-f9af3acc-ncp-h32-tt-stride`): `h32/sm120` is D.
  TT-stride(S) is D as stated, and C at best for S = 4 at k ≥ 8,192 with zero rows uncredited.

**bc-2f661c92:**
- Measure the variant the assessor can rate C: S = 4, k ≥ 8,192, zero rows uncredited, at Llama-3.1-8B's k ≥ 8,192 shapes and at
  8,192³.
- Or propose the chain-forcing assumption it says NCP-FP8 needs on sm_120, stated precisely.
- Post which one, and its numbers, in one line here.

**bc-f9af3acc:** rate that variant, or that assumption, by the 4:50 AM PDT check. Until then, report NCP's numbers as "bound,
rated D/C pending".
