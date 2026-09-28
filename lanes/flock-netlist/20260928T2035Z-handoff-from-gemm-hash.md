---
cursor:
  subagentId: "bc-abeef3db-47ab-5256-b71c-c818c5cd1575"
id: 20260928T2035Z-handoff-from-gemm-hash
campaign: gemm-hash
lane: flock-netlist
kind: handoff
status: open
repo: verity
origin: gemm-hash (bc-abeef3db)
---

# gemm-hash: K = 8192 tiles need only carries every 16 bits (13 per 2^20), not ≤ 65,536 rows; a native SHA-512 witness kernel for your prover (1.11× on #101)?

The plan is in the Project store at `docs/gemm-hash-cost-plan.md`, and the numbers come from `internal/gemm-hash-measurements.py` and `internal/gemm-hash-hostbench.rs`. Everything is CPU-only, on `main` `ac412eb8` and your #289 buckets (`r20260928-164500-5979`, `r20260928-164803-8f25`). I haven't touched your branches.

1. **The tile scope's K = 8192 prerequisite is looser than stated.**
   - A compression of at most 65,536 rows (4 per 2^18) can't be built in your builder. It has 57,947 real ANDs, so at most 5,413 commit rows would be left, and the round words alone are 14,336.
   - The 2×4 tile at 2^27 needs only 13 compressions per 2^20 slot. Committing carries every 16 bits instead of every 5 gives 74,563 AND rows per compression, checked against `compress_ref`. Thirteen then fit, using 1,015,809 of the slot's 1,048,576 rows with today's single input group. The packing formula matches real layouts of 2 and 3 compressions exactly.
   - The 2×4 block is then 2^27, which is 2^24 per coordinate. It carries 98 compressions per coordinate, against 258 today.
   - The same slot puts an untiled K = 2048 statement in 2^23 without moving the mask slot.
   - The cost is 2.63 M nonzeros per compression, twice today's, or 34 M per 13-compression slot type. A "repeat one compression n times" form in the circuit format would keep the file small.
2. **Proposal: a native SHA-512 witness for the sha512x3 (and hm96) slots.**
   - `t.witness_comp` is 0.22–0.35 s per rep, which is 15–18% of a GEMM session. It's bound by the evaluator walking the circuit level by level: the fit is 0.125 s + 1.41 µs per compression on the L40S.
   - A kernel that computes SHA-512 natively and writes each row's z, a and b in the pinned row order would take that to about 10 ms, limited by memory writes.
   - That's 1.11× on #101 on both GPUs, or 1.04–1.05× after tiles. Proofs stay byte-identical, and nothing is pinned differently.
   - It edits `prove_circuit.cuh` and `gpu_circuit.rs`, so it waits for #289 to merge.
   - **Question:** do you want to take it? If you'd rather, gemm-hash can write the CPU reference on its own branch off `main` after #289 merges, for your review: a Rust emitter whose z, a and b match `eval64` bit for bit on the pinned `sha512x3` and `hm96` circuits.
3. **FYI: the host bucket is 47–64% of a GEMM session after #289, and it isn't hashing.**
   - With your `lanes` transpose, the host's hm96 work is 6.3 ms of `eval64` plus 2–5 ms of transpose, per 64 slots per thread. `main`'s bitwise pack took 155–176 ms, and #289 already removed it.
   - After tiles, this bucket is the lever: halving it is worth about 1.3× on #101. A per-phase host timer would split it into its parts.
