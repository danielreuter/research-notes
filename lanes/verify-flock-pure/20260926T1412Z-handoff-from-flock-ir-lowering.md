---
lane: verify-flock-pure
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T14:12Z
---

# flock-ir-lowering: class cell c1 (T = 1..128) is ready to replay, art:4fb2de9c; the replay script's class support is 31d275ad

- **Cell:** `art:4fb2de9c24a72b19afb05f1139d635625cc5d901ea5a2d8fbed11c87fd16f0cf`.
  - Verifier run r20260926-132839-b5e6 (vy-flock-ir-lowering-b-ver): its `out/verifier` has `class.json`, `net-t1..128.txt` and `p0-2048/sessions-s0..127`, each 1 probe + 1 warm + 5 timed.
  - Prover run r20260926-132856-68b3.
- **Inputs for `34-ir-replay.sh`:** set `art:74986510` (T 1..128, 16 heads per T), `TEMPLATE=attention-head`, `PER=16`. It is 128 sub-batches, so about 770 sessions to replay.
- **Build:** `flock-ir-frame` from 31d275ad, or any commit from 11f24da6 on: the cells ran on 11f24da6, and 31d275ad adds the script's class support.
- **Next:** c2 around 14:25Z and c3 around 14:35Z. I'll send each one's runs when it registers.
