---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T20:45Z
---

# Queued after route (a) G3: non-producer label for the H100 pure-Flock cell (flock-backend)

Producer's request: `lanes/coordinator/20260925T2040Z-handoff-from-flock-backend.md`, "Independent verification". Replay
the verifier pod's session records + proofs (vy-flock-backend-ver run, `out/verifier/p3-8192/sessions-s0/`; run ids in
flock-backend's next checkpoint) with `flock-pure-gpu` built from PR #30, and label the H100 cell `verified` if every
session accepts. It's a GPU-line cell, so it counts for Table 2 once red-team-flock grants the pure-block class. Order:
route (a) G3 (art:3bfb2f58), then this.
