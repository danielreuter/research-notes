---
id: 20260930T2345Z-report-blocker
campaign: verity
lane: proofs-flock-fp
kind: report
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# No blocker for proving FP8/FP4 GemmCoordinates in C-Flock (4:47 PM PDT); the steps, sized

Nothing is blocked. M0's statement path takes these coordinates as they are. Four pieces of work stand between us and a proof,
plus one dependency on the Definitions lane.

## What I checked
- `class_statement` packs every word of up to 16 bits into one u16 leaf, then hashes each row with SHA-512. A Call parameter is
  a row port (scale arrays included). So an E4M3 byte or an E2M1 nibble stages today, one word per leaf. `circuit.py` only
  refuses non-u16 *ports*, and every port is u16 here. No Rust change is needed.
- The step primitives are already in core on the Definitions lane's base (#502 and #523 merged there, not on `main`):
  `BlackwellE4m3QmmaDot32_v1` (sm_120: one group of 32, 26-bit adder, floor −133, total) and `BlackwellNvf4OmmaDot64_v1`
  (total: a NaN scale gives 0x7FFFFFFF, bit 7 is ignored, a NaN or infinite accumulator passes through). There's no MXF4 step
  primitive on any branch yet. `models.BLACKWELL_SM120_MXF4` exists.
- Piece sizes: the sm_120 E4M3 step is 9,793 ANDs per 32 products, so K=2,048 is about 0.63 M ANDs. BF16 Hopper's is 8,233 per
  16, so its K=2,048 is about 1.05 M. The finite NVFP4 unit is 6,829 ANDs per 64 products, so K=2,048 is about 0.22 M plus the
  total rules.
- Node 1: disk is at 72%, and 7 of its 8 GPUs are idle. The census has `rtx-pro-6000-server/e4m3` (1 PFLOPS dense at FP32
  accumulate, from #502) but no `e2m1` line.

## Steps
1. **sm_120 E4M3 piece:** `fp.tc_dot_e4m3` with (32,), 26, −133, mapped in `PIECES`, plus a check against the reference. About 0.3 h.
2. **NVFP4 total piece:** refactor `unit_fp4` into a piece with the primitive's total rules (stand-ins, then the special
   selects), and check it on random and edge inputs. About 1 h.
3. **MXFP4 piece and pipe:** decode UE8M0 scales (mantissa 8, exponent code − 130, so 8-bit exponents), handle the binding
   −174 floor, and follow the total rules (overflow to ±inf, sums below the subnormal grid to +0). It also needs the new step
   primitive's exact semantics from `proofs-gemm-defs`. About 1.5 h.
4. **Job:** generalize `proofs-bf16-hill`'s `74-gemm-hill.sh` / `gemm_hill.py` over dtype, Definition and peak id. Add
   `rtx-pro-6000-server/e2m1` (2 PFLOPS dense, the same NVIDIA sources as the e4m3 line). About 0.5 h.
5. **Dependency:** the Definitions `GemmCoordinate{E4m3,Nvf4,Mxf4}_v1{K,DOT}` from `proofs-gemm-defs`. `NAMES.md` isn't
   written yet. Until they land, I test the pieces against the step primitives. Sharing the x row across coordinates, as BF16's
   `Gemm_v2` does, needs a Gemm-level batch. If the Definitions lane doesn't add one, I build it as an unregistered program
   module.

Dense packing (two E4M3 bytes or four E2M1 codes per u16 leaf) is a later hillclimb step, not a prerequisite. Until then,
FP4 rows cost as much row hashing as BF16 rows. Every point records `coins: seed-mode`, per
`note:20260930T2343Z-handoff-from-proofs-record-coin-mode`.
