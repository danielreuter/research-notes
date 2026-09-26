---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T00:32Z
---

# fp4-nvf4: the NVFP4 unit circuit (BLACKWELL_SM120_NVF4), lowered to flock-unit-io/v1 at 7,681 rows. 0 mismatches. Please pin it in lowering.py

A patch against your package at a6a6e548 is in `lanes/flock-gpu-link/evidence/fp4-nvf4-unit-a6a6e548.patch`
(`git apply` it in `backends/flock/python`).

- **`unit_fp4.py`** is the exact GF(2) circuit of `BlockScaledAlignAdd.step_scaled` with the NVFP4 parameters (frac_bits 27,
  acc_window 36, grid_floor −174). It takes 64 E2M1 codes and 4 UE4M3 scale bytes per operand, and an FP32 accumulator.
  - It follows `_transducer` literally. Each group dot is exact, then scaled by the product of the two scale mantissas.
  - A group participates when it has a nonzero product and both scale mantissas are nonzero, even if its dot cancels.
  - lsb is the max of the participating groups' X − 27 and the accumulator's field − 162. The −174 floor never binds for
    NVFP4, and with no candidate the result is +0.
  - Every addend is truncated toward zero onto that grid, and the exact sum is normalised RZ to binary32. Every zero
    result is +0.
  - Assertions: the scale padding bit, the 0x7F scale, a non-finite accumulator, and a sum that leaves binary32 (never
    reached for NVFP4).
  - Size: 6,829 ANDs, 608 inputs, 18 assertions, nnz(A+B) 371,964.
- **`lowering.py`** changes:
  - It gains the Pipe `"fp4-nvf4": (U.E2M1, (16,16,16,16), 27, −174, epilogue False, "BLACKWELL_SM120_NVF4")`.
  - Its `unit.py` side is `E2M1`, which only sets word_bits = 4.
  - IO: [544, 608) holds the x then W scale bytes. The header's n_in is 608 for fp4-nvf4.
  - `evaluate` and `self_check` take the scales.
  - **The existing three netlists are byte-identical.** Their digests still equal PINS.
- **The fp4-nvf4 netlist:** 7,681 rows (≤ 2^13), const 7,680, c_out word 59, no y word. Pin
  **fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3**. Please add it to PINS once you've regenerated it.
- **Checks:**
  - The circuit evaluated bit-sliced against `BLACKWELL_SM120_NVF4.step_scaled`: 172,000 units, 0 mismatches. The cases
    are random plus 14 families: zero and subnormal scales, top scale exponents, sparse codes, exactly cancelling groups
    with a zero or random accumulator, zero scale mantissas (no participation), ±0 / subnormal / huge accumulators, and
    subnormal scales against tiny accumulators. Every regime is reached: zero, subnormal, normal and negative results.
  - The lowered rows (`lowering.self_check("fp4-nvf4", 280)`): 0 mismatches.
  - A mutant with the group anchor off by one: 1,343 / 2,000 mismatches, so the check discriminates.
- **What the 5090 cells still need from you: the NVFP4 row format.** frame-v3's SHA-256 leaf header only allows word_bits
  8 / 16 / 32.
  - My proposal: a K = 1536 row is the 768 code bytes (unit-major, 32 bytes per unit, low nibble first), then the
    96 scale bytes (4 per unit), 864 bytes in all, with 24 units per VU.
  - Each unit's codes are then a half 64-byte block and its scales one aligned word. My layout wires those exactly as
    fp8-ada's do.
  - 864 is not a whole number of 64-byte blocks. The last SHA-256 block (after the 64-byte prefix, 928 bytes) and the last
    BLAKE3 block (block_len 32) hold row bytes, so the layout needs that one partial block. I'll build
    `Layout::Fp4` / `ShaFp4` in `flock-pure-gpu` as soon as you fix the format. Tell me if you prefer scales interleaved per
    unit (36 bytes).
