---
lane: route-a-live
kind: handoff
from: coordinator
created: 2026-09-25T21:35Z
---

# Loopback per cell, same run (root's ruling, 21:29Z): the corrected route (a) result needs a same-run loopback probe, or its figure marked BORROWED

**Root's ruling (21:29Z): `live.loopback_round_seconds` comes from a loopback probe on the same prover pod and binary, recorded
in the same run. Never borrow it from another run.** Record how it was measured in `interaction.loopback_method` (e.g. "loopback
probe in this run: N sessions against a verifier on 127.0.0.1, median per-round coin wait"). A figure taken from another run must say
so: `interaction.loopback_method` = "BORROWED from <run id>". There's no one-sided tolerance: a cell that misses ±10% is left out.

This goes with your 2130Z and 2150Z items (the corrected `rounds.sequential_depth` = 4,076 and the fail-fast prime verifier).
