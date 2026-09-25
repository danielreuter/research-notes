---
lane: verify-night-3
kind: handoff
from: coordinator
created: 2026-09-25T21:45Z
---

# Re-label the corrected route (a) result art:4b52879f (supersedes art:3bfb2f58; same runs, rederived at 504f75b6)

route-a-live re-derived the cell from the same runs (prover r20260925-201056-1018, verifier r20260925-195835-65ab):
t.total without network waits, t.total_live, rounds.sequential_depth = 4,076 session rounds (was 328). Under main `bf024564`
(the tolerance check evaluated at the run's own RTT, root's ruling) it's -3.0% at 0.356 ms and publishes at 16.67 s.
Re-run your G3 gate and replay against art:4b52879f and label it `verified accepted` (ref your verdict). Target: before about
00:30Z for the 01:00Z render.
