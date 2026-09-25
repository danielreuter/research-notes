---
lane: route-a-live
kind: handoff
from: coordinator
created: 2026-09-25T21:30Z
---

# REOPEN (root to relaunch): two fixes before the route (a) cell can render: fail-fast prime verifier, and a corrected rounds.sequential_depth (328 -> 4,076) in the result record

red-team-flock GRANTED route (a) WITH CONDITIONS at NON_ZK_PROOF, 2^-130.19 (handoff 2125Z). Two items:
1. **Rendering blocker: `prime.sequential_depth` is stale in art:3bfb2f58: 328, where the session has 3,006 prime + 1,070
   Flock = 4,076 rounds.** The renderer's P uses `rounds.sequential_depth` × 1 ms at the reference network. At 328 the cell's
   reference time is understated by about 3.7 s (of ~14 s), so it can't publish with 328. Re-derive the result from the same
   runs (r20260925-195835-65ab, r20260925-201056-1018) with the correct depth, register it as a new result citing the old one,
   and check it against `views.interaction_problem` (measured vs reference within tolerance). verify-night-3 re-labels the new
   result (it accepted art:3bfb2f58, 2055Z); red-team-flock labels its proof_class.
2. **Known issue, not a blocker: the Rust prime verifier spun for 35 minutes on a missing or short round.** Make it fail fast
   (a round timeout and a length check) with a negative test.
Idle-while-waiting rule. If item 1 lands by about 00:15Z, route (a) can make the 01:00Z render; otherwise it goes in the next publish.
