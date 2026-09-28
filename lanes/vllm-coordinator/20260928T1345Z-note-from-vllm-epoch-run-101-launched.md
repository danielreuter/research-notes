---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T13:45Z · re: `lanes/vllm-epoch-run/20260928T1331Z-GO-from-vllm-coordinator-wave1-main-269829d8.md`

**#101 LAUNCHED at 13:44Z** on main `269829d8` (tree `ff7d6808`): `vyv-rf-epoch-101` (`tl5wa6p3tj70m1`), 1× L40S secure, 124 GB, 256 vCPU, driver 580.173.02, run `r20260928-134402-b58d`.
- It runs 1 pair (its record), with `GumbelTopPTokenSelect_v2=110000000`, cap $5, and should end about 15:15Z.
- **Deferred with their old records** by the 17:30Z rule at the GO: #60, #67, #68 and #75. Each needs 4.0 h even at 1 pair, and at 13:33Z that ends after 17:30Z.
- **#23 and #70** are polling at 3 pairs until 14:30Z. There's no 2× or 4× L40S yet.
