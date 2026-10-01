---
id: 20260930T2320Z-report-inventory-sm120-steps
campaign: verity
lane: proofs-tc-defs
kind: report
status: open
repo: danielreuter/verity
origin: proofs-tc-defs (bc-de7192ba), worker of @proofs (bc-8416bc72)
---

CHECKPOINT 3aca29a5b (23:51Z) [open] E5M2 step prim BlackwellE5m2QmmaDot32_v1 in (f8c22821f, circuit-check ok, dossier PINNED); MXFP4 edge probe submitted as node-1 sky job 346 (provers); next: FP8/FP4 GemmCoordinate composites
CHECKPOINT a3e35aa7f (23:16Z) [open] 4:22 PM PDT inventory posted (note:20260930T2320Z-report-inventory-sm120-steps): sm_120 FP8 E4M3 pinned on PRO 6000 in #502, E5M2 measured but hypothesis; missing core E5M2 and MXFP4 steps and all FP8/FP4 GemmCoordinates. Next: E5M2 total step, MXFP4 edge probe on node 1 provers queue.
# proofs-tc-defs: inventory of sm_120 tensor-core steps, probes and Definitions (4:20 PM PDT, Sep 30; results 5:15 PM PDT)

Base: `origin/main` `ce30e9b65`. Branch `cursor/proofs-tc-defs-95d4` merges the open #523 (on #515, #487) and #502.

## Results (5:15 PM PDT)

The GemmCoordinate Definitions and the MXFP4 step moved to lane proofs-gemm-defs at 4:41 PM PDT
(note:20260930T2341Z-handoff-from-proofs-defs-moved). This lane wrote one Definition, `BlackwellE5m2QmmaDot32_v1`, and
no composites.

- **E5M2: pinned on the PRO 6000.** The dossier is `art:fc4bb891…`, anchored on two dies (r20260930-063527-4d6b,
  r20260930-073650-c9c5). The step `BlackwellE5m2QmmaDot32_v1` (`f8c22821f`) is total. It replays the PRO 6000's specials
  and signed-zero tiles (38,912 words). circuit-check: 64 vectors, 20 edge vectors, numpy kernel 0 mismatches, 0 failures,
  0 warnings; no C-Flock piece.
- **MXFP4 total semantics: measured on the PRO 6000.** The run is r20261001-000520-2440 (5:05 PM PDT, vy-nebius-1,
  GPU-a98a36f6, one `OMMA.SF.16864.F32.E2M1.E2M1.E8` per tile kernel). It has 1,179,648 words, and the 1,089,536 in gated
  families show 0 mismatches against `BLACKWELL_SM120_MXF4`. Lane proofs-gemm-defs' `BlackwellMxf4OmmaDot64_v1`
  (`0f05a4dd6`) reproduces every word, the 90,112 record-only ones included, through both its kernel and its scalar
  prim. Those include the never-run 0xFF scale (9,216 words, all 0x7FFFFFFF, 3,770 of them over a ±inf or NaN
  accumulator), and a ±inf accumulator against an opposite-sign overflowing sum (734 words: the accumulator, never NaN).
  The fixture is `72408f917` and the instruction evidence `d07134047`; the handoff to lane proofs-gemm-defs is
  note:20261001T0014Z-handoff-from-proofs-tc-defs-mxf4-measured.
- **The one unmeasured E5M2 rule:** opposite-sign infinite products in one group. The NaN result is inherited from the
  E4M3 total step, not measured.
- **A `tools/research` fix**, branch `cursor/research-timefmt-tzdata-ec6a`, `42ea2831b`, needs a PR of its own.
  `research.timefmt` (on main since `0a0a7aa45`, 1:48 PM PDT) raised `ZoneInfoNotFoundError` at import in the Nebius job
  images, which have no tz database. So every prover-dev job on a newer tree died before its command ran (sky job 346).
  The fix prints UTC alone when no tz database is found; a subprocess test covers it. Job 347 ran with it.

## C-Flock prover support (out of scope; what it would take)

| step | C-Flock piece | per step | per BF16-out coordinate at K = 2,048 / 4,096 / 8,192 / 16,384 |
|---|---|---|---|
| E4M3 `BlackwellE4m3QmmaDot32_v1` | pinned | 9,793 AND (665 redundant) | (K/32) × 9,793 + 77 (`F2fpBf16_v1`) = 626,829 / 1,253,581 / 2,507,085 / 5,014,093 AND |
| E5M2 `BlackwellE5m2QmmaDot32_v1` | none | not built | K/32 steps |
| NVFP4 `BlackwellNvf4OmmaDot64_v1`, MXFP4 `BlackwellMxf4OmmaDot64_v1` | none | not built | K/64 steps = 32 / 64 / 128 / 256 |

- **E5M2** has the same `GroupSum` pipeline as E4M3 (groups of 32, width 26, floor −133). Its products have 3-bit
  significands where E4M3's have 4, and its exponent field is 5 bits where E4M3's is 4, so the alignment range is wider.
  Expect a per-step count of the same order as E4M3's: a piece adapted from the E4M3 one, plus the inf/NaN classification
  in `tc_dot_total_e5m2`.
- **NVFP4 and MXFP4** need a new `BlockScaledAlignAdd` piece:
  - 64 E2M1 × E2M1 products, each a lookup in a 16 × 16 table;
  - per-block scale adds (4 UE4M3 or 2 UE8M0 per operand);
  - the align-add on the 2^−27 grid with a 36-bit accumulator window, floor 2^−174, truncation;
  - the total rules above.
- **No AND count until the pieces are built.** `verity.ml.tc.relation.census()` covers only the BF16 pipelines.

## Registry (`verity.ml.tc.instructions`) and trust

| id | on main | open PRs | anchor / evidence |
|---|---|---|---|
| `sm120.mma.m16n8k16.bf16` | pinned | | RTX 5090, `art:b87e5a5b…` |
| `sm120.mma.m16n8k64.e2m1.nvf4` | pinned | | RTX 5090, `art:3e02931d…` (fp4-re) |
| `sm120.mma.m16n8k64.e2m1.mxf4` | pinned | | RTX 5090, `art:d8d4d1b6…` (fp4-re); this branch adds the PRO 6000 sweep r20261001-000520-2440 |
| `sm120.mma.m16n8k32.e4m3` | absent | #502: **pinned** | PRO 6000 target, dossier `art:b3074aba…`, run `r20260930-063457-5410`: 25,041,024 elements, 0 mismatches |
| `sm120.mma.m16n8k32.e5m2` | absent | #502, then this branch: **pinned** | PRO 6000 anchor, dossier `art:fc4bb891…`: runs `r20260930-063527-4d6b` (25,041,024) and `r20260930-073650-c9c5` (6,440,960), 0 mismatches |

The FP8 step (#487, lane vllm-sm120-tc-gemm): `GroupSum` one group of 32, 26-bit truncating adder, floor −133, the
accumulator not truncated; one `QMMA.16832` in SASS. Ada's (16,16)/14 misses 19,033,876 of the 25M, the sm_90 double
HMMA 3,049,017. **Hawkeye-style RE of sm_120 FP8 is therefore done bit for bit for finite inputs**, and with the E5M2
specials replay above, for NaN and inf as well, except opposite-sign infinite products in one group.

## Probes

- `tools/tc_probe`: sm_120 bf16 on main; #487/#502 add `sm120.mma.m16n8k32.{e4m3,e5m2}` (`mma_*_m16n8k32_tiles`, `sm_120a`).
- `tools/tc_probe_fp4`: NVFP4/MXFP4 k64 families; `specials` is record-only. This branch adds four record-only MXFP4 edge
  families (`families_mxf4_edges`: the 0xFF scale, overflowing blocks that cancel, the binary32 overflow edge, inf/NaN
  accumulators against overflow) and `--library` for a library built on another host. #525 (open) adds PRO 6000 K=32
  E2M1 rows (`BLACKWELL_SM120_E2M1_M16N8K32`, model only); #492 (open) mxf8f6f4 / mixed-FP8 capture rows, not yet run.
- `backends/numerical` Hawkeye: the Ampere BF16 simulator port only (`reference/hawkeye_close.py`,
  `fixtures/hawkeye/PIN.json`); nothing for sm_120, FP8 or FP4.

## Other lanes' sm_120 results

- fp4-re / fp4-proof (RTX 5090): NVFP4 and MXFP4 pinned for arbitrary accumulators; tcgen05 showed B200 computes the same words.
- vllm-sm120-tc-gemm on the PRO 6000: the FP8 fit above; NVFP4 total rules from job 119 (`r20260930-093614-53fd`): scale
  low 7 bits 0x7F → NaN (over ±inf too), NaN acc → NaN, ±inf → itself, bit 7 ignored; NVFP4/MXFP4 PRO 6000 pins in pouw
  runs `r20260930-064142-07f5`, `-064149-a24f`.

## Core IR (what a hillclimb subcircuit can bind)

- Step prims: `BlackwellE4m3QmmaDot32_v1` (#515), `BlackwellNvf4OmmaDot64_v1` (#523, total), `BlackwellE5m2QmmaDot32_v1`
  (this branch), `BlackwellMxf4OmmaDot64_v1` (proofs-gemm-defs).
- Composites (proofs-gemm-defs `21e333a9b`): `GemmCoordinateE4m3_v1`, `GemmCoordinateNvf4_v1`, `GemmCoordinateMxf4_v1`
  `{K, DOT}`. E5M2 type-checks as `GemmCoordinateE4m3_v1`'s `DOT`, but that composite's kernel maps only E4M3 steps.
