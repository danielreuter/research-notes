---
lane: agkr-flock-cell
kind: report
created: 2026-09-25T17:38Z
status: final
---

CHECKPOINT c95dd13a (18:28Z) [final] route (a) cell art:8f7ef58b: A100 BF16 4096 VUs, 143.3 s (3.55e9x), 2^-130.19 (C8: A-GKR hash SHA-512 2^-384, no change). PR #28 @ c95dd13a (main merged). 5/5 sessions accepted by cell-verifier. A100 terminated 18:19Z; ~$3.1
CHECKPOINT a1664ac9 (18:25Z) [final] route (a) cell art:8f7ef58b: A100 BF16 4096 VUs, 143.3 s (3.55e9x), 2^-130.19 (C8: A-GKR hash term SHA-512 2^-384, no change). E0/E1/P1-P3 in PR #28 @ a1664ac9; 5/5 sessions accepted by cell-verifier. A100 terminated 18:19Z; ~$3.1. Handoff to coordinator for red-team re-audit
CHECKPOINT a83d7de7 (17:38Z) [open] timed run r20260925-173611-8cb5 launched 17:36Z (1 local warm-up + 5 sessions vs cell-verifier 157.157.221.30:26732, verifier run r20260925-172927-6883; writes result.json). Check back ~17:45Z; then gate, handoff, FINAL. PR #28 open (draft)

# agkr-flock-cell: the first route (a) cell (A-GKR + Flock + link), A100 BF16, 4,096 VUs

Checkpoints from 16:01Z to 17:36Z are in `20260925T1601Z-report-agkr-flock-cell.md`. That file is the same report: the
checkpoint CLI started this second file after a store error.

**The cell:**
- **Result:** bench-result/v1 art:8f7ef58b (run r20260925-173611-8cb5). t.total 143.3 s (5 timed sessions, min 134.0,
  max 145.1), **3.55e9× native**, composed bound 2^-130.19 (contract problems []).
- **Verifier:** lane cell-verifier's pod, round 2 (r20260925-172927-6883, art:3b185b68), 5 of 5 sessions accepted.
- **Earlier runs:**
  - round 1: 3 accepted sessions (verifier r20260925-164419-448b art:5a7ccc3b, prover r20260925-165446-17f9
    art:79d8d4a5). There Flock took about 21 s at 18 ms RTT, 5.3e8×.
  - loopback self-test (r20260925-165039-cc6b): prime 2.5 s, Flock 9.2 s, 2.3e8×.
- **Where the time goes:** Flock's 1,070 live-coin round trips (129–142 s of waits in round 2) dominate whenever the
  verifier is remote.
- **Sizes:** the prime proof is 58,994,344 B; the Flock proofs are 2 × 461 KB.

**Conditions:** all implemented; details in PR #28, PROTOCOL §17.5 and `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`.
- E0: the library refuses the ungated exchange.
- E1: `tools/cell_gate.py`.
- P1: root_F handed to the session; the points and y come from the record.
- P2: two GF(2^128) points.
- P3: keyed-BLAKE3 row leaf (two constants in Flock's circuit, no big-endian Λ, nothing broke).

**Tests:**
- flock-link selftest: all cases pass at 8 and 64 VUs (r20260925-170814-6f81, and again at 8 after the main merge).
- gkr pytest (test_circuit_pins, test_cell_gate, test_commit): 27 passed.
- gkr cargo test: pass.
- The producer gate preview admits a real session and refuses a swapped proof, the empty probe session and a
  producer-operated record.

**C8:** A-GKR's hash term is SHA-512 Merkle, 2^-384, so counting it leaves the composed bound at 2^-130.19. I changed
no parameter and did not re-run. The 2^-127.7 figure was from the SHA-256 era. Open for the coordinator: the other
256-bit hashes (Flock's BLAKE3 Merkle tree, the prime SHA-256 transcript, the leaves) under the same convention.

Handoffs received:
- `20260925T1816Z-handoff-from-coordinator.md` (C8): answered in `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`.
- `20260925T1830Z-handoff-from-coordinator.md` (merge main): done. Merged origin/main as c95dd13a, which touches no
  gkr or flock file; cargo test and the 8-VU selftest pass; pushed.

Handoff written: `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`, asking for the red-team re-audit.

## FINAL

~~~text
tip: lane/agkr-flock-cell @ c95dd13a (merged origin/main; base lane/flock-link@4b560b2b + lane/agkr-bound@89433d06)   merge-with: none (PR #28)
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too, per flock-link)    pod: vy-agkr-flock-cell-a100 terminated 18:19Z; ~$3.1 (A100 ~2.0 h × $1.39/h + cell-verifier ~$0.76)
artifacts: art:8f7ef58b art:9464fe7a art:3b185b68 art:5a7ccc3b art:79d8d4a5
~~~
