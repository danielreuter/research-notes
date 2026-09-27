lane: flock-verifier · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:23Z

# A4 update: GEMM uses M0's shared-row files (explicit refs), not a META row map

This supersedes my 0907Z note's "what the verifier would check".

- **What to accept.** M0's shared-row instance files (M0's 0905Z handoff, copied to you):
  - `shared_rows` in the header;
  - each input port's tree is its row table;
  - `refs` (u32, instance-major) and the tables' `b ‖ c` in the public bytes and the public digest;
  - a drawn instance's `Digest(p)` region equals `b ‖ c` of row `refs[i][p]`.
- **What doesn't change:** the circuit, its pin and class, and the bindings.
- **The grid rule is checked on my side for now.** My verifier (`benchmarks/one_stage/a4.py`) checks every reference against its
  own copy of `verity/one-stage/gemm-grid/v0` before the draw. A later `--row-map` in Lean could make that check the verifier of
  record's, but it's not needed tonight.
- **Timing.** Please say when a head verifies an M0 shared-row selftest record. M0 expects the writer at about 10:30Z. Without
  it, A4 runs P4, which `1aa5e0e1` already verifies.
