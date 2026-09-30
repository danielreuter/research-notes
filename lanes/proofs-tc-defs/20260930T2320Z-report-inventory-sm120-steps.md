---
id: 20260930T2320Z-report-inventory-sm120-steps
campaign: verity
lane: proofs-tc-defs
kind: report
status: open
repo: danielreuter/verity
origin: proofs-tc-defs (bc-de7192ba), worker of @proofs (bc-8416bc72)
---

CHECKPOINT a3e35aa7f (23:16Z) [open] 4:22 PM PDT inventory posted (note:20260930T2320Z-report-inventory-sm120-steps): sm_120 FP8 E4M3 pinned on PRO 6000 in #502, E5M2 measured but hypothesis; missing core E5M2 and MXFP4 steps and all FP8/FP4 GemmCoordinates. Next: E5M2 total step, MXFP4 edge probe on node 1 provers queue.
# proofs-tc-defs: inventory of sm_120 tensor-core steps, probes and Definitions (4:20 PM PDT, Sep 30)

Base: `origin/main` `ce30e9b65`. Branch `cursor/proofs-tc-defs-95d4` merges the open #523 (on #515, #487) and #502.

## Registry (`verity.ml.tc.instructions`) and trust

| id | on main | open PRs | anchor / evidence |
|---|---|---|---|
| `sm120.mma.m16n8k16.bf16` | pinned | | RTX 5090, `art:b87e5a5b…` |
| `sm120.mma.m16n8k64.e2m1.nvf4` | pinned | | RTX 5090, `art:3e02931d…` (fp4-re) |
| `sm120.mma.m16n8k64.e2m1.mxf4` | pinned | | RTX 5090, `art:d8d4d1b6…` (fp4-re) |
| `sm120.mma.m16n8k32.e4m3` | absent | #502: **pinned** | PRO 6000 target, dossier `art:b3074aba…`, run `r20260930-063457-5410`: 25,041,024 elements, 0 mismatches |
| `sm120.mma.m16n8k32.e5m2` | absent | #502: **hypothesis** | run `r20260930-063527-4d6b`: 25,041,024, 0 mismatches; P1 fails only because no Target anchors e5m2 on the PRO 6000, so trust falls back to the RTX 5090 |

The FP8 step (#487, lane vllm-sm120-tc-gemm): `GroupSum` one group of 32, 26-bit truncating adder, floor −133, the
accumulator not truncated; one `QMMA.16832` in SASS. Ada's (16,16)/14 misses 19,033,876 of the 25M, the sm_90 double
HMMA 3,049,017. **Hawkeye-style RE of sm_120 FP8 is therefore done bit for bit for finite inputs**; what's open is E5M2's
pin (a PRO 6000 anchor) and total (NaN/inf) semantics of the E5M2 step, which no probe has asserted (`specials` is
unasserted in `tc_probe` unless the model is total, and `tc_probe`'s total path is BF16-only).

## Probes

- `tools/tc_probe`: sm_120 bf16 on main; #487/#502 add `sm120.mma.m16n8k32.{e4m3,e5m2}` (`mma_*_m16n8k32_tiles`, `sm_120a`).
- `tools/tc_probe_fp4`: NVFP4/MXFP4 k64 families; `specials` is record-only; UE8M0 draws stop at 254, so the NaN scale
  0xFF has never run. #525 (open) adds PRO 6000 K=32 E2M1 rows (`BLACKWELL_SM120_E2M1_M16N8K32`, model only), #492 (open)
  mxf8f6f4 / mixed-FP8 capture rows, not yet run.
- `backends/numerical` Hawkeye: the Ampere BF16 simulator port only (`reference/hawkeye_close.py`,
  `fixtures/hawkeye/PIN.json`); nothing for sm_120, FP8 or FP4.

## Other lanes' sm_120 results

- fp4-re / fp4-proof (RTX 5090): NVFP4 and MXFP4 pinned for arbitrary accumulators; tcgen05 showed B200 computes the same words.
- vllm-sm120-tc-gemm on the PRO 6000: the FP8 fit above; NVFP4 total rules from job 119 (`r20260930-093614-53fd`): scale
  low 7 bits 0x7F → NaN (over ±inf too), NaN acc → NaN, ±inf → itself, bit 7 ignored; NVFP4/MXFP4 PRO 6000 pins in pouw
  runs `r20260930-064142-07f5`, `-064149-a24f`.
- MXFP4 edges measured on the 5090 only: NaN acc → NaN, ±inf → itself, sums leaving binary32 → ±inf. Unmeasured: the
  0xFF scale, and an infinite accumulator meeting an overflow of the opposite sign.

## Core IR (what a hillclimb subcircuit can bind)

- Step prims: `BlackwellE4m3QmmaDot32_v1` (#515), `BlackwellNvf4OmmaDot64_v1` (#523, total). **Missing:** the E5M2 and
  MXFP4 steps.
- Composites: only BF16's `DotBf16_v2` / `GemmCoordinate_v2` / `Gemm_v2`. vLLM has its own (#566 `DotNvfp4_v1`,
  `ScaledMmNvfp4Coordinate_v1`; #582 `ScaledMmFp8Block_v2`; #565 `ScaledMmFp8NoSwap_v1`), none in core.

## Plan

1. E5M2 step prim, total, checked against the PRO 6000 specials capture of `r20260930-063527-4d6b`; pin E5M2 on the PRO 6000.
2. MXFP4 step prim, total, after a PRO 6000 probe of the 0xFF scale and the overflow edges.
3. Core `Dot*` / `GemmCoordinate*{K, DOT}` for FP8, NVFP4 and MXFP4, with circuit-check.
