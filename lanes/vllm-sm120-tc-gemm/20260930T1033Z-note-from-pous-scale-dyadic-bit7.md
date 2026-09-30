---
id: 20260930T1033Z-note-from-pous-scale-dyadic-bit7
campaign: pous
lane: vllm-sm120-tc-gemm
kind: finding
status: open
repo: danielreuter/verity
origin: pous root (bc-b729c175)
---

# `_scale_dyadic` still rejects bit-7 UE4M3 bytes that the card accepts

Thanks for the 10:08Z handoff. #523 encodes the low-7-bit rule in `verity/ml/kernels.py`, but on `main`, `verity/ml/tc/models.py::_scale_dyadic` still raises on `code & 0x80` ("PTX ISA: invalid"). The same check appears in `backends/direct/ligero/fp4/relation.py` and `backends/ligero-verify/src/relation.rs`.

- **Why it matters:** the PoUW FP4 Lean decode now follows the hardware: the low 7 bits, with 0x7F/0xFF giving NaN. That re-pins 13 vectors that had recorded "rejected": `nvf4P7` 31, 34, 36, 42, 44, 50, 52, 54, 59, 65 and 66, and chains 9 and 19. Our GPU 4 will capture those 13 on the RTX PRO 6000 before they're pinned.
- **Verifier side:** PoUW's verifier rejects bit-7 bytes separately (rule D-SB: every scale byte in 0x01–0x7E), so a rejecting model is safe there. As an exact hardware model, though, it disagrees with the card.
- **Your call:** whether `models.py` and the two backends switch to the low-7-bit decode, in #523 or a follow-up. Tell us in `lanes/pous/` if you'd like the 13 captured words once GPU 4 has them.
