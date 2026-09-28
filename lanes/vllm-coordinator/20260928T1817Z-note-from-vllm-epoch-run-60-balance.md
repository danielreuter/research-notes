---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T18:17Z

**#60 is held by the balance test again, by $0.18** (18:16Z): $170.19 − running rows' remaining caps $106.37 − sweep $0 − POUS $15 − $25
= **$23.82 < its $24 cap**. #101's relaunch took $5. It passed at 17:37Z, but no 2× or 4× L40S-class shape was in stock then.
- **The windows:** #60's 3-pair start closes about 18:20Z, and its 1-pair start about 19:20Z (4.0 h).
- **The cap is sized for the wrong shape:** $24 is for 4× L40S ($4.36/h). On the 2× shapes it would actually get ($2.18/h or less), $12 covers
  the 1-pair 4.0 h plus margin.
- **Your call:** lower #60's cap to $12 (it launches when a shape appears), or keep $24 (it waits for headroom).
- #68 ($13) and #70 ($6.5) still fit the balance test and are waiting for stock.
