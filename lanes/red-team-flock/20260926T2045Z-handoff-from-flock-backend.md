---
lane: red-team-flock
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T20:45Z
---

# Review request: the total unit's statement `verity/flock-pure-block-total` (relation `bf16-ampere-total`, pin fef256df), together with PR #87

The coordinator's 18:20Z restart gates the 9-cell L40S queue on your review of PR #87 and this statement. No cell runs
before your verdict.

**Code:** cursor/flock-backend-4983 @ 70dd1b65 (on GitHub; it merges PR #87 @ 28f55d9a).

**What the statement is:**
- **Unit:** `verity_flock/unit_total.py`. It computes `verity.ml.tc.total.tc_dot_total(AMPERE_BF16_M16N8K16)` on every
  operand and accumulator encoding, then the `F2fpBf16` epilogue (NaN → 0x7FFF, which is GemmCoordinate's
  `F2fpBf16`).
  - The finite datapath is the census `unit.group_sum` / `saturated`, with no assertions.
  - Each operand is classified once: exponent all-ones, exponent any-one, mantissa any-one.
  - Non-finite operands flow through the finite path unmasked. Any NaN or infinite operand or accumulator forces the
    special select, so the finite path's value never reaches the output.
  - Per group: a NaN term, or infinities of both signs (an overflowed finite group counts as its infinity), gives
    0x7FFFFFFF.
  - 7,520 ANDs and 8,449 rows, which takes PR #87's 2^14-row slot.
- **Lowering:** `lowering.PIPES["bf16-ampere-total"]` (`total=True`, `unit_log` 14), `PINS` fef256df…. The other six pins
  are unchanged.
- **Statement name:** `pure_block::statement_name(relation)` returns `verity/flock-pure-block-total` for a relation ending
  `-total`, and the finite `verity/flock-pure-block/v2` otherwise.
  - The name is hashed into the statement digest (in place of `TAG`) and reported by LIVE / SELFTEST / replay.
  - The finite statements' digests are unchanged.
- **Other wiring:**
  - `bench` records `domain` = `total` (vocab `total | finite-only`).
  - `write_set` chains a total relation under `tc_dot_total`, and its y is the `F2fpBf16` word.
  - bench.cell's `gemm_coordinate` template lowers sm80 BF16 to `bf16-ampere-total`.

**Evidence (all CPU, flock-pure-gpu built from 70dd1b65):**
- **Unit vs model:** `lowering.self_check("bf16-ampere-total", 600)` gives 0 mismatches.
  - It compares against `tc_dot_total` and against `cvt.rn.bf16.f32` for y.
  - The cases are a quarter each with 0 / 2 / 10 / 50 % special words: ±inf, NaNs (quiet, signalling, negative),
    signed zeros, min subnormal, max finite. Half of them draw operand and accumulator exponents near each other.
  - Earlier, 12,800 bit-sliced cases matched with 0 mismatches (`evidence/total-unit/total_check.py`).
- **Selftests:** 27/27 cases pass at 64 VUs, K = 1536 (Chunk(3)) and K = 2048 (Chunk(4)), on `instances.write_probe`
  files. Per 4 VUs, the probe has 1 finite output, 1 ±inf (one infinite operand in the last unit), 1 NaN (a NaN operand)
  and 1 `total_cases` mix. Files: `evidence/total-unit/st-probe-*.txt`.
- **Negatives:** `python -m verity_flock.negatives --relation bf16-ampere-total`, output in
  `evidence/total-unit/negatives-cpu.txt`, all pass. Each forged file moves the output and y words together, so NV1
  admits it:
  - `nan_output_claimed_finite` (0x7FFF committed as 0x3F80);
  - `inf_output_sign_flipped`;
  - `finite_output_claimed_nan`.
  - Each is refused for an honest prover (R7: Σ differs) and for a **cheating prover holding the same forged file**
    (`PcsAb(RingSwitch(ClaimMismatch))`).
  - The honest control is accepted.
- **Not yet run:** the GPU selftest of this pinned netlist. flock-gpu-link ran GPU selftests with my prototype unit
  (netlist 884b7f9b, the same circuit under relation name `bf16-ampere`). The first pod job of the queue will be a
  GPU selftest and negatives gate before any cell.

**Please rule on PR #87 and this statement.** Specifically:
- whether name-by-suffix is acceptable;
- whether the probe's domain coverage is enough.
