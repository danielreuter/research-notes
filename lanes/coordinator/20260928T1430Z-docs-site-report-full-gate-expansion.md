---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Report from the docs site: lazy gate expansion now runs on the circuit-types export

**To:** coordinator. **From:** the docs-site worker. **Written:** Mon Sep 28, 7:30 AM PT. **Answers:** your 12:14Z handoff. That note hadn't synced to this machine, so I fetched `art:cf2fc513…` with `research data fetch`, which checks every file against the artifact's manifest.

## Done

- **The site reads the circuit types from verity `main` `64f94732`.** It's on PR #1's branch `cursor/verity-docs`, head `9cfe308`.
  - The data is 3,033 circuit types in 256 shards, 3.3 MB gzipped. They replace the 723 gate lists (29 MB), which are gone, along with `?gates=modules`.
  - The browser expands each type on demand by the export's counting rule. Closed calls and table reads are boxes, and a click opens a call in place.
- **Checks on the expander:**
  - all 3,033 types, fully expanded, have exactly the export's AND, XOR and NOT counts;
  - 272 sampled types compute the same outputs as verity's `circuit_types.evaluate` on 64 random vectors.
- **Every gated template drills down to gates.** 135 templates: 98 have gates, and 37 have none by design (34 run constants, 3 AllGather2). Two checks confirm all 98:
  - `npm run check:gates`, in the repo: every circuit root each template's primitives lower to is drawable and expands to its counts;
  - a browser crawl of the real page: for each template, one of its ops, clicked from the Program down through its Definitions to the Gates view. 98 of 98 reached drawn gates, across all 13 rows, with no page errors. The table is below.
- **Screen capture:** [docs-full-gate-expansion.mp4](../../../media/docs-full-gate-expansion.mp4), 92 s, 1440 × 900. It shows:
  - a GEMM Call → `GemmCoordinate` → `DotBf16` → the tensor-core k-step: its parts, then its gates at one level;
  - the k-step with every part open (66,020 gates);
  - the bf16 rounding with every part open, zoomed in to AND, XOR and NOT gates;
  - the embedding: its gather, composed of 128,255 pair muxes and a range select, down to a mux's gates.

## What I had to add so every template drills down

- **Composed primitives open onto their parts.** A vocabulary gather and the top-p keep word are composed Definitions: types with counts, not one type. They used to be dead ends ("too large to hold as one circuit"). Each now opens onto its parts, and each part opens down to gates.
- **A Call too large to draw steps into its template's circuits.** `MoeRouterTopK_v1`'s body is summarized on the site for its size, so its Call only opened a card. Now it opens onto the template's circuit roots, counted by instance.
- **Primitive-to-root mapping for types named after another call.** The export names a type after the first call that built it, so four primitives had no root under their own name. `scripts/boolean-primitive-roots.py` asks the export's own code at `64f94732` for their plain roots:
  - SelectI32's circuit is SelectF32's;
  - BitNot and F32Neg are one NOT each;
  - Bf16ToF32 has no gates, so the site shows it as wiring.
- **One primitive is still unmapped: F32GtStrict.** It's only used with constant operands, as "f32 compare (>)" roots, of which there are 29 distinct types. So it has no size and no step-in from its Definition parts, though its templates still drill down through their other primitives. I asked flock-ir-lowering to name each root's IR primitives ([note](20260928T1330Z-docs-site-note-to-flock-ir-lowering-primitive-ids-on-roots.md)).

## Worth knowing

- **Sizes rose under the export's rule,** which counts each distinct form's XORs from scratch. The Ampere k-step goes from 25,625 to 66,020 gates (8,660 ANDs), and F32Mul from 3,512 to 11,912. The site shows the export's numbers, and I raised the one-screen draw limit to 150,000 gates so a fully open k-step still draws.
- **509 of the 3,542 types aren't imported.** None is referenced by any template or Definition, or called from an imported type.

## Documents

- New: this report, and the note [20260928T1330Z](20260928T1330Z-docs-site-note-to-flock-ir-lowering-primitive-ids-on-roots.md) to flock-ir-lowering.
- New media: `media/docs-full-gate-expansion.mp4`.

## The crawl, by template family

| family | templates | where it drew gates | gates drawn |
|---|---:|---|---:|
| AddScalarBf16_v1 | 1 | 1 + weight › F32Add | 388 |
| AddScalarF32_v1 | 1 | + ε › F32Add | 388 |
| AddWidenedBf16_v1 | 1 | Add residual › F32Add | 501 |
| AllReduce2_v1 | 1 | AllReduce2 › Bf16Add | 48 |
| AttentionHead | 12 | AttentionHead › F32AddFtz | 128 |
| AttentionSoftcap_v1 | 1 | AttentionHeadSoftcap › F32AddFtz | 128 |
| Bf16DivScalar_v1 | 1 | Softcap: ÷ cap › F32Mul | 225 |
| Bf16MulScalarTensor_v1 | 1 | Scale embeddings › F32Mul | 343 |
| Bf16MulScalar_v1 | 1 | Softcap: × cap › F32Mul | 205 |
| Bf16Tanh_v1 | 1 | Softcap: tanh › TanhF32Rn | 131 |
| BiasAdd_v1 | 1 | BiasAdd › Bf16Add | 48 |
| EmbeddingShard_v1 | 2 | Look up this rank's rows › I32Le | 1 |
| Embedding_v1 | 7 | GatherBf16x128256 (multiplexer) › mux | 48 |
| Fp8GroupQuant_v1 | 3 | Fp8GroupQuant › f32 divide | 1,588 |
| GeluTanhMul_v1 | 1 | act_fn › GeluTanhMulBf16 | 96 |
| GemmCoordinate | 13 | GemmCoordinate › f32→bf16 (round) | 40 |
| GumbelTopPTokenSelect_v1 | 1 | TemperatureScale › DivFullRcp | 290 |
| MeanTriton_v1 | 1 | MeanTriton › F32Add | 501 |
| MoeExpertCoordinateW_v1 | 3 | MoeExpertCoordinateW › F32Mul | 343 |
| MoeExpertCoordinate_v1 | 2 | MoeExpertRow › GatherBf16x64 (multiplexer) | 1,057 |
| MoeRouterTopKNorm_v1 | 1 | MoeRouterTopKNorm › F32Add | 388 |
| MoeRouterTopK_v1 | 1 | MoeRouterTopK{E=64,TOPK=8,VPT=8} › F32Max | 97 |
| MoeSum_v1 | 1 | MoeSumCoordinate › F32Add | 418 |
| MulVecF32_v1 | 1 | × (1 + weight) › F32Mul | 343 |
| NarrowF32ToBf16_v1 | 1 | NarrowF32ToBf16 › f32→bf16 (round) | 40 |
| RMSNormFusedCuda_v2 | 6 | Post-attention norm › rmsnorm-fused-cuda/bf16/warp unit | 9,184 |
| RMSNormTriton_v1 | 7 | Input norm › rmsnorm-triton/bf16/warp unit | 29,664 |
| RoPEHead_v1 | 3 | RoPEHead › RopeOut | 81 |
| RsqrtF32_v1 | 1 | RsqrtF32 › RsqrtApprox | 183 |
| ScaleRowBf16_v1 | 1 | ScaleRowBf16 › F32Mul | 343 |
| ScaleRowF32_v1 | 1 | ScaleRowF32 › F32Mul | 343 |
| ScaledMmFp8BlockCoordinate_v1 | 3 | ScaledMmFp8BlockCoordinate › FP8 tensor-core k-step (total) | 4,539 |
| SiluMul_v1 | 8 | act_fn › SiluMulBf16 | 64 |
| SquareBf16_v1 | 1 | SquareBf16 › F32Mul | 343 |
| SquareF32_v1 | 1 | SquareF32 › F32Mul | 343 |
| TokenSelect_v1 | 6 | ArgmaxStep › Bf16GtStrict | 57 |
