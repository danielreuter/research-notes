---
id: 20260930T2110Z-handoff-from-infra-targets-and-12-gpuh-watermark
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: hit T2 (≥80% useful GPU busy and ≥60% CPU by 6:00 PM PDT) and keep ≥12 GPU-h of ready GPU work queued on node 2

Daniel's targets are in `lanes/infra/20260930T1845Z-report-infra.md` § Targets.
1. **The watermark.** Every alerts tick (every 15 min), compute the GPU-h of ready GPU jobs in the fill queue. If it's below 12 GPU-h,
   ping the owners through `lanes/pous/` and `lanes/compute-accounting/` (compute-accounting, bc-e90634dd, holds PoUW's queue now):
   say how many GPU-h are missing. At 2:05 PM PDT it was 0 GPU jobs queued.
2. **Fill with Verity GPU guests** when PoUW's GPU queue is empty and no window is on, from the one pool (`gpus=1`, preemptible).
   Ask kueue-fold and node1-fill for Verity GPU work that can run on node 2.
3. **CPU ≥60%.** 24 PoUW CPU jobs are queued. If slots, not work, are the limit, raise the fill queue's CPU concurrency for `gpus=0`
   jobs outside windows, within the memory budget.
4. **Report the hourly number,** useful GPU % and CPU %, in ops.md as now. Add a line to `lanes/infra/` only at 6:00 PM PDT, for T2: hit
   or missed, and why.
