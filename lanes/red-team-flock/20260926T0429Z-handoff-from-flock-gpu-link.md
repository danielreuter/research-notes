---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T04:24Z
---

# CN2 and CN3 are enforced in admission at e4f631bd, on top of NV5 (e84e3fe2)

- **CN2:** `admit` refuses k_log + log2(blocks) > 35, which for Chunk(n) is n × VUs > 32,768, before any coin.
  The selftest case `batch_past_m35` asks for one VU more than m35 holds, and it is refused.
- **CN3:** `admit` refuses `Chunk(1)`, the 1024-byte rows. The selftest case is `chunk1_rows`. `Layout::of` still maps a
  1024-byte / 32-unit file to Chunk(1), and admission refuses it.
- **Evidence:** CPU selftests pass on every layout with both cases. The honest 1,920-VU Chunk(16) file at m35 is admitted.
  The statement digests are unchanged.
