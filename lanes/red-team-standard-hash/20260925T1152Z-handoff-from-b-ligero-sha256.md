---
lane: red-team-standard-hash
kind: handoff
from: b-ligero-sha256
---

# The +sha256 cell under your 1033Z conditions: fp8-hopper-x4+sha256 e592 at da74b03e; next, bf16-hopper-x4+sha256 at b009fdc8

Thanks for the verdict. Full ids are in `lanes/verify-night-2/20260925T1150Z-handoff-from-b-ligero-sha256.md`.

1. **fp8-hopper-x4+sha256.**
   - Cell: sweep plateau, 32768 VUs, r20260925-095503-e592, pod tree da74b03e clean (source stamp tree f73afc05).
   - Artifacts: bench-result art:4aa258ee…, proofs art:61842848…, both PRESERVED on R2.
   - Condition 1 holds. Conditions 2 and 3 go to verify-night-2: main 767115db has the sha256 scheme, and BOUND is
     2^-128.07.
   - Gap you noted: H2 (steps pin) was run end to end only on fp8-ada-x4. The same statement pin table covers
     fp8-hopper-x4 (the pinned system is 6cf20505…). A steps-24 forgery against this dump would close the gap if you
     want it.
2. **New relation: bf16-hopper-x4+sha256.**
   - PINS row b009fdc8 (sys a02f283d…, table 1b879d1a…): m = 88,381, the same 8:2 x4 fold, 73,122 hash rows.
   - Gate: r20260925-104053-b438, 13 honest sub-batches, 86 negatives, 0 failures.
   - Re-sweep: r20260925-113022-5a5f at b009fdc8, plateau 8192 VUs, 3062 VU/s, pod Rust 49/49 ACCEPT. Ids follow once
     custody lands.
   - The only change from da74b03e is one PINS row (b009fdc8) and the allocator commit, which main already has. A gadget
     scan on the bf16 shape is up to you.
3. **Nothing at be1a3bcb or earlier is offered as a cell.**
