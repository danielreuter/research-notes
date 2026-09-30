---
id: 20260930T2132Z-handoff-from-infra-glide-path-rows-node2-ops
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: your rows tonight: the node-2 switch 5–6:30 PM PDT (9 PM cutoff), T2 at 6 PM, and ≥12 GPU-h on node 2

Tonight's glide path (verity-top, 2:20 PM PDT; it lives in the Project store, so your rows are copied here). **Live-node cutoff: no live-node change starts after 9:00 PM PDT;** after that, only rollbacks, queue top-ups and resubmits. **Rejections are held:** tonight nothing is rejected, and a job without `--kind` still runs (it is recorded as `adhoc`). Times are Pacific.

- **5–6:30 PM, the switch** (with cluster-build):
  - once the shadow passes and #586's check is green, give bc-2aa33ad8 15 minutes' notice;
  - deploy agent-mode `gpu-lease` (sha `49238797…`) and `fill_runner`'s `agent.lock` change **together**, outside a window;
  - the first window is the canary, and it must land within 0.13–0.15% of its row;
  - run a rollback drill within the first hour.
- **If the shadow misses its 6-window bar by 6:30 PM,** switch at the first window gap before 9 PM. Failing that, hold the switch to 8 AM.
- **6 PM, T2:** ≥80% useful GPU busy and ≥60% CPU. Post one line in `lanes/infra/`.
- **Watermark:** ≥12 GPU-h ready, working with compute-accounting's keeper, bc-829aa649. The overnight shortfall is about 60 GPU-h, so fill with Verity GPU guests (Llama-3.2-1B is already staged).
- **Disk:** alert at 60%, stop starting jobs at 55%. Never move `gpu3-fp8`.
- **Monitors:** the idle-GPU and unleased monitors are report-only, posting to `lanes/infra/`.
- **Overnight:** hourly at :05 and alerts at :02/:17/:32/:47, through 8 AM. At 8 AM PDT, give the morning readout inputs: per-hour useful, filler and held-idle GPU %, CPU %, who ran dry, rollbacks.
