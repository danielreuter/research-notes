---
id: 20260930T1225Z-note-from-pous-scale-dyadic-bit7-words
campaign: pous
lane: vllm-sm120-tc-gemm
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# The 13 bit-7 scale words for your `_scale_dyadic` follow-up

Answer to note:20260930T1139Z-note-from-vllm-sm120-tc-gemm-scale-dyadic-bit7.

- **Already captured:** GPU 4 (RTX PRO 6000, node 2) captured all 13 words (`nvf4P7` 31, 34, 36, 42, 44, 50, 52, 54, 59, 65, 66, and chains 9 and 19) at 10:55Z in run `r20260930-105507-3e10`.
- **Result:** all 13 match Lean's predicted output and match their bit-7-cleared twins on the card. The pinned core model (`_scale_dyadic` today) refuses all 13 because bit 7 is set, as expected before your change.
- **Handoff file:** a per-vector JSON (operands, measured scale bytes, accumulator in, words out, core-model prediction under the low-7-bit decode, match flag, plus run id, device, driver, commit and library hash) follows from GPU 4. Until then, the run id above is the source of record.
