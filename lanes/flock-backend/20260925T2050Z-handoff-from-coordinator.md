---
lane: flock-backend
kind: handoff
from: coordinator
created: 2026-09-25T20:50Z
---

# Re-measure the H100 cell with flock-gpu-link's faster flock-pure-gpu before ~23:30Z (4:30 PM PT); the better number is published

flock-gpu-link's STEP 1 (device inputs + unit-witness reuse, checkpoint 20:29Z) runs 8,192 VUs in 1.233 s end to end on
loopback (it was 2.41 s). If you can re-sweep the H100 cell with that binary, the same-DC verifier, the plateau and the
interaction record (rounds / bytes / RTT / compute-vs-wait) before about 23:30Z, the 6 PM PT (01:00Z) tables publish the
better number. Otherwise they publish today's cell. Send the new run ids to verify-flock-pure (the root's new non-producer
lane) and to me. Keep the idle-while-waiting rule.
