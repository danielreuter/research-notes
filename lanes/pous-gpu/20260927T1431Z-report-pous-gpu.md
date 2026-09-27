---
lane: pous-gpu
kind: report
created: 2026-09-27T14:31Z
status: open
---

CHECKPOINT 53bccf6b (15:06Z) [open] guard 'vy-pous-gpu': alive (pid 4742), last poll 15:06:33Z, spent $1.65 of $100, rate $3.49/h, deadline 17:30:00Z (replaced my 14:55Z guard, cap $40/17:40Z). Pod busy: r20260927-150115-df9e (1 KB raw-block honest tails). Next: CPU t_step bench. Acked 1440Z handoff
CHECKPOINT 53bccf6b (14:54Z) [open] vy-pous-gpu up 14:38Z (h1ab1zz6mptu1x, $3.49/h); r20260927-145214-e6d6 = P3 fused-decode check; re-prioritized per Daniel: hash primitives in fused kernel, then CPU+GPU oracle-round latency, then 1 KB raw-block honest tails; agent bc-dcd75184
CHECKPOINT 53bccf6b (14:31Z) [open] started 14:36Z: pous GPU measurements (fused decode cost, round/answer latency) on one H100 SXM, budget $100 separate from research cap, until 17:30Z; agent bc-dcd75184-1121-5344-9456-193b0d164e81; next: create vy-pous-gpu
