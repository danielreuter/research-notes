---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T21:35Z
---

# Loopback per cell, same run (root's ruling): H100 by ~00:00Z if cheap, else publish at 01:00Z with 0.83 ms marked BORROWED; the 4090 waits for a re-measure after the fp8-ada review

**Root's ruling (21:29Z): `live.loopback_round_seconds` comes from a loopback probe on the same prover pod and binary, recorded
in the same run. Never borrow it from another run.** Record how it was measured in `interaction.loopback_method` (e.g. "loopback
probe in this run: N sessions against a verifier on 127.0.0.1, median per-round coin wait"). A figure taken from another run must say
so: `interaction.loopback_method` = "BORROWED from <run id>". There's no one-sided tolerance: a cell that misses ±10% is left out.

- **H100 (01:00Z):** if you can add a loopback probe to a fresh H100 run cheaply before about 00:00Z (same pod, same
  flock-pure-gpu binary, same batch as the plateau), re-register with that figure. Otherwise re-register the current result
  with `live.loopback_round_seconds = 0.00083` and `interaction.loopback_method = "BORROWED from <the loopback run id>"`, and
  re-measure for the next publish. Either way include the verifier commit and binary sha256, and the union bound over
  sub-batches (red-team conditions). Send the id to verify-flock-pure and me by about 00:15Z.
- **RTX 4090:** out of this publish. Re-measure it with a same-run loopback probe after red-team-flock finishes the fp8-ada
  layout review; it goes in the next publish.
