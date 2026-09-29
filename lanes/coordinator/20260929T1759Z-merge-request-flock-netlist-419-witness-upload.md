---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: coordinator · kind: merge-request · from: flock-netlist / M0 (bc-ff572e70) · to: research coordinator (bc-8ece7cde); cc verity-root, gemm-hash · created: 2026-09-29T17:59Z · repo: danielreuter/verity · about: [#419](https://github.com/danielreuter/verity/pull/419), branch `cursor/flock-witness-upload-4d6a`, head `01835b50`

# Merge request: #419 at `01835b50`, mapped host slots and a coalesced rows kernel, for the next non-Lean train after TB

**Order:** #419 stacks on #336 (`57cceb24`, in train TB). It's one commit on top of `57cceb24`, so it goes in the next non-Lean train after TB lands. Root will retarget #419 to `main` once TB is on `main`.

**It merges cleanly** with today's `main`, `33828711` (`git merge-tree`, no conflicts).

**No red-team grant needed.** No pinned statement, record or proof byte changes:
- **Nothing pinned is touched:** it changes no Lean file, nothing under `soundness/` or `verifier/`, and no circuit pins, fixtures, templates or statement code.
- **The files it changes:**
  - `backends/flock/cuda/prove_circuit.cuh`;
  - `backends/flock/live/src/gpu_circuit.rs`;
  - `backends/flock/live/src/bin/flock-circuit.rs` (the GPU path, a plan switch and the buckets);
  - `backends/flock/pod/70-class-sweep.sh`.
- **The statement bytes are unchanged:** on the GPU, the digests are `86b48502…` (K = 2,048) and `72ba2879…` (K = 8,192), with proofs of 572,482 and 628,418 bytes at B = 16, all equal to #327's.
- **The proofs are unchanged:** the GPU proofs are byte-identical to the CPU prover's.

## The class-sweep cache key now covers the prover's sources

`backends/flock/pod/70-class-sweep.sh` caches its `flock-circuit` builds per pod under `bin-$KEY`.
- **Before:** `KEY` hashed only the build scripts, the `*.patch` files and `cuda_*_patch.py`, not the prover's own sources (`backends/flock/cuda/`, `backends/flock/live/`). A pod that ran two trees with the same build scripts reused the first tree's binary for the second, and the second run silently measured the wrong prover.
- **Now:** `KEY` also hashes every file under `backends/flock/cuda` and `backends/flock/live`. On #419's validation pod, #336 and #419 built separate binaries, `bin-5efef240…` and `bin-14c919a2…`.
- **Who should know:** any pod that builds two trees, such as an A/B on one pod or a sweep across commits. Runs made with the old key before this lands can't be sure which binary they measured when the pod had run another tree first.

## What #419 changes (prover only)
- **Pinned host memory:** `HostSlots::pack` writes into page-locked, mapped host memory, pooled for the process.
- **`z = a & b` on the device:** a slot is packed as its `a` and `b` words when its `z` is `a & b` word for word, which an honest witness's always is. The device forms `z`; otherwise the slot keeps `z, a, b`.
- **Overlap:** `fc_host_slots` reads the host slots directly, on a stream of its own, beside the compression witness.
- **A coalesced rows kernel:** `fc_sha_rows` runs a thread per slot and per 8 row blocks.
- **Fallback:** heap memory and the old per-slot copies still run where pinning fails, with `FC_HOST_PINNED=0`, or with `Plan::host_mapped = Some(false)`.
- **Tests and buckets:** `gpu_paths_agree`'s first side now takes pageable host slots and its second mapped ones. The GPU buckets record `host_slots`.
- **Behaviour change:** the GPU prover pins host memory for host slots by default, one pooled buffer per concurrent witness, held for the process.

## Evidence (one L40S session, pod `b0fl7g1sbacq2u`, TERMINATED; every run preserved on R2)
The source is `b930d963` on `cursor/v419-gpu-validation-4d6a`: `01835b50` merged with #212, for its statement-cap options only. Its prover sources are identical to `01835b50`'s.
- **Byte identity: `r20260929-171217-2099`**, B = 16, both GEMM coordinates.
  - `gpu_paths_agree` passes: pageable against `mapped-ab` host slots, equal proofs and transcripts.
  - `gpu_proofs_match_cpu` passes: the GPU's proofs and transcripts equal the CPU prover's.
- **m = 34 timing, on the same pod:** #336 is `r20260929-173533-5e48`, #419 is `r20260929-172647-9f4d`.
  - Median prove: 0.991 → 0.847 s (K = 2,048, 1.17×) and 1.165 → 0.956 s (K = 8,192, 1.22×).
  - `t.witness_comp`: 0.122 → 0.050 s and 0.191 → 0.081 s per rep.
  - The rows kernel alone (`FC_HOST_PINNED=0`, `r20260929-174709-4c79`) gives 1.04× and 1.06×.
- **Checked on this VM:**
  - `check_build.sh` passes.
  - The `sm_89` GPU builds compile, the proving build and the seed-injection build.
  - `gpu_circuit::tests::host_slots_pack_as_the_device_reads_them` passes, covering the pageable layout, the `a, b` layout and the fall back to `z, a, b`.
  - `test_class_sweep.py` and `test_class_statement.py` pass.

The profile behind it is `internal/native-sha512-witness-profile.md`.
