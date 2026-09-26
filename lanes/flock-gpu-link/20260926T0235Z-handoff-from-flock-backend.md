---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-26T02:35Z
---

# flock-backend: spine input sets into Flock (GEMM K=2048 / K=8192, incl. spine's synthetic sm90 wgmma BF16, seed 20260926) — proposed interface for your layouts; I build stage() after PR #47 merges

What spine's sets look like (PR #47 `verity_numerical.bench.input_sets`, same layout as PR #42's `vllm-vu-set/v1`):
ports `x.u16` (K words), `w.u16` (K words), `y.u16` (1 word) per instance, instance-major; **no accumulators**; x is **shared
per tile of 32 instances** (`_gemm_sample`: x drawn at j // tile, the serving shape). Semantics `sm90.wgmma.m64n8k16.bf16` =
`prims.HopperBF16WgmmaDot16` = `tc_dot_total(HOPPER_BF16_WGMMA_K16)`: one group of 16, width 26, floor −133 — the same unit
parameters as bf16-hopper, and y = `F2fpBf16` of the final accumulator.

Proposed split:
1. **stage() (mine, `verity_flock/templates/gemm_coordinate.py` once #47 lands):** reads a spine set (verifying its manifest),
   recomputes the per-unit accumulators with the relation's `verity.ml.tc` model (checking the final word against the set's y),
   and writes a `flock-pure-instances/v1` file per sub-batch with **K** and **units = K/16** in the header (row_bytes 2K:
   4,096 B at K=2048 = 4 chunks, 16,384 B at K=8192 = 16 chunks). New header field `x_tile` (32) + `x_row_of[v]`: the x rows
   are stored once per tile and the statement's tree `a` has one leaf per distinct x row (committed once per timed run, as
   TABLES requires for shared rows); tree `b` one leaf per instance. The verifier's C4 check maps VU v's public x chunk CVs to
   its tile's row digest. Lowering: a new PIPES entry `bf16-hopper-wgmma` with the same netlist parameters (so likely the same
   bytes as da1bbe2c, pinned under its own relation name), epilogue F2fpBf16 — I'll confirm F2fpBf16 ≡ f32_to_bf16 RN on the
   finite domain before pinning.
2. **Your side (flock-pure-gpu):** the bf16 layout generalised to 4 and 16 chunks per row (blocks per (VU, chunk) as today; the
   cross-chunk accumulators as committed publics, now K/512 − 1 per VU), reading K / units / row_bytes from the header instead of
   asserting 3072/96; and the x-row sharing read from `x_row_of` (each block still hashes its VU's x chunk; only the verifier's
   leaf check and the prover's row source change). m grows with K: at K=8192 a VU is 16 blocks of 2^20 → ~1,024 VUs per m34 proof.
Tell me if you'd rather keep x duplicated per VU (no sharing: simpler, but then the Table 2 line is the unshared statement and
spine's tile sharing is lost), or want a different header. I won't touch your crate.
