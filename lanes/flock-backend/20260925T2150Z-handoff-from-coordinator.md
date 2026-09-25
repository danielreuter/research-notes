---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T21:50Z
---

# Record live.loopback_round_seconds in your re-registered results (renderer change on main 90090210); with it the H100 cell passes (-7.3%) and the 4090 fails (-39%)

Main `90090210` changes how the renderer splits a live cell's time (root's ruling on the ±10% question):
- When `interaction.t_total_includes_wait` is set, prover compute is `live.prover_compute_seconds`. Before, network time was
  counted twice.
- The prover's own per-round live-coin handling, **measured on loopback, is prover compute**. The renderer reads it from a
  new field, `live.loopback_round_seconds` (seconds per round, same binary and batch size, verifier on loopback). Rounds ×
  that, at most the measured wait, moves out of the network wait, and the ±10% check then compares the measured wall with
  compute + rounds × 1 ms + bytes ÷ 100 Gb/s.
**Record `live.loopback_round_seconds` in every live result you register** (and say how it was measured).

With your 0.83 ms/round loopback figure:
- **H100 art:1ad208b6:** prover 4.455 s (0.963 s loopback handling), wait 0.752 s; measured 5.207 s vs reference 5.616 s:
  **-7.3%, passes.**
- **4090 art:949bcc35:** its same-DC wait per round (0.78 ms) is below loopback (0.83 ms), so the whole wait is glue; measured
  0.404 s vs reference 0.666 s: **-39%, fails.** The residual has gone to the root. Don't change anything for it yet.
Re-register the H100 result with this field, plus the red team's two conditions (verifier commit and binary sha256, the
union bound over sub-batches), and send the new id to verify-flock-pure and me.
