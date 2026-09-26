---
lane: red-team-flock-3
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T11:12Z
---

# flock-ir-lowering: two commits since the f4cd5d4e/22dc6320 you took for the attention review. One changes the v3 statement digest; the other only the prover's thread count

- **0839742b:** `ir_frame.rs` `TAG` (the statement digest's domain tag) was still `verity/flock-ir-frame/v2`. It is now `.../v3`, matching the statement name, the Σ tag and the rep domains, which were already v3. The digest differed from v2's anyway, because v3 adds each port's words and hashed flag, but the tag now matches. Docstrings and template reasons also say v3. Nothing else changed.
- **ece9fdd2:** `33-ir-cell.sh` and `34-ir-selftest.sh` now size rayon from the cgroup CPU quota, reading v1 `cfs_quota_us` when there is no v2 `cpu.max`. On the US-NC-1 L40S (13.6 cores on a 128-core host) they had run 128 threads, and the timing guard flagged T=258 contended for throttling. The proof and statement are unchanged.

**L40S cells** (prover vy-flock-ir-lowering-nc-l40s; verifier vy-flock-ir-lowering-nc-ver in US-NC-1 over global networking, session Ping 0.12–0.14 ms):
- Twelve T values (1..4, 128..132, 256, 257) are registered on f4cd5d4e/0839742b at 128 threads. Driver log: `~/attn-cells.jsonl` on the control VM. The first is T=4, art:308df7ad; T=1 and T=4 used the old TAG.
- All sixteen T values are being run again at the quota's 14 threads, under 0839742b + ece9fdd2. Those are the cells I will cite; I'll label the earlier twelve superseded.
- GPU selftest with the device prover: 24/24 at T=129 on an L4 (sm_89, same architecture as the L40S), r20260926-092748-5876 (preserved).
