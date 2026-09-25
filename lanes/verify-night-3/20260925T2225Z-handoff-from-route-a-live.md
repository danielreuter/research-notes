---
lane: verify-night-3
kind: handoff
from: route-a-live
created: 2026-09-25T22:25Z
---

# Re-label request: art:77411c934df40460f2c2a737d8363d62934d9aaa40912a111960e97b2a4d152d supersedes art:112afcfa, art:3d7cbea2, art:4b52879f and art:3bfb2f58 (which you accepted at 2055Z); same runs, same proofs and records

- Only the envelope changed. It has re-derived measurements (`cell.py rederive` @ 8b14460e) and adds:
  - the protocol, sweep, commit and loopback blocks;
  - `refs.run_files` art:d9666f5a (the prover run's dump you replayed) and `refs.verifier_files` art:42841b22.

  The producing attempt is r20260925-221942-7052, and its script is `lanes/route-a-live/evidence/pod-scripts/40-rederive-4096.sh`.
- To reproduce, run that script's `cell.py rederive` line on art:4b52879f's payload, with `lanes/route-a-live/evidence/protocol-4096.json`, `sweep-4096.json` and the loopback times.json at `out/cell-4096/s0/times.json` in art:d9666f5a. The derivation is deterministic.
- This label is the only reason left on the renderer (U). It replaces my 2210Z request.
