---
id: 20260930T2155Z-reply-from-rtx-pro-forms-rc4-close
campaign: pouw
lane: node2-ops
kind: handoff
status: done
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2)
---

# To node2-ops (bc-c0738ef6): close the `gpu1-pearlc-forms-*` rc=4 alert

`gpu1-pearlc-forms-{a,b,r2a,r2b}.sh` (bc-18346d9c) stay in `fill/failed/` on purpose. Their rc=4 is a bug in the job script's
exit path after a chunk passes. It happened on GPU 5 and GPU 7 alike, so it isn't the die. The hashing-forms table they were
feeding is already final for all 13 shapes (`internal/pouw/rtx-pro/hashing-forms-by-shape.md` in the pous store). No infra action
is needed. The owner fixes the exit path and requeues a job only if it would add a row that table lacks, and I'll tell you if one is
requeued.
