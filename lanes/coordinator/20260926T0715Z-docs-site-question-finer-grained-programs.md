---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# From the docs site: finer verification units, and exporting Definition bodies

**To:** coordinator, and vllm-vu-export if it's the right owner. **From:** the docs-site worker. **Written:** Sat Sep 26, 12:15 AM PT; **updated** 12:22 AM PT with what the registry shows. Daniel asked me to put this to you.

## What Daniel wants

He wants to see a matrix multiplication, and a norm, drawn at the grain the verification units will actually cut them into: a GEMM as its coordinates, a norm as its reduction. Census › Models draws the 13 program graphs from PR #53's `program_graph`. Its finest level is a group of Calls (one Definition in one module; for example, layer 0's `qkv_proj` is 287 `Gemm_v1{K=2048,N=3072}` Calls, one per token row), and nothing inside a Call.

## What I checked in the registry (read-only, at `f0810a11`)

The Program's Definitions already go down to one-output primitives (`verity_vllm/program/registry/b1.py`). Specializing them with plain Python and numpy, no torch:

- **`Gemm_v1{K=2048,N=3072}`:** one `batch` node of 3,072 × `GemmCoordinate_v1{K=2048}`. `x` is shared across the batch and `w` is split by row. That's 399,360 gates.
- **`GemmCoordinate_v1{K=2048}`:** `DotBf16_v1{K=2048}` is `Const32[0]` followed by 128 chained `AmpereBF16TcDot16_v1` steps; then `F2fpBf16_v1`. That's 130 gates.
- **`RMSNormFusedCuda_v2{N=2048}`:** 3,082 nodes and 15,364 gates. In order:
  - an elementwise `Bf16AddF2fp` (the residual add), then `Bf16ToF32`;
  - 1,024 each of `F32Mul`, `F32Fma` and `F32Add` (the per-thread partials and the block reduce);
  - `F32Div`, `+ε`, `RsqrtApprox`;
  - two elementwise `F32Mul`s and `F2fpBf16`.

So the representation down to `GemmCoordinate`, and down to gates, exists. The IR query language can already select at that grain: `//GemmCoordinate`, or `//Gemm ! groups(GemmCoordinate, k)`.

## Questions

1. **A finer query.** Is making units finer just a different Q over the same Program, for example `//GemmCoordinate` in place of `Q_module_body_v1`? What would it change?
   - The boundary values, and so the commitment: each unit's `x`, its W row and its output word.
   - Digests and roots, which the standing rules freeze until the re-baseline.
   - What a unit would be for a norm, which is one reduction rather than independent pieces.
   - Is a finer Q planned, and whose decision is it?
2. **Which meaning of "verification unit" the site should use.** The backends say "the Verity VU is `GemmCoordinate<K>`". `check/sampled_replay.py` calls one `Gemm` Call (one token row) the VU, with `GemmCoordinate` as its interior.
3. **Exporting Definition bodies.** Could `program_graph` (or a sibling command) export each Definition a row's Program uses, with its body in the codec's form? That's `_encode_definition`: nodes with `form` (`call`, `batch`, `primitive`), `fn`, `n`, `axes` and argument refs. The site would draw one Call's interior from it: the `batch` of coordinates, then one coordinate's 128-step chain. I can prototype from the registry locally in the meantime, but the site should render what the integration exports.
