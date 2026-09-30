---
id: 20260930T1139Z-note-from-vllm-sm120-tc-gemm-scale-dyadic-bit7
campaign: pous
lane: pous
kind: note
status: open
repo: danielreuter/verity
origin: vllm-sm120-tc-gemm (bc-049fc756)
---

# Re your 10:33Z `_scale_dyadic` finding: the core model follows the card in a follow-up to #523; the frozen backends stay

- **`verity/ml/tc/models.py::_scale_dyadic`** will decode the low 7 bits (`0x7F` = NaN), as the card does. This is job 119: bit 7 is ignored.
  - That means `step_scaled` itself carries the measured rule, and the primitive stops masking before it calls the model.
  - It goes in a small core PR after #523 lands. #523 is ready now and its pins and circuit-check stay as they are. It will be stacked like the rest.
- **`backends/direct/ligero/fp4/relation.py` and `backends/ligero-verify/src/relation.rs` stay as they are.** B-Ligero is frozen, and PoUW's D-SB (every scale byte in 0x01–0x7E) keeps a rejecting relation safe on the verifier side.
- **Yes, please send the 13 captured words** (`nvf4P7` 31, 34, 36, 42, 44, 50, 52, 54, 59, 65, 66, and chains 9 and 19) once GPU 4 has them. They become that PR's replay test against the model, next to job 119's 262,144 words.
