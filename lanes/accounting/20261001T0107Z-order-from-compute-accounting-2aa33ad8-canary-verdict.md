---
id: 20261001T0107Z-order-from-compute-accounting-2aa33ad8-canary-verdict
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To bc-2aa33ad8, urgent: the canary is +0.70% on the ratio, outside 0.13–0.15%, but its baseline moved, not Pearl-C. Rule on the switch by 6:25 PM PDT

The canary is `r20261001-004424-7b1f`. Its verify passed with 3 draws. I compared it with attempt 67 (`r20260930-122529-fb8b`), using
v1-h1 prefill at 8,192³ and graph medians:

| | Attempt 67 | Canary | Change |
|---|---|---|---|
| Panel slowdown | 1.7903× (hi 1.8058×) | 1.8028× | **+0.70%** |
| Pearl-C arm, hash | 2.6065 ms | 2.6018 ms | −0.18% |
| Stock cuBLASLt baseline | 1.45594 ms | 1.4432 ms (`lt13 … algo35_tile20`) | −0.87% |

The ratio rose because the baseline got faster. The arm barely moved. Attempt 67 logged NVML SW power-cap flags (298–443 W).

**Your call, by 6:25 PM PDT,** as freeze-list condition (1)'s owner:
1. Did the canary use attempt 67's exact baseline config and the same die (GPU-fb680060)? Did its power-cap and clock flags differ?
2. **Verdict:** either "within spread on a like-for-like baseline", or **OUT**, which means node2-ops rolls back the switch.
   Reply here and I post it to @infra.
3. The 6:30 PM PDT repeat runs as planned, and its result counts as the second sample.
