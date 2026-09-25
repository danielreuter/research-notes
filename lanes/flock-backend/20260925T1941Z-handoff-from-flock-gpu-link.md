---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T19:41Z
---

# flock-pure-gpu exists (CPU + GPU, flock-pure's CLI); CPU selftest 17/17 at 8/64 VUs on your bf16-hopper files; H100 run in flight

- Branch `cursor/flock-gpu-link-797a` @ 996013f0 (PR #30); if origin lacks it (VM push 401s intermittently) it is also on
  the pods via `research run --source`.
- Build: `backends/flock/pod/20-gpu-link.sh MODE=build` (GPU=0 for a CPU-only build) → `flock/target/release/flock-pure-gpu`.
  GPU needs `cuda_chunk_patch.py` + `flock-gpu-link-b684b12.patch` (the script applies both). `22-pure-gpu.sh` is my runner.
- CLI as agreed: `serve --listen --out --instances --netlist --pin [--sessions N] [--operator]`,
  `prove --verifier --instances --netlist [--gpu] [--warm W] [--runs R] [--dump DIR]`, `selftest [--gpu] [--only CASE]`.
  bf16-hopper only (16-bit rows of 3 chunks, 96 units): the file and netlist relations must match, the netlist sha256 must be `--pin`.
- LIVE json: accepted, run, warm, e2e_s, commit_s, rows_s, prove_s[2], prove_total_s, buckets[2]{t.witness, t.encoding_commitment,
  t.arithmetic, t.link, t.zerocheck, t.lincheck, t.ring_switch, t.ligerito, t.total}, wait_s, calls, wire_sent, wire_recv,
  rtt_ms + rtt_method (the Hello round trip), verdict{rounds, verify_s, handle_s (your 8d6abf3c, merged)}, roots, sigma,
  dense_m, nbl, n_blake3, n_units, proof_bytes, netlist_sha256, statement_digest, statement, prover="flock-cuda-block".
- Public claims layout (quote it): module docstring of `backends/flock/live/src/pure_block.rs`; Commit publics are 68 bytes per
  real block b = 3v + c: x chunk CV (8 u32 LE), W chunk CV (8 u32), unit 31's y16 (u32; checked via the Y region at c < 2, the
  verifier's out word is used at c = 2). The cross-chunk accumulators are NOT publics: the verifier takes them from the
  instance file's recorded accs (AccIn/AccOut regions). Σ = SHA-256("verity/flock-pure-block/sigma/v1", relation, vus, units,
  row_bytes, nbl, m, netlist sha256, statement digest, instances JSON, roots a/b/y).
- Limits: m = 20 + log2ceil(3·vus): 4,096 VUs → m34, 8,192 → m35 (the largest Fast100 config), so a proof's plateau is ≤ 8,192
  VUs; larger batches are sub-batches.
- H100 run r20260925-193447-1f8e (GPU selftest 8/64, loopback 2048/4096/8192, 4 sessions at 8192 against a same-DC CPU verifier
  r20260925-193409-4413). I'll hand you the numbers; you own the cell (bench.py --bin flock-pure-gpu).
