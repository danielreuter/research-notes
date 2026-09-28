---
cursor:
  subagentId: "bc-abeef3db-47ab-5256-b71c-c818c5cd1575"
id: 20260928T2100Z-handoff-from-gemm-hash
campaign: gemm-hash
lane: flock-netlist
kind: handoff
status: open
repo: verity
origin: gemm-hash (bc-abeef3db)
---

# gemm-hash: the native SHA-512 witness's CPU reference matches eval64 (#328, stacked on #289); the CUDA kernel, the GPU hour and the host bucket are yours

This follows up `20260928T2035Z-handoff-from-gemm-hash.md`, per the coordinator's split:
- **gemm-hash:** the CPU reference, done.
- **You:** the CUDA kernel, the GPU byte-identity hour, and the host bucket.

I haven't touched `prove_circuit.cuh`, `gpu_circuit.rs` or your branches.

- **[#328](https://github.com/danielreuter/verity/pull/328)**, draft, branch `cursor/native-sha512-witness-1575`, based on #289 at `788bf662`. Two commits:
  - `backends/flock/live/src/sha512_native.rs`;
  - a selftest case, `native_sha_matches_eval64`;
  - and four `pub(crate)`s in your `circuit.rs`: `SHA512_IV`, `SHA512_K`, `transpose64` and `lanes`.

  No prover path changes.
- **How it works:**
  - `tape()` computes a slot's SHA-512 in 64-bit words, in `compress_gadget`'s creation order. For each addition it records `x ^ c`, `y ^ c`, the carries `c` and the sum; it also records `Ch`'s and `Maj`'s operands, and the port bits (hm96's `b || c` via `hm96::mask`).
  - `NativeSha::derive(net)` finds, for each row, which tape bit its `a` and its `b` are (`z = a & b`). It matches the pinned slot circuit's rows in order against the tape's candidate rows on 256 random lanes, so constant folding and the carry-commit spacing are read off the circuit.
  - `NativeSha::check` compares it with `eval64` on fresh random, all-zero and all-one lanes.
- **Results:**
  - The plan matches `eval64` on the pinned `sha512x3` (256,001 rows) and `hm96` (246,785 rows) circuits, and on the carries-every-16 variants.
  - `native_sha_matches_eval64` passes on a staged RoPE statement and on a K = 256 GEMM coordinate (4-compression chains), padding instances included. `honest` and `host_units_match_witness` still pass there.
  - `check_build.sh` passes.
- **For the kernel:**
  - `NativeSha::rows` is two `u32` per row: `0` is zero, `1` is one, and `2 + 64 w + i` is bit `i` of tape word `w`.
  - `window()` is 2 words on both circuits. A thread can compute its slot's tape as it writes the rows in order, holding one addition's four words.
  - `NativeSha::slot_zab(ins)` is the per-slot reference output, in `Stmt::slot_zab`'s packing.
  - The plan derives in about 0.15 s per slot circuit, so it can be built at statement load.
- If you want the plan in another form (run-length segments per addition, say, or precomputed into the circuit's META), tell me in `lanes/gemm-hash/` and I'll add it on #328.
