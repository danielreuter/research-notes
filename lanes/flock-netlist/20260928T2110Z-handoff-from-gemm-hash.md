---
cursor:
  subagentId: "bc-abeef3db-47ab-5256-b71c-c818c5cd1575"
id: 20260928T2110Z-handoff-from-gemm-hash
campaign: gemm-hash
lane: flock-netlist
kind: handoff
status: open
repo: verity
origin: gemm-hash (bc-abeef3db)
---

# gemm-hash: your 20:42Z asks are met on #328 at f639cd66 — straight-line u64 stream in row order, rows mapped by kind from the laid-out circuit, pins that fail on a row-order change

This answers `lanes/gemm-hash/20260928T2042Z-handoff-from-flock-netlist-native-sha512-split.md`, and replaces the interface notes of my 21:00Z handoff. The reference is on [#328](https://github.com/danielreuter/verity/pull/328), based on #289 at `788bf662`, in `backends/flock/live` (no `gpu`).

- **Straight-line u64 code, rows emitted in the pinned row order.**
  - `NativeSha::slot_zab(ins)` runs `tape()`, a slot's SHA-512 in `u64` words in `compress_gadget`'s order, into a `Stream` sink with a 4-word ring.
  - Each row is written in row order as soon as the words it reads exist. Every row reads within 2 words of the newest (`window()`), and a ring miss asserts.
  - That's one thread's program per slot.
- **Row index → what it computes, derived from the laid-out circuit.**
  - Every tape word carries a `Role`: its compression, part, addition, and what it is (`x ^ c`, `y ^ c`, `c`, the sum, `Ch`'s or `Maj`'s operand, or a port word).
  - Each row's `(a, b)` sources come from matching the pinned circuit's rows in order against the tape's candidate rows, by kind (a commit's B form is the constant column) and by values on 256 `eval64` lanes. No hand indices.
  - `kind(r)` and `describe(r)` name each row, for example "committed carry: compression 0, Round(25), addition 2, bit 4".
  - `census()`: `sha512x3`'s counts equal the builder's (per compression, 47,707 carry rows, 5,120 `Ch`, 5,120 `Maj`, 9,119 committed carries, 14,336 committed words), and no row is left without a kind.
  - Matching by kind came from a test catching a folded carry row taking a commit's place, value-identical but mislabelled.
- **A test that fails if the row order changes.** The slot circuits' text SHA-256 (`sha512x3` `9649f9b7…`, `hm96` `4eb22192…`) and their plans' SHA-256 are pinned in `native_witness_matches_eval64_on_the_pinned_slot_circuits`. The selftest case reports each staged circuit's SHA-256, and both staged statements' match the pins.
- **Tests: random inputs, and the real `Stmt::row_inputs`, against `eval64` on both slot types.**
  - Lib tests: fresh random lanes, all-zero and all-one inputs, and the stream lane by lane against `eval64` + `lanes`. The carries-every-16 variants pass too.
  - Selftest case `native_sha_matches_eval64`: every compression and hm96 slot of the statement, from `Stmt::row_inputs`, against `Stmt::slot_zab`, padding instances included. It passes on staged RoPE (8 instances) and on a K = 256 GEMM coordinate (4 instances, 4-compression chains). `honest` and `host_units_match_witness` still pass, and so does `check_build.sh`.
- **For the kernel:** upload `rows` (two `u32` per row) and `need` (one `u32` per row: one past the newest word the row reads). The plan derives and checks in about 0.6 s per slot circuit at statement load.
- **Order is as you wrote:** the host bucket first, then the kernel against this. If you want the plan precomputed into META, or as run-length segments per addition, tell me in `lanes/gemm-hash/` and I'll add it on #328.
