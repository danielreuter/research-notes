---
lane: route-a-live
kind: handoff
from: coordinator
created: 2026-09-25T21:50Z
---

# Add to your reopen: record live.loopback_round_seconds (renderer change on main 90090210) in the corrected route (a) result

Main `90090210` changes how the renderer splits a live cell's time (root's ruling on the ±10% question):
- When `interaction.t_total_includes_wait` is set, prover compute is `live.prover_compute_seconds`. Before, network time was
  counted twice.
- The prover's own per-round live-coin handling, **measured on loopback, is prover compute**. The renderer reads it from a
  new field, `live.loopback_round_seconds` (seconds per round, same binary and batch size, verifier on loopback). Rounds ×
  that, at most the measured wait, moves out of the network wait, and the ±10% check then compares the measured wall with
  compute + rounds × 1 ms + bytes ÷ 100 Gb/s.
**Record `live.loopback_round_seconds` in every live result you register** (and say how it was measured).

Route (a) has 4,076 rounds, so its loopback per-round figure matters. Use your loopback run (e.g. the 16:50Z producer
self-test's per-round time) or measure it with the same binary. Add it to the corrected result, alongside the fixed
`rounds.sequential_depth` (my 2130Z handoff).
