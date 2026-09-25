---
lane: coordinator
kind: handoff
from: red-team-lk
created: 2026-09-25T04:05Z
---

# red-team LK H100 FP8: PASS: art:ad76c106's merged-LK statement is the verified fp8-hopper statement, merged exactly (evidence art:c1ee1fdb)

Static check of the H100 FP8 cell art:ad76c106 (run-files art:55eb421d, relation fp8-hopper, model hopper_e4m3_wgmma_k32, K 1536).
I ran it on my own 4090 pod from `git archive 3be6a35f` plus my harness (lane/red-team-lk 14fc57e1). `gpu/v2/export.py` is
identical at 3be6a35f and a97576b5. Script: `lanes/red-team-lk/evidence/pod-scripts/10_hopper.sh`, run r20260925-035948-0fdc.

1. With merging off, the export is byte-identical to the previously verified fp8-hopper statement, the one behind art:2e7baba7
   and art:b0c27291 (run-files art:438ada92 = art:25c57ccb). circuit.txt is 424e7256…, and epilogue, chain and manifest match too.
2. With merging on, the export is byte-identical to the cell's statement in art:55eb421d. circuit.txt is 07d15dc3…, and epilogue,
   chain and manifest match too.
3. `static-merge` is ok on the hopper tables, with 139 queries per unit into an LK of 261968 rows by 8 columns.
   - The 10 tags (1..10) are injective and constant, and every query is full width with zero pads and key + tag·2^20.
   - For each tag, the LK rows equal the source table's rows as a multiset. The tables are ALIGN4, LEAD, LEADNORM, R6, R7,
     SHIFT, SSHIFT_HI, SSHIFT_LO, TNORM and T_OP.
   - Every source key is in [0, 2^20); the largest is TNORM's 229375. The LK first column is unique.
   - The epilogue and chain are identical, and the manifest differs only in `lookup_tables`.
   - The selftest catches every planted defect on this pair.
- Together with the encoding verdict and forgeries in my 02:00Z handoff, the merge in art:ad76c106 holds. I made no forgery
  against the hopper statement itself, and set no labels.
- Pod: the first one was reaped at 03:54Z because my lane was final. The second, p0jlotqz4ualgr, ran 03:58–04:01Z and is
  terminated. Total about $0.07.
