---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator, for the next train
created: 2026-09-28T15:54Z
---

# Merge request: PR #289, GEMM options 2 and 3 in the flock-circuit GPU prover (merge after the sweep's GPU byte-identity run)

- **PR:** [#289](https://github.com/danielreuter/verity/pull/289), branch `cursor/flock-gemm-witness-4d6a`, head `851170614ad590eacf03d430fdc0d233eb3acd54`, on `main` 64f94732. The PR is still a draft; I'll mark it ready when the GPU run passes.
- **check:** passed on that head, recorded run `r20260928-145910-af1e`:
  - pytest: 3291 passed, 31 skipped;
  - circuit-check, lean-build, lean-unit-cut and lean-audit: passed;
  - lean-agreement: skipped, no bundle.
- **What changes:** the prover only. Statements, the proof format, digests and pins don't move, so no statement reviewer is needed. Four commits:
  1. **Deep units on the host.** A unit of at least 2048 AND-levels, such as the flattened GEMM coordinate, is evaluated on the host, so the device doesn't walk it level by level. The note's accumulator hints don't fit the circuit: step 2 reads 134 rows of step 1, not the 32-bit word.
  2. **Rep 1 reuses rep 0.** Rep 1 proves from rep 0's device witness and level-0 commitment. It falls back to proving in full when the device lacks room for three more witness-sized buffers plus 4 GiB.
  3. **The sweep's switch.** `SELFTEST_GPU=1` in `70-class-sweep.sh`, a new key parameter of `flock_class_sweep`.
  4. **Kept buckets.** The sweep keeps each session's phase buckets.
- **Condition:** merge after the sweep lane's (bc-ea1c2c4f) run A on its L40S passes the new selftest cases on the GEMM shapes:
  - `gpu_paths_agree`: device units with a rebuilt rep 1, against host units with reuse;
  - `gpu_proofs_match_cpu`.

  Both need byte-identical proofs and transcripts under equal seeds; the request is `20260928T1450Z-handoff-from-flock-netlist-gemm-gpu-validation-289.md`. CPU evidence so far: `host_units_match_witness` (every host unit slot equals the CPU witness's words) passes on a deep tiny-model class, and the GPU build compiles and links for `sm_89`.
- **Also written:** the option 4 + 5a layout scope for the red team, `internal/gemm-column-batch-tiles-layout-scope.md`, with its numbers script `internal/gemm-tile-layout-measurements.py`.
