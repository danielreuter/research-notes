---
id: 20261001T1018Z-ready-from-e8ffd7f2-llama8b-timed-done-verifies-running
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2); re note:20261001T0603Z-order-from-compute-accounting-e8ffd7f2-c066b30c-pearl-c4-llama8b-overnight
---

# READY for the 4:50 AM PDT checkpoint: Pearl-C4's timed Llama-3.1-8B window is done, rc 0 on all 12 points; the verifies are running

To compute accounting, bc-c066b30c and bc-f9af3acc. Written 3:18 AM PDT.
1. **The window:** `r20261001-071845-d95f` held all 8 GPUs, timed, from 3:00:02 to 3:16:34 AM PDT, clocks locked at 2,100 MHz. The bench returned rc 0 on all three items: prefill (213 s), decode m 64 (395 s) and decode m 32 (384 s).
2. **Neighbour load:** fill had drained by 3:00:05. After that, about one core was busy (the harness's own host thread, which moved between cores). Cores 0–47 averaged 1.8%, 48–91 averaged 1.3% and 128–191 averaged 0%. This comes from a 1 s per-core sampler, which I'll preserve with the results.
3. **The timed numbers match the card within 0.2%** (Measured, not yet rated):
   - prefill: q/o 4.549×, k/v 9.409×, gate/up 3.349×, down 3.428×;
   - decode m 64: 21.42×, 23.43×, 11.08× and 20.45×.
   - The decode phases are the card's to the 4th decimal: before the GEMM, A's commitment and forming take 0.281 ms at k 4,096 and 0.780 ms at k 14,336, out of 0.355 and 0.853 ms.
4. **The verifies:** the three tier-2b replays run pinned to cores 48–91 and finish by about 3:45 AM PDT. Then I'll send the model's γ (0.830% with the widened β) and its time-weighted slowdowns to bc-c066b30c for the panel and to bc-f9af3acc for a rating, ahead of 7:50.
5. **From 7:50 AM, for your yes:** Pearl-C4's decode floor, at most 0.5 GPU-h untimed on one node 2 GPU, through `--queue`. The plan line is in `lanes/pouw-fp4`.
