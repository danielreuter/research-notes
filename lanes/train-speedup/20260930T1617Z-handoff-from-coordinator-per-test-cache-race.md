---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: train-speedup
kind: handoff
from: coordinator
to: train-speedup lane (owner of #512)
created: 2026-09-30T16:17Z
---

# Two checks sharing node 1 race on the per-test verdict cache

- **What happened:** train TVK's check `r20260930-155046-270c` passed every step, pytest included, then crashed while finishing:
  `FileNotFoundError: /home/research/.cache/verity/tests/per-test/backends_flock/backends~flock~tests~test_circuit.py--0225dc5a…`.
- **What was running:** two other checks on node 1 at the same time (slots b and c). All three share `~/.cache/verity/tests/per-test/`, so another check's pruning or replacement most likely removed an entry this one was reading.
- **Please:** make the per-test cache safe for concurrent checks on one host. Write entries atomically, never delete an entry another check may be reading (or ignore one that vanishes), and treat a missing entry as a cache miss rather than a crash.
- **For now:** I re-ran TVK (`r20260930-161436-541f`).
