---
lane: red-team-flock
kind: handoff
from: coordinator
created: 2026-09-25T18:35Z
---

# REOPEN for a fourth audit: route (a) cell art:8f7ef58b at PR #28 (lane/agkr-flock-cell @ a1664ac9): E0, E1, P1–P3, plus a ruling on the verifier's independence

The producer's handoff is `lanes/coordinator/20260925T1830Z-handoff-from-agkr-flock-cell.md`. It has the audit list,
the `cell_gate.py` command for each round-2 session and the run ids.

- **Audit** your third audit's must-fix items as implemented: E0 (`SessionConfig::check`), E1 (`backends/gkr/tools/cell_gate.py`),
  and P1–P3 (root_F from the prime transcript; two GF(2^128) points, as Daniel confirmed; the keyed-BLAKE3 row leaf, as
  Daniel confirmed). PROTOCOL §17.5.
- **Rule:** does `cell-verifier` count as a non-producer verifier (E1)? It's a sub-agent the producer launched, but with
  its own lane, pods and operator id.
- **Check the C8 arithmetic:** the producer says A-GKR's hash term is SHA-512 Merkle, q²/2^512 = 2^-384, so the
  composed bound stays 2^-130.19.
- **Label** the cell per TABLES.md if it holds; it merges after your verdict.

Section 4a of `cloud-lane-setup.md` applies (reopened lane: open checkpoint first). Follow the idle-while-waiting rule
(section 6).
