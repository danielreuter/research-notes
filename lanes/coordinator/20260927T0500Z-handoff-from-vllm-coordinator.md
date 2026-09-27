---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T05:00Z

# Merge request: PR #106 @ df13126f (FP8 block scale products computed once, `ScaledMmFp8BlockSharedScale_v1`, opt-in): APPROVE

The lane's handoff is `vllm-coordinator/20260927T0445Z-handoff-from-vllm-rf-recompute-fp8.md`.
- **Merges:** one commit on main 3040ac1f. Additive only: 52 lines in `registry/fp8.py` plus a test file. It merges cleanly with main and
  with every queued PR (#98, #99, #102, #103, #105).
- **Opt-in:** a `SHARED_SCALE` map in #101's style; nothing binds the new Definitions.
  - On main and on #106, `ScaledMmFp8Block_v1` encodes identically (spot check: `38c97e3b…` at K=256, N=256, G=128).
  - The lane shows all 229 Definition specializations of #74's and #57's request Programs byte-identical, so no Program, manifest or
    verdict of record moves.
- **Checker on #74 with the selector on:** 113,639,803,200 recomputed gates → **0**, and 4 violations → 0. Widths: committed units are
  32 bits, outputs 16. The cost is +894,801,600 committed words on the row (3.58 GB, +17% of #74's committed interior), the price of the
  no-recompute rule for this kernel's scale layout.
- **Equivalence:** the same circuit after interning the gate DAGs (3 shapes), and bit-equal on e4m3/f32 edge vectors (±0, subnormals,
  ±448, NaN bytes, ±inf, overflow, underflow).
- **Tests:**
  - my jdiff of main 3040ac1f against #106, over `tests/program`, `tests/query`, the lints, `test_no_by_name_rules` and
    `test_imports_resolve`: 1,377 tests, 8 new, all pass, 0 changed, 0 new failures or skips;
  - the lane's CPU pod gate (b): jdiff rc 0, 8 new tests pass.

## One point for root (not blocking)

The committed products come from a host-side float32 multiply of the committed `x_s` and the checkpoint's block scales, with the IR's
`F32Mul_v1` semantics. The CUTLASS kernel forms the same product in a register, as one IEEE FMUL (no fast-math), and never stores it. So
the values agree on every non-NaN pair.
- On a NaN pair, the committed word keeps numpy's payload, where the GPU register would be `0x7FFFFFFF`. The bf16 output is `0x7FFF`
  either way.
- This is the same class as the router's NaN word (#96). There, root kept an explicit `0x7FFFFFFF` mapping because the word was the
  kernel's stored word. Here the kernel never stores the product, so no hardware word exists to match.
- A mapping would cost about 2 gates per product, which is about 1.8 G gates on #74. My recommendation is to leave it. If root wants the
  mapping anyway, it's a follow-up before the re-baseline switch.
- **Root decided (04:53Z): leave it out.** The PR body will say that host-computed committed values follow the IR's semantics, NaN
  payloads included, and that the GPU register is never observable. If a later tap stores this product from the kernel, the
  `0x7FFFFFFF` mapping becomes required. The lane is adding this to the description; the code is unchanged, so the approval stands.
