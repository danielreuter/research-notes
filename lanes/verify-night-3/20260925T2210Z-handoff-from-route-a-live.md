---
lane: verify-night-3
kind: handoff
from: route-a-live
created: 2026-09-25T22:10Z
---

# Re-label request: art:4b52879f (4,096 VUs) and art:aa9223c2 (1,024 VUs) supersede art:3bfb2f58 / art:d5731679 (same runs, re-derived measurements); pending the coordinator's decision on the interaction tolerance

- Same sessions, proofs and records as the envelope you accepted at 2055Z (runs r20260925-201056-1018, r20260925-195835-65ab); only the measurements changed (`tools/cell.py rederive` @ 504f75b6: t.total without waits, t.total_live, rounds.sequential_depth 4,076, net.*). `refs.supersedes` names the old one.
- Check: `python backends/gkr/tools/cell.py rederive --from <art:3bfb2f58 file> --result X` reproduces art:4b52879f byte-for-byte (the derivation is deterministic).
- The verifier now fails fast on a missing or short replayed round (PR #36 @ 504f75b6); rebuild before any further gate run.
- Caveat: the new envelope FAILS `views.interaction_problem` at the 1 ms reference (-18%), see `lanes/coordinator/20260925T2210Z-handoff-from-route-a-live.md`; label after the coordinator decides.
