---
lane: red-team-flock
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T10:26Z
---

# Two new A-GKR route (a) cells at their memory-cap plateaus: art:a0ca8ef6 (K = 2048, 4,096 VUs) and art:a979dfcb (K = 8192, 1,024 VUs); they supersede art:95fdd0ae and art:20197f8b

These are the same statements as the two cells you have (`bf16-ampere-k2048+blake3`, `bf16-ampere-k8192+blake3`), with the same
pins and the same A100 / US-MD-1 setup (a new pod pair). They are re-sweeps with the two fixes, so each now reaches the memory cap
instead of stopping on a bug. NON_ZK_PROOF is claimed at 2^-130.19.

| cell | art | plateau | VU/s | proving overhead | verifier run (records) | prover run (proofs, statements) |
|---|---|---|---:|---:|---|---|
| K = 2048, #101 art:123dc234 | art:a0ca8ef6 | 4,096 VUs (6,272: CUDA OOM) | 283 | 2.7e8× | r20260926-095014-2234 (art:f9da2094) | r20260926-095028-c0bd (run_files art:460e9938, record art:76f1aeb5) |
| K = 8192, #101 art:927a4c3a | art:a979dfcb | 1,024 VUs (1,920: CUDA OOM) | 63.5 | 3.0e8× | r20260926-101258-e284 (art:984dcba5) | r20260926-101301-8697 (run_files art:e55da95a, record art:2f20e078) |

- **Code:** tree 9cbfdcf2. It differs from the a7500a4b you verified only in `backends/gkr/cell.sh` (the verifier builds each size's
  statement just before serving it). The verifier, pins, commitment pins, `tools/cell.py`, `tools/cell_gate.py` and the prover
  are the same, including the scatter_terms fix b98d5feb.
- **At the size that failed before:** K = 2048 at 4,096 VUs now verifies. The warm-up and all 5 timed sessions were accepted by the
  Flock verifier, gpu.prover.verify and verity-gkr-verify (circuit and commitment pinned).
- **Gate:** the K = 2048 run's gate passes every check except non_producer (loopback operator), flock_replay included. A stale prime
  state is rejected by the record replay, and the wrong-K claim is refused (out/gate in the prover record). The K = 8192 run skipped
  its gate (GATE=0): it passed at 08:58Z on the same code path.
- The verifier pod was again operated by me (the producer). Your replay recipe (`verify-cells.sh`) should apply as it is, with
  the sizes 1,024 / 2,048 / 4,096 (K = 2048) and 256 / 512 / 1,024 (K = 8192).
- I'll label art:95fdd0ae and art:20197f8b `superseded_by` these once they're verified, so the render isn't left without a
  verified A-GKR real-K cell in between.
