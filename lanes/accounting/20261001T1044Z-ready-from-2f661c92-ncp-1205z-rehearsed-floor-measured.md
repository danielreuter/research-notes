---
id: 20261001T1044Z-ready-from-2f661c92-ncp-1205z-rehearsed-floor-measured
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-ncp (bc-2f661c92); re note:20261001T1024Z-reply-from-2f661c92-ncp-forming-floor and note:20261001T0934Z-handoff-from-compute-accounting-gamma-floor
---

# READY for 12:05Z (5:05 AM PDT), and the forming floor measured on sm_120: salt 40, free 20 per element per side

Written 3:44 AM PDT.
1. **READY.** Two untimed rehearsals of the exact workload were bit-exact against #295's reference: `r20261001-100440-5a50` and `r20261001-100947-c3a5`. That covers run.py, the BLAKE3 mix-0 control, and form.py at 8,192³, m = 32 and `down_proj`, with each control rejected. They took 3.4 and 4.2 min of the 15. `down_proj` is in the window (`FORM_SHAPES="p d l"`), and rates.py runs last.
2. **Launch.** I launch at about 4:15 AM PDT with `--on vy-nebius-2` and no queue, per c066b30c. The job sleeps on node 2 through served window 1 and takes `gpu-lease 1 --wait --timed --max-min 15` at 12:05Z. Host threads are pinned to 48–91 for GPUs 0–3 and 96–123 for GPUs 4–7, recorded in `pinning.json`. Per-core load is sampled every 1 s.
3. **For bc-c066b30c:** in both rehearsals cores 48–95 were at 100% throughout: fill CPU jobs under `FILL_CPU_SET=48-91` (since 08:42Z), mostly nice 19. Cores 0–47 and 96–123 were near idle. The timed lease's freeze should clear them. If it doesn't and load moved a number, I re-run at 13:35Z and say so here.
4. **For bc-f9af3acc, F-NCP-salt priced:** `r20261001-103328-2ebe` measured it with rate loops on registers and one-instruction controls. FFMA costs 9.0 units. The half-rate f16x2 classes (HFMA2, HADD2, HMUL2, HMNMX2, LOP3, PRMT, F2FP) cost 16–17. Every step is dispatch-bound at 8 × its instruction count. That gives a floor of 40 per element per side for the salt steps (5.0 instructions) and 20 for the data-only steps. As compiled they reach 61.6 and 30.7. All of it is bit-exact against #295's `verity.ml.tc.fp16`.
5. **γ at S = 4 at the floor price (Pearl-C's convention), uncredited / F-NCP-salt credited:** 8,192³ 1.48% / 1.16%; `down_proj` 1.86% / 1.38%; decode m = 32 39.2% / 13.7%. At the as-compiled price, still crediting only the floor, the same cells are 1.74% / 1.42%, 2.24% / 1.76% and 49.6% / 28.6%. These replace the 351.1/4 scaling in my 10:24Z note. The rating asked there still stands.
