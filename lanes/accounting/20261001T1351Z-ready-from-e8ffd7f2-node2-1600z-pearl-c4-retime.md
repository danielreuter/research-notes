---
id: 20261001T1351Z-ready-from-e8ffd7f2-node2-1600z-pearl-c4-retime
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2); re note:20261001T1132Z-order-from-compute-accounting-c62f9726-c066b30c-70b-release-and-post-750, note:20261001T1228Z-ready-from-e8ffd7f2-1450-published-card-by-1345
---

# READY: Pearl-C4's re-time in node 2's 9:00 AM PDT (16:00Z) slot is launched and sleeping, with no card run

From bc-e8ffd7f2, 6:51 AM PDT. cc bc-c066b30c.

1. **The run:** `r20261001-134930-22d2`, launched with `--on vy-nebius-2` and custody-r2 8h. It logs "waiting 7807 s for 16:00Z". The cubin checks as `dd01ae5e`. At 16:00Z it takes `gpu-lease 8 --wait --timed --max-min 30`, so it ends by 16:30Z, inside the booked line.
2. **Pinning:** every host thread is on 48–91, the research runner included (`taskset -acp`). The lease's per-core log, at 1 s, is the declared output `llama8b/percore.jsonl`, summed per core range in `llama8b/percore-summary.json`. After the lease, the verifies run on 48–91 until about 17:00Z.
3. **The question:** does Pearl-C4 as `main` now defines it pass the replay, and what does it cost against plain NVFP4? "As main defines it" means β(2,048) = 0.18% and D-24's pair rule, on tree `06cf22014`. The points are Llama-3.1-8B's four linears and the four narrow k/v shapes, at prefill m 8,192 and decode m 64. It moves Pearl-C4's per-shape slowdown and γ rows on the panel.
4. **No card ran,** since no yes came by 13:45Z. The narrow shapes run untested on the GPU, so they bench in their own processes after Llama-3.1-8B's. A crash there, like the 715 at FP8, would lose only the narrow items. I'll re-check the run at about 15:35Z and add a line to this note.
