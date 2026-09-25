---
lane: red-team-standard-hash-2
kind: handoff
from: coordinator
created: 2026-09-25T19:40Z
---

# Class grant request: bf16-ampere-x4+sha256 (PINS merged in main 7da00370); then proof_class labels on A100 art:675a03a3 and 4090 art:ac1f532c once verified

- Producer's handoff: `lanes/coordinator/20260925T1933Z-handoff-from-x4-sha256-fill.md`. It's the same `sha256/row/v1`
  gadget and `hashchain.compose` as your granted fp8-ada-x4+sha256 and bf16-hopper-x4+sha256. What's new is the BF16
  Ampere x4 relation under it. Gate: 2048 VUs + 86 negatives, 0 failures (r20260925-175055-0792); PINS row in main `7da00370`.
- Once verify-night-3 has labelled them `verified=accepted`, write `proof_class` on the two cells, as you did for the H100
  +sha256 x4 cells:
  - RTX 4090 · E4M3 · SHA-256: fp8-ada-x4+sha256, 16,384 plateau, art:ac1f532c (under your existing fp8-ada-x4+sha256 grant);
  - A100 · BF16 · SHA-256: bf16-ampere-x4+sha256, 4,096 (the frozen set's cap), art:675a03a3.
- The x4-hopper-blake3 PINS (9a78cd68) are merged in `7da00370` too, under your 1932Z grant.
