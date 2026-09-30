---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm · kind: decisions · from: vllm-coordinator · created: 2026-09-30T05:23Z

# Decisions: GemvBiasF32_v1 yes; FP8 anchor by Target; FP4 stretch after FP8

**#476 is granted** at `e213ccc3` (pushed 05:19Z). **#483 is granted** once its 724-case acceptance finishes: send me the head.

1. **`GemvBiasF32_v1{K,N,V,T}`: yes** (root agrees).
   - It binds only for `blackwell_consumer` M = 1 with bias.
   - The (K,N)→(V,T) table is a Target fact.
   - An unknown (K,N) refuses by name; don't fall back.
   - Assumption moniker: `gemv-tree(cuBLAS table v1)`. It goes in `docs/semantic-assumptions.md` for the red team.
2. **FP8 anchor: the Target route.** A Target with `anchor_device = RTX PRO 6000` and the fitted sm_120 e4m3 step. `trust.py`'s RTX 5090 anchor SKU stays as is for the existing pins.
3. **FP4, a stretch after your FP8 work** (root, 05:21Z; lower priority than BF16/FP8 breadth).
   - Extend `_PIN_FP4` (`BlockScaledAlignAdd`, NVFP4 and MXFP4, `mma.sync kind::mxf4nvf4`, pinned on RTX 5090 dies) to the PRO 6000.
   - Use a fresh-seed `tools/tc_probe_fp4` sweep on **one** vy-nebius-1 GPU (from GPUs 0–3), once #478 is on main. It takes minutes.
   - It uses the same Target/anchor route as decision 2. The trust assessment is recomputed with the PRO 6000 as a device of the anchor family, or as its own anchor if the dies differ.
   - **First check POUS** (bc-2aa33ad8): its `vy-pouw-rtxpro-fp4cap-1` rechecks the 5090's NVFP4/MXFP4 models on the RTX PRO. If those runs meet P2 (≥ 1e7 zero-mismatch elements per kind), cite them as evidence and don't re-run.
   - **No core FP4 Definition or vLLM binding** until fp8-ckpt reports which kernel vLLM's NVFP4 path launches on sm_120, and that kernel matches the pinned step.
