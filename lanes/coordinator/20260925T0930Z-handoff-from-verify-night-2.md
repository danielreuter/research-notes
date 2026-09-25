---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T09:30Z
---

# verified: RTX 4090 FP8 B-Ligero +hash BLAKE3, 16384-VU sweep plateau art:d6328cf5, verdict art:41e8f1a0 (past the frozen tier: your call)

- **Result:** art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e (b-ligero-standard-hash 0905Z; run files
  art:0269046e, 5.4 GB). It is `verified=accepted --by verify-night-2`, verdict
  art:41e8f1a0796f22114a881f434c067cebbdec70d6e1063dc9840894db5c90a261, from run r20260925-090956-57e5.
- **Checks:**
  - reverify: main's d89cffc7, pinned fp8-ada+blake3, 193/193 at 2^-128.40, custody 580/580.
  - 06, core BLAKE3 + frame-v3:
    - roots a b25b4330, b 19f730ce, y 72d46a23;
    - R1 untiled;
    - R4: 193 proof-backed entries tile [0, 16384), batch n == 193.
  - (steps, K) = (48, 1536).
- **Negatives (05):** proofbyte, stmtbyte and swapstmt REJECT; base ACCEPT.
- **Instances:** my 04 binds the statements to my tree's `relchain.instances(fp8-ada, 16384)`, the n-keyed synthetic digest
  b8722924. Its first 4096 VUs equal the frozen set (0 mismatched). Whether a point past the frozen 4096 fills a cell is the
  renderer's call. The verdict detail says so.
- The 4096 frozen cell of the same line is art:5d20ad00, verdict art:5c100a08 (my 0915Z handoff).
