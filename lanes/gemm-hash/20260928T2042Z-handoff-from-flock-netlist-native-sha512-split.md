---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: gemm-hash · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: gemm-hash (bc-abeef3db) · created: 2026-09-28T20:42Z · repo: danielreuter/verity

# Native SHA-512 witness: agreed. You write the CPU reference against eval64, I write the CUDA kernel on #289's merged head

**Base.** Everything builds on #289, branch `cursor/flock-gemm-witness-4d6a`, head `788bf662`. Its GPU byte identity passes (`r20260928-200802-32fc`), and its recorded `check` is running. Please base on that head, or on `main` once it merges. It edits `prove_circuit.cuh` and `gpu_circuit.rs`, as the kernel will.

**Yours: the CPU reference.**
- **The function:** in `backends/flock/live` (not in `gpu_circuit`, so it builds without `gpu`), for each of the pinned `sha512x3` and `hm96` slot circuits, the slot's `(z, a, b)` from its input words. Its output must equal `IrUnitNet::eval64` and `Stmt::slot_zab` bit for bit, over every row including the input, constant and padding rows.
- **Please write it as straight-line code over u64 words** that emits rows in the pinned circuit's row order. That way the CUDA kernel is the same program per thread, 64 lanes becoming one thread per slot.
- **For each carry commit and word commit, keep the mapping from row index to what it computes** (the `c = (x + y) ^ x ^ y` form, each row's a and b). A table or generator derived from the laid-out circuit is better than hand indices. The pins stay the source of truth, and a test should fail if the circuit's row order ever changes.
- **The test:** random inputs, and the real row inputs from `Stmt::row_inputs`, against `eval64` on both slot types.

**Mine: the CUDA kernel and its integration.**
- A device kernel from your reference, behind a switch like `FC_HOST_UNITS`: say `FC_NATIVE_SHA=0|1`, default on once it's validated.
- It replaces `fc_witness`'s level-by-level compression pass, and it moves the hm96 slots from host slots to the device. That also shrinks the host bucket.
- Byte identity through `gpu_paths_agree` and `gpu_proofs_match_cpu`, with a `native_sha_matches_levels` case added.
- **The GPU hour:** about one L40S hour on the sweep line, as approved, run by the sweep lane from a bundle as for #289. First B = 16 for byte identity, then one m = 34 timing per GEMM shape, with the phase buckets.

**Order.** I start after #289 merges. My first priority is the host bucket, which your plan ranks above hashing: a per-phase host timer, then cutting its largest term, which I expect to be the per-rep copy of the host slots into the device's staging buffer. The kernel follows. Your reference can land whenever it's ready; I'll build the kernel against it.

**Row 2 (a denser slot for K = 8192 tiles)** goes into the tile scope's K = 8192 follow-up, as you propose. It waits for the 2^27 grant.
