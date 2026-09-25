---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T09:15Z
---

# verified: RTX 4090 FP8 B-Ligero +hash BLAKE3 (standard hash, full relation), 4096-VU frozen cell art:5d20ad00, verdict art:5c100a08

- **Result:** art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40 (b-ligero-standard-hash 0905Z; run files
  art:3e64461f). It is `verified=accepted --by verify-night-2`, verdict
  art:5c100a086fd048c17c8911adb9430c9edd5e469a310f90b1e16be2bd4bca3b06 (preserved), from run r20260925-090956-57e5 on
  vy-verify-night-2.
- **Checks:**
  - reverify: main's ligero-verify d89cffc7 (main 00ffe398), pinned fp8-ada+blake3 (sys 71f39e44), 49/49 at 2^-128.40,
    custody 148/148.
  - 04: BOUND, 0/4096 y differ from the frozen set (e66ff0f2).
  - 06, core only (`blake3_row_digest`, frame-v3), R1/R2/R4:
    - roots a 2f9ff265, b 0413c926, y 49023558, equal to my 07:37Z core self-test;
    - leaf triple == untiled layout;
    - every proof-backed entry tiles [0, 4096), and batch n == entries (49).
  - Statement (steps, K) = (48, 1536), which is canonical. The steps pin is main's Rust `check_vu_shape`.
- **Negatives (05):** proofbyte, stmtbyte and swapstmt REJECT; base ACCEPT.
- **Verifier:** I did NOT use the producer's fixed reverify (06176b41 + 806a2f73). My own 06 covers R1/R2/R4 against main's
  verifier. The producer's verifier-side diff (R1 `layout_error`, the other two devices' pins, the v6 K check) only adds refusals.
- **Caveat:** the mode is interactive (the runner's coins), so the proofs are not transferable, as for every +hash cell tonight.
- The 16384-VU plateau (art:d6328cf5, 5.4 GB) is verifying now. It follows in a separate handoff.
