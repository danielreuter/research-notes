---
lane: pouw-queue
kind: report
created: 2026-09-30T21:12Z
status: open
---

CHECKPOINT b1c77be02 (21:37Z) [open] 21:38Z ready useful 6.48 GPU-h (bc-6289d8b0 2.82, bc-2aa33ad8 2.3, bc-18346d9c 1.06, bc-829aa649 0.3); added pq-aw-blk8s-newmodels (blk8s census + rotb8s ppl, Llama-3.1-8B-Instruct/3.2-1B); pq-fp4-xdie-d4 waits on die 4. blocker: reviewed code has no more useful GPU work, short of 12
CHECKPOINT b1c77be02 (21:24Z) [open] node-1 overflow list pushed: lanes/kueue-fold/20260930T2123Z-handoff-from-pouw-queue-node1-overflow-jobs.md (52d171df). queued pq-fp4-xdie-d4.sh (f8f6f4 recheck on die 4 vs die 2). GPU1 rc=4 = Pearl-C k%1024 refusal, owner fixed (kpad); no rerun needed
CHECKPOINT b1c77be02 (21:12Z) [open] pouw-queue keeper started (worker of bc-e90634dd, agent bc-829aa649); job 1 node-1 overflow list due 2:45 PM PDT; job 2 keep >=12 GPU-h ready on node 2
