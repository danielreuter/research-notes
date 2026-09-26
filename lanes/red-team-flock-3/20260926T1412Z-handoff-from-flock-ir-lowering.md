---
lane: red-team-flock-3
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T14:12Z
---

# flock-ir-lowering: class cell c1 (T = 1..128) registered, art:4fb2de9c. The full-set point, so CP8 holds; the code is at 11f24da6 = 4eb3b991 plus CP2

- **Cell:** `art:4fb2de9c24a72b19afb05f1139d635625cc5d901ea5a2d8fbed11c87fd16f0cf`.
  - Prover run r20260926-132856-68b3 on vy-flock-ir-lowering-b-l40s (L40S, pod epczpcyja4oqsh, machine pxp3jjc5ozkz).
  - Verifier run r20260926-132839-b5e6 on vy-flock-ir-lowering-b-ver (pod 34vxo7onho9xig, machine daejz5pkfg8j), US-NC-1, over podnet.
  - The pair was planned through PR #74's check, and `cell.placement` is in the registered document.
- **Set:** `art:74986510` (key_class_sets T 1..128, 16 heads per T, source synthetic). Class pin 2f102216.
- **CP8.** The plan has one point, the full 2,048-head set, in 128 sub-batches, one T each. The registered result is that point:
  - `key_counts` lists all 128 T values, 16 heads each;
  - `per_key_count` has 128 entries, from 0.18 s at T=1 to about 0.69 s at T≈100 per 16-head sub-batch;
  - it passed validation, is uncontended, and runs at 32.8 heads/s (e2e 62.4 s for the whole class).
- **Commit:** 11f24da6, which is 4eb3b991 plus the CP2 check (the manifest must be its own canonical serialization; a duplicate key and a whitespace variant are refused). `git diff 4eb3b991 11f24da6` touches only `check_class` in `bin/flock-ir-frame.rs`. 31d275ad after it changes only `34-ir-replay.sh` and a `getattr` in `ir_bench.stage_point`; no cell ran on it.
- **Next:** c2 (T 129..256, set art:82c591d1, pair a: machines av7yp9ygnbzg / oc60c34mphhh) lands around 14:25Z. c3 (T 257..287, set art:74de7df5, class [257, 512], pair b) lands around 14:35Z. Both are at 11f24da6.
