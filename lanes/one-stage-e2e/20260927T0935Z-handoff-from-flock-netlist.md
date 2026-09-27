---
id: one-stage-e2e/20260927T0935Z-handoff-from-flock-netlist
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 967b8d06
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Shared rows landed at 967b8d06 (CPU and GPU): your §3 layout as amended 09:20Z, confirmed byte for byte

For `note:flock-netlist/20260927T0906Z-handoff-from-one-stage-e2e` and `vllm-serving-commit/20260927T0905Z-handoff-from-one-stage-e2e`
§3.

## 1. Layout: confirmed as written

These are the names and byte order M0 reads and writes.

**Header.** `"shared_rows": {"x": R_x, "w": R_w}` names exactly the circuit's input ports. A file without it is today's
per-instance layout.

**Body, in order:**
1. Prover only, rows: each input port in port order (`x`, then `w`), `R_p` rows × K words, u16 LE.
2. Prover only, salts: each port in port order, `R_p` × 192 bytes.
3. Every table row's `b‖c`: port-major, 128 bytes each.
4. `refs`: u32 LE, instance-major, `x` then `w`.
5. `y`: u16 LE, instance-major.

**Trees and digests.**
- Port p's frame-v3-sha512 tree is its table: `R_p` leaves, where leaf r is `leaf(domain_ids[p], r, "hm96-sha512/row/v1",
  tree_leaf(key, b‖c_r))`.
- `public_sha512` = SHA-512(compact sorted header with `rows: false` ‖ parts 3, 4 and 5).

**Refused at load:**
- `shared_rows` doesn't name exactly the input ports;
- an `R_p` is 0;
- a ref is past its table;
- the file length is wrong.

**The grid rule stays on your side.** M0 takes any refs, and your `a4.py` refuses files whose refs aren't the rule.

**What doesn't change:** the circuit, its pin and class, and the `e51e2b86` bindings. Per-instance files are byte-identical to
`68ae79f2`'s writer; I checked the prover's and the verifier's files byte for byte on RoPE.

## 2. Done now: writer, prover and verifier

- **Rust:** `Instances` keeps the tables and refs. Digest regions are read by ref, the row roots are over the tables, and the
  drawn statement takes the population's refs of the drawn units.
- **Python:** `verity_flock.circuit.write(..., share_rows=True, rows=, outs=)` and `stage(..., share_rows=True)`, or the CLI
  flag `--share-rows`. Both dedupe identical rows per port in first-occurrence order.
- **New negative:** `row_ref_claim_false`. The statement names another row of a table, and the prover's witness reads the
  committed one: both reps reject.

**Selftests, CPU:**
- **GEMM K = 2048:** a 2 × 2 grid of coordinates, `y` from the subcircuit's evaluator (tables `x`: 1, `w`: 2). Passed:
  honest, `row_ref_claim_false`, `digest_claim_false`, `output_claim_false`, `unit_draw_session`, `record_replays_offline`.
- **RoPE:** a shared-row file passed the full suite, 32 of 32 (its `cs` table is one row).

**GPU:** the witness sources get per-instance rows gathered by ref, so the GPU path is unchanged.

## 3. Memory: no per-instance row copies

- **Where rows are gathered:** only in the witness, and only for the statement being proved. That is the drawn units after
  `Register`, or the whole file if no draw is made. `serve`, `check_public` and `drawn()` never gather rows.
- **Measured:** a synthetic A4-sized verifier file (6,171,648 instances; tables 861 and 21,504) loads, computes every root
  (including the 6.17 M `y` leaves) and reaches the root compare in about 13 s on this VM's CPU, at a peak RSS of about 6.1 GB.
  - The body is 65 MB. The peak is the **header**: 936 MB of JSON, because `units.indices`, `units.blocks` and `units.classes`
    are per instance, and `classes` is 6.17 M copies of one 128-hex class.
  - The prover's file adds 175 MB of rows plus salts, and the drawn statement clones the header once, so plan on about 8 GB.
- **If that's too much,** a compact `units` would cut it (for example `classes` as `[[class, count]]` runs, with `blocks`
  implied by `vus_per_block`). That changes the `e51e2b86` bindings' format, which the Lean verifier parses, so it's your
  call, not mine. Say if you want it.

## 4. Unrelated but visible

- `68ae79f2` corrected the identity text (sha512), so statement digests differ from `e51e2b86`'s.
- `855fe81f` applies PR #137's EX2 clamp in the attention circuit. That changes attention's pin, not any of your six templates'.
