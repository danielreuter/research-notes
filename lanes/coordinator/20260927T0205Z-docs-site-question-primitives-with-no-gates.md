---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Question from the docs site: the primitives with no gates yet

**To:** coordinator. **From:** the docs-site worker. **Written:** Sat Sep 26, 7:05 PM PT. Daniel keeps clicking into primitives and finding nothing below them. The latest was the embedding's `GatherBf16x128256`.

## What the site does now

A primitive with no Boolean circuit is drawn dashed. Clicking it now opens a card that leads with "No gates below this yet" and gives the export's reason. The site can't draw gates the Boolean export doesn't have. In the export, **13 of the 66 primitive types** the served rows use have Boolean circuits. The other 53 don't, per [the dataset's README](../../datasets/boolean-circuits/README.md) under "Not yet lowered":

- **the embedding's row gathers**, `GatherBf16x{V}`, in every row. The export's reason: "a row gather by token id (data movement from the committed table); no Boolean lowering yet";
- **attention's softmax:**
  - `F32Max`;
  - the FTZ adds, multiplies and fused multiply-adds;
  - `MufuEx2Ftz`, `GuardNegInfZero` and `Fa2InvSum`/`Fa3InvSum`;
  - for gemma, `MufuTanh` and `TanhF32Rn`;
- **the norms' row scalars:** `RsqrtApprox`, `DivFullRcp`, `DivFullScaleA` and `MufuSqrtFtz`;
- **token selection:**
  - Gumbel top-p: `GumbelStreamKey`, `GumbelNoiseLane`, `TopPMaskWordx{V}` and `BitAtx{V}`;
  - greedy argmax: the compares and selects;
- MoE routing's comparisons and selects;
- GELU-tanh · mul;
- FP8: `F32ToE4m3Sat` and `HopperE4m3QgmmaDot32`.

The most common reason given is "ir_lower has no piece for this primitive yet".

## Questions

1. **Is lowering these planned, and in what order?** By size, the tensor-core steps dominate and are done. By what Daniel clicks, the gather, softmax and sampling come up first.
2. **Will the gather ever be gates?** The architecture's ZK-Flock list has "the embedding by private opening". If a row gather is checked as an opening of the committed table rather than as a circuit, the site should draw it that way, not as "not lowered yet". What should it say?
3. **Anything I should show in the meantime?** For example, each primitive's exact model (its docstring) is already on its card, and those docstrings are tested against production where the status says so.

The PR question is separate: [20260927T0138Z](20260927T0138Z-docs-site-question-what-to-do-about-the-prs.md).
