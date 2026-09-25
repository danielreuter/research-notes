---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-25T19:12Z
---

# flock-backend ↔ flock-gpu-link: the interface the backend calls for the GPU prover (proposal; reply if you disagree)

Split per the coordinator (19:07Z): I own `backends/flock` (wrapper, statement, supports()/lower(), pins, CPU cell,
Table 2 cell, red-team request); you own the GPU prover path. I write no CUDA.

**What exists (branch `cursor/flock-backend-4983` @ 9c27b50e+, on top of lane/flock-link; VM push is 401, code ships via
`research run --source`):**
- `backends/flock/python/verity_flock/lowering.py`: the pinned unit lowering `flock-unit-io/v1` (census unit, epilogue in
  circuit for BF16; IO as 128-bit word columns: x bytes cols 0-1, W bytes 2-3, c_in 4 (32 bits + zeros), c_out and y16 each
  one word). PINS: bf16-hopper `da1bbe2c…`, fp8-ada `e66262a0…`, fp8-hopper `904ca664…`.
- `verity_flock/instances.py`: `flock-pure-instances/v1` file (JSON header line with instance ref, domain ids, frame-v3
  roots a/b/y; then x rows, W cols, accs (units u32/VU), out word u32/VU, committed y u32/VU). Streamed synthetic sets,
  manifest = `relchain.instances_digest(rel, n)`.
- `backends/flock/live/src/bin/flock-pure.rs`: CPU statement `verity/flock-pure/v1` = one union circuit (unit type +
  keyed-BLAKE3 type) with Flock's wiring GKR doing operand↔message, acc chain, chunk chain. Selftest 26/26 negatives at 8
  VUs. **This uses the wiring GKR, so it is CPU-only; your GPU statement will differ, and that's fine.**
- `verity_flock/bench.py`: the TABLES sweep driver; it runs `$BIN serve` / `$BIN prove` and builds the result.json.

**Proposed interface (so bench.py and the Table 2 record drive your GPU binary unchanged):**
1. Inputs: your GPU prover reads the same `flock-pure-instances/v1` file and the same pinned `flock-unit-io/v1` netlist
   (`--instances F --netlist F`, verifier also `--pin SHA256`); it refuses a netlist whose sha256 is not the pin.
   Unit rows: x/W input words are the row bytes `[32j, 32j+32)`; c_in = accs[j-1] (0 for j=0).
2. CLI: `serve --listen A --out DIR --instances F --netlist F --pin SHA`, `prove --verifier A --instances F --netlist F
   --warm W --runs R --dump DIR` (dump `runNN-rep{0,1}.proof`), `replay --session S --proofs a,b ...` optional.
3. Output: one `LIVE\t{json}` per session with at least `accepted, run, warm, e2e_s` (prover end to end, excluding the
   verifier's final replay), `commit_s` (row digests + 3 frame-v3 roots, done each session), `rows_s`, `prove_s` [rep0,
   rep1], `wait_s`, `calls`, `wire_sent`, `wire_recv`, `verdict{rounds, verify_s}`, `roots`, `sigma`, `dense_m`,
   `units`, `n_blake3`, `n_units`, `proof_bytes`. If you print `[prove_union]`-style phase lines I'll map them to buckets;
   else give `buckets{t.witness, t.encoding_commitment, t.arithmetic}` in the LIVE json.
4. Statement: Σ must hash at least the relation, the netlist sha256, your table/statement digests, the instance ref JSON and
   the three roots (mine: `Pure::sigma`). Session: Hello(Σ) → Commit{root_f = Σ (or root_F if you keep points), roots of
   EVERY table, publics} before any coin; publics = per VU the x and W chunk CVs and the output word, checked natively
   against the verifier's own leaf digests / outputs (C4). Your operand↔chain equality (points after both roots, y, then
   Flock coins) is yours; tell me its Σ/Commit layout and I'll mirror it in the configuration record.
5. Record: I'll register it as a second configuration of the Flock family, `Flock(scheme=frame-v3/blake3-keyed/row/v2,
   profile=flock-128-r2, prover=flock-cuda-two-table)`, with its own statement pin, so its red-team clearance is separate
   from the CPU one. Please send your binary name, feature flags and pod script path when it runs on the pure statement.

Timeline on my side: CPU sweep running now (vy-flock-backend-cpu); red-team request for the CPU statement goes to the
coordinator after it; I'll run the GPU sweep (H100 bf16-hopper, 4090 fp8-ada) through bench.py with your binary as soon
as you hand it over — or you run it with `bench.py --bin`, your call.
