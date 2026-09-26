---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T05:45Z
---

# bench-spine: FP8 spine sets merge-ready as PR #57; flock-backend's four FP8 cells need re-running on them

**Merge:** PR [#57](https://github.com/danielreuter/verity/pull/57), branch `cursor/bench-spine-fp8-5777` at `7aead8e5`, based on
main 3f81173b. CPU only, with no pods and no spend.

## What

- **Core, `verity.ml.kernels`:** `ADA_E4M3_STEP` and `ADA_E4M3_DOT{K}`, sm_89's E4M3 step, as finite-domain scalar references over
  `models.ADA_E4M3_M16N8K32`.
  - Their numpy kernels decline the non-finite domain, and the self-check shows the kernel declining exactly what the
    reference rejects.
  - `test_evaluation` also lists `HopperE4m3QgmmaDot32`, whose absence made main's
    `test_every_registered_kernel_is_self_checked_here` fail.
- **Spine:** `gemm-coordinate` can now generate `sm89.mma.m16n8k32.e4m3` and `sm90.wgmma.m64n8k32.e4m3`.
  - `x` and `w` are E4M3 `u8` bytes, uniform over the finite codes; `y` is the FP32 accumulator word (`u32`), with no epilogue.
  - The new `generate --suite fp8` makes the sets below.
- **Tests:** core evaluation, ml and boundaries, plus the bench directory: 603 passed, 6 skipped.

## The sets (`input-set/v1`, preserved, seed 20260926)

- **fp8-ada K2048:** art:c063de3a (6,272) and art:c0999789 (16,384).
- **fp8-ada K8192:** art:cdb0e90d (1,920) and art:6ffda100 (8,192).
- **fp8-hopper K2048:** art:5f311851 (6,272) and art:31d0727a (16,384).
- **fp8-hopper K8192:** art:d5578eff (1,920) and art:9d85bd96 (8,192).

Every instance re-evaluates through the IR. Each smaller set is the larger one's prefix, and every `y` equals the backends'
`verity.ml.tc` chain. The sizes are the captured #101 sizes plus the 4090's largest sweep batches; that choice is my reading of
"memory-limited". Evidence: `lanes/bench-spine/evidence/20260926T0540Z-fp8-sets.json`.

## Decisions and follow-ups

- **Flock's `write_synth` files can't be re-expressed as spine sets.** They come from a numpy PCG64 stream rather than the spec's
  SHA-256 counter streams, their distribution differs (0x77/0xF7 are doubled), and no rows coincide, so no instance-equivalence
  argument exists.
  - The four cells `art:43986c5d`, `art:c0999f7f`, `art:c200eef3` and `art:c4d03dd5` need re-running on the sets above.
  - flock-backend is told (`lanes/flock-backend/20260926T0545Z-handoff-from-bench-spine.md`). Their `write_set` must first
    accept 8-bit sets, and their `templates/gemm_coordinate.py` must admit K = 2048 / 8192.
- **bligero-real-k has the art ids** (`lanes/bligero-real-k/20260926T0545Z-handoff-from-bench-spine.md`). Their
  `relchain.set_instances` refuses FP8 sets as written, because it compares `pack_public(acc)` with the FP32 word. The one-line
  fix is in that note.
