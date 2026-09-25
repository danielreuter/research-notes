---
lane: agkr-flock-cell
kind: handoff
from: coordinator
created: 2026-09-25T18:16Z
---

# C8 decided: A-GKR's hash budget counts toward the whole-proof bound, so route (a) is 2^-127.7 today. Raise it to >= 2^-128 and report the cost

Daniel's decisions (via the root, 11:15 AM PT):
- **C8:** the A-GKR hash term counts toward the composed whole-proof bound. Today's cell is therefore 2^-127.7, not
  2^-130.19, and doesn't meet the 2^-128 target.
- **P3 confirmed:** the keyed-BLAKE3 row leaf.
- **P2 confirmed:** the two GF(2^128) link points.

**Ask:** raise the A-GKR parameter that sets the hash term until the composed bound is **>= 2^-128**. Use whichever is
cheapest, hash output length or repetitions, and show the arithmetic behind the choice. Then re-run the timed sessions at
the new setting against the non-producer verifier.

Report:
- the new term and the composed bound;
- the prime-side and Flock-side time, before and after;
- the cell's new overhead (x native);
- proof and communication size, if they change.

Keep the old timed run as the baseline. Follow the idle-while-waiting rule: a WAITING checkpoint with the run id, then end
your turn.
