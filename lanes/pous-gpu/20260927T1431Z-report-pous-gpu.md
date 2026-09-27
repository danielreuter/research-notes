---
lane: pous-gpu
kind: report
created: 2026-09-27T14:31Z
status: open
---

CHECKPOINT 5a7061c0 (15:45Z) [open] 64 KB k=1 L40S: fr at 0.3 ms under hbm, 30k rounds each: dev late 0/30000 (1d9f direct, 6def direct1), host late 2 and 4. serve fr running on both; then fetch + deliverable. Recorded CPU wide64 r20260927-153825-8050 (agent-VM Xeon, incidental). Spend ~$3.2
CHECKPOINT 5a7061c0 (15:38Z) [open] budget: POUS $200/20:30Z, my share $80 incl. spent; guard now prefix vy-pous-4090 only (pid 4998, cap $80, baseline $2.80, 20:30Z) so vLLM worker's vy-pous-vllm-gpu is not counted/touched. Running: 1d9f (64 KB tails) then r20260927-153736-6def (GIL-attribution: events+launch in one C++ call; fr at 0.3 ms). Only live pod: vy-pous-4090 (busy). Spend ~$2.9
CHECKPOINT 5a7061c0 (15:32Z) [open] scope narrowed (Daniel): honest 64 KB single-answer tails only; adversary calibration dropped; cap now $70. terminated 9d4dqa1v95nk55 (vy-pous-cpu) 15:31:00Z. WAITING r20260927-153131-1d9f on vy-pous-4090 (64 KB k=1 tails idle/hbm/serve/gemm + fr at 0.3 ms), check after 15:43Z; agent bc-742e3b0e-a1a2-5fdc-8e4d-de86601b1327
CHECKPOINT 5a7061c0 (15:29Z) [open] H100 vy-pous-gpu h1ab1zz6mptu1x: NOT running (terminated 15:12:40Z by prev agent; absent from pod list). Live: vy-pous-cpu 9d4dqa1v95nk55 + vy-pous-4090 qoyit5h904i2a2 (L40S) under guard prefix vy-pous- (pid 2904, cap $40, 17:30Z, baseline $2.60). POUS spend $2.79 (guard tally). ba5e done rc0 (1 KB tails); df9e failed pre-measure; e6d6 failed its wrong-salt check. Next: 64 KB wide-perm latency (CPU core + L40S SM), 64 KB tails
CHECKPOINT 5a7061c0 (15:18Z) [open] took over 15:17Z; agent bc-742e3b0e-a1a2-5fdc-8e4d-de86601b1327 (prev bc-dcd75184 stopped). pods up: vy-pous-cpu 9d4dqa1v95nk55, vy-pous-4090 qoyit5h904i2a2 (L40S). next: fetch e6d6/df9e/ba5e, CPU label-step latency
CHECKPOINT 53bccf6b (15:15Z) [open] pods: vy-pous-cpu 9d4dqa1v95nk55 (cpu5c 4 vCPU $0.14/h), vy-pous-4090 qoyit5h904i2a2 = L40S $1.09/h (no 4090/5090 stock in 5 tries); guards per prefix (cpu $10, 4090 $15, both 17:30Z). WAITING r20260927-151512-ba5e (1 KB probe tails, L40S). Next: CPU P3 round t_step
CHECKPOINT 53bccf6b (15:12Z) [open] terminated h1ab1zz6mptu1x (vy-pous-gpu, H100) 15:12:40Z; H100 spend $2.37 (40.7 min). Replanning per Daniel: CPU pod for P3 round t_step, RTX 4090 pod for honest 1 KB probe tails; no H100 re-measure
CHECKPOINT 53bccf6b (15:06Z) [open] guard 'vy-pous-gpu': alive (pid 4742), last poll 15:06:33Z, spent $1.65 of $100, rate $3.49/h, deadline 17:30:00Z (replaced my 14:55Z guard, cap $40/17:40Z). Pod busy: r20260927-150115-df9e (1 KB raw-block honest tails). Next: CPU t_step bench. Acked 1440Z handoff
CHECKPOINT 53bccf6b (14:54Z) [open] vy-pous-gpu up 14:38Z (h1ab1zz6mptu1x, $3.49/h); r20260927-145214-e6d6 = P3 fused-decode check; re-prioritized per Daniel: hash primitives in fused kernel, then CPU+GPU oracle-round latency, then 1 KB raw-block honest tails; agent bc-dcd75184
CHECKPOINT 53bccf6b (14:31Z) [open] started 14:36Z: pous GPU measurements (fused decode cost, round/answer latency) on one H100 SXM, budget $100 separate from research cap, until 17:30Z; agent bc-dcd75184-1121-5344-9456-193b0d164e81; next: create vy-pous-gpu
