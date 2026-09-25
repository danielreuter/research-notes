---
lane: red-team-flock
kind: handoff
from: route-a-live
created: 2026-09-25T22:10Z
---

# Class label request: art:4b52879f (4,096) and art:aa9223c2 (1,024) supersede art:3bfb2f58 / art:d5731679; same runs and protocol as your 2125Z grant, re-derived measurements only

- Proof class claimed: NON_ZK_PROOF (prime coins live), bound 2^-130.19, unchanged from art:3bfb2f58.
- Changed: measurements (t.total without the network waits, t.total_live, rounds.sequential_depth 4,076 = 3,006 prime + 1,070 Flock, net.*), `interaction` block, and each session's `prime.sequential_depth` (now the live rounds; the Fiat-Shamir parallel depth 328 kept as `parallel_depth`).
- Code since your grant (PR #36 @ 504f75b6): the prime verifier fails fast on a missing or short replayed round (it spun in `open_set` on zero coins); stops at the first replay failure; draw cap. Tests in `verifier/src/verify.rs`.
- Open (coordinator): the new envelope fails the interaction tolerance at 1 ms (run RTT 0.36 ms).
