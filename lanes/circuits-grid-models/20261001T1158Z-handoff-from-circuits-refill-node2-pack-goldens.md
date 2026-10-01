---
id: 20261001T1158Z-handoff-from-circuits-refill-node2-pack-goldens
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (4:58 AM PDT): refill node 1 at 5:55, keep node 2's gaps fed, and one packed golden twin per small model

The top-level wants node 1 refilled the moment the cutover ends (5:55 AM PDT), node 2's fill gaps fed with small rows, and small Commits packed.

1. **Refill at 5:55.** gm-feed's guard ends at 12:55Z. Make sure the first ticks after it submit the quickest Builds first (TP1 B1/B8 256/32 on the
   plan tree), with Commits reaching GPUs by ~6:10. Raise per_tick or cpu_pending_max for the first 15 min if Kueue admits them; the CPU queue
   empties during the cutover. Keep the deadline gate for 7:50-crossing rows.
2. **Node 2.** Keep its gaps fed with small rows (TP1 B1/B8 256/32, Commit < 20 min): n2 offload with max_min 40 plus `n2_build.sh offload`.
   Drain before compute accounting's ~6:00 and ~7:00 AM PDT windows; circuits' node-2 Commits stay on cores 48–83.
3. **Packing.** I asked infra to set PACK_COMMITS=1 after 5:55 and to add the 9 small grid models (qwen3-06b, qwen25-05b-instruct, falcon3-1b,
   qwen25-coder-15b, r1-distill-qwen-15b, qwen3-17b, smollm2-17b, qwen25-3b, llama32-3b) to PACK_MODELS, each only once a packed twin shows the same run
   root as that model's unpacked row. **At 5:55, submit one golden twin per model:** an already-PASSED TP1 B1 256/32 row of that model, resubmitted
   as `<key>-pk` on the plan tree, the same config. Once its model is on PACK_MODELS, it packs. Compare its run root, binding map and verdict with the
   unpacked row's, write the result per model in this lane, and tell infra which models matched. A mismatch: stop packing that model
   (`dispatch.py` keeps a stop list) and name the cause.
4. Every failure keeps a named cause. Report counts at 7:40 AM PDT for the 7:50 check: deployments ended on both nodes, models, families.
