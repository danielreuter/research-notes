---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T16:25Z

**#67 and #75 are running; the balance test blocks #60.**
- **#67 LAUNCHED 16:19Z** on `432edb3b`: `vyv-rf-epoch-67`, 2× L40 secure, $1.64/h, 499 GB, 256 vCPU, run `r20260928-161923-0a05`, 3 pairs, cap $13, ends about 21:50Z.
- **#75 LAUNCHED 16:08Z:** 2× L40S secure, 376 GB, run `r20260928-160802-960f`, 3 pairs, cap $12, ends about 20:40Z.
- **#60 is refused** by the balance test (16:23Z): $217.57 − running rows' remaining caps $147.38 − sweep $12.11 − POUS $15 − $25 = **$18.07 < $24**.
  - #68 ($13) and #70 ($6.5, which needs a cheaper 2× shape) still fit and are polling.
  - #60 retries every 2 min, and headroom grows as the sweep reserve runs down to 18:00Z and as rows finish under their caps (#4, #101 about 17:30Z).
