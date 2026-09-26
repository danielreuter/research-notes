---
lane: red-team-flock-3
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T14:40Z
---

# flock-ir-lowering: class cell c3 (T = 257..287, class [257, 512]) registered, art:4dd2069b. c2's first run was refused as contended by our own lingering GPU contexts; it is re-running

- **c3:** `art:4dd2069b9c797223093b2e23461aad1dc54c62ade344187f02f50a7d457d6b56`, at 11f24da6.
  - Prover run r20260926-140931-b414 on vy-flock-ir-lowering-b-l40s (machine pxp3jjc5ozkz).
  - Verifier run r20260926-140928-d05d on b-ver (machine daejz5pkfg8j).
  - Set `art:74de7df5`: 16 heads per T for T 257..287, source synthetic. Pin 365f1b5d.
  - It is the full-set point (CP8): `key_counts` lists all 31 T values, 16 heads each, and `per_key_count` has 31 entries (2.31 s at T=257 to 2.35 s at T=287 per 16-head sub-batch). 7.0 heads/s; it passed validation and is uncontended.
- **c2 (T 129..256):** the first run, r20260926-132849-6ee6 / r20260926-132838-47c3 at 11f24da6, was refused by `bench.cell check` as contended. There is no art.
  - The timing guard counted "1 other GPU compute process". Those were our own prover contexts, which NVML still listed more than 2 s after the prover exited. A 128-sub-batch cell gives that race 128 chances; it hit twice.
  - 53ffcaca: `ir_bench` now waits, between sub-batches and outside the timed sessions, until NVML lists no compute process (at most 20 s). The statement code is unchanged since 11f24da6.
  - Re-runs at 53ffcaca: r20260926-142744-14e6 / r20260926-142734-f7e5 on pair a (machines av7yp9ygnbzg / oc60c34mphhh), and a backup, r20260926-143648-ba5a / r20260926-143635-57a2, on pair b. Both land around 15:15–15:25Z. The first clean one counts; I'll label the other superseded.
