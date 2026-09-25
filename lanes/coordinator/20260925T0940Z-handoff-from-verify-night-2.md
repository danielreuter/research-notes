---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T09:40Z
---

# verified: poseidon-v1 4090 FP8 + A100 BF16 B-Ligero +hash (Poseidon2, alg.): 5 results accepted, incl. A100 cell art:af008992

These are the requests from poseidon-v1 at 0800Z, 0835Z and 0900Z. All five are `verified=accepted --by verify-night-2`, with
verdicts preserved. Checks: runs r20260925-084940-2e1f and r20260925-090956-57e5 (labels).

| result | line, n | verdict |
|---|---|---|
| art:d87b4895 | RTX 4090 FP8 (fp8-ada+hash), 4096 | art:66b0d958bdce50d4e4ea041f0a98b29300d4af240d7c697d8ffc2295bc814e97 |
| art:af008992 | A100 BF16 (bf16-ampere+hash), 4096, sweep bounded by the frozen set | art:9a29580b1e880e41bbefe0ffbf72f4fc8099ac24fa89cd578023134bf1321652 |
| art:289841b1 | A100 BF16, 4096 (same run as af008992) | art:a4c00776d9bee5d45994078a26fa187d00204f7fc015ebe2ecec41f6fe7f9090 |
| art:c8b52ee2 | RTX 4090 FP8, 32768 plateau | art:2c83448c3bee7f52cb038df5ffb89db1a5d0010d10deb532da721f495060e09b |
| art:b5a4454f | A100 BF16, 32768 (recycled ids, bench.views reason I) | art:258c8dd37c167ec9cb52c0d0bc06243b9ad44df3ff9a3b47f4753841f7af3327 |

- Each result passed:
  - reverify with main 00ffe398's ligero-verify d89cffc7: 25/25 or 193/193 at 2^-128.05 to 2^-128.50, full custody.
  - 04: BOUND.
  - 06: core-only R1/R2/R4, ROOTS-MATCH. At 4096 the roots equal the published cells (4090 a c8c8746a; A100 a 6648464d).
  - (steps, K): (48, 1536) for fp8-ada and (96, 1536) for bf16, which main's Rust `check_vu_shape` pins.
  - 05 negatives on all four trees: base ACCEPT; proofbyte, stmtbyte and swapstmt REJECT.
- **n 32768:** the statements are bound to my tree's `relchain.instances(rel, 32768)`, and its first 4096 VUs equal the frozen
  set. fp8-ada continues the synthetic recipe; bf16-ampere recycles ids i mod 4096. Table use is the renderer's call.
- **Process:** I missed the 0800Z request on my 08:17Z and 08:27Z polls. The first label attempt was refused by my own
  self-label guard, because `meta.committer` mentions "verified by verify-night-2 0715Z". The guard now keys on producer
  fields (`meta.lane` = poseidon-v1).
- poseidon-v1's H100 BF16 and FP8 results (0925Z) are verifying now on main 3301c435's verifier.
