---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T13:01Z
---

# The ChunkTail GPU failure is fixed: PR #75 (cursor/flock-chunk-tail-gpu-797a @ ea27aa86, on main). Re-run k2304 and k8960 on it

- **Cause 1: the claim cap.** Your `invalid argument at prove_chunk.cuh:544` was the device arena refusing to `begin`
  because the previous prove had aborted with it still open.
  - The prover took at most 16 region claims. ChunkTail with the BF16 epilogue has 9 regions, so 18 claims.
  - So the first prove refused at link (`FFI chunk: link refused (-1)`, the line just before the three :544 errors), and
    every later one failed at begin. Whole-chunk layouts have at most 12 claims.
  - The cap is now 64 (`MAX_EXTRA_CLAIMS`, asserted at statement build).
- **Cause 2: a deadlock.** With the cap fixed, the ChunkTail prover then hung: a rayon deadlock in its continuation
  accumulator table. That table is now sequential and computed up front.
- **Checked on an RTX L4:**
  - The old commit reproduces your error exactly (r20260926-113905-6e09).
  - On the fix, K = 2304 passes CPU and GPU selftests at 8 and 64 VUs, and three 512-VU sessions in one process are
    accepted at 1.44–1.52 s (r20260926-122547-cfbe).
  - K = 8960 passes the same selftests, and three 256-VU sessions (m33) are accepted at 2.5–2.6 s (r20260926-123657-2b0b).
  - All are PRESERVED.
- **For your cells:** build from PR #75's branch until it merges; no other changes are needed. The K = 8960 CN2 limit is
  still 1,820 VUs per proof. The L40S has 48 GB, so 1,024 per proof at m35 should fit there. On a 24 GB card, stay at
  m33 (256 VUs).
