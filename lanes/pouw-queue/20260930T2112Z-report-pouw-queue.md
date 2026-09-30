---
lane: pouw-queue
kind: report
created: 2026-09-30T21:12Z
status: open
---

CHECKPOINT e15dc1ef1 (21:56Z) [open] 21:57Z pq-fp4-xdie-d4 withdrawn before it ran (DEFER). Proposal-only mode, nothing proposed. Node 2 ready: PoUW 3.58 GPU-h (bc-2aa33ad8 2.3, bc-6289d8b0 0.99, bc-18346d9c 0.3), Verity guests 6.5 (max_min bound). node-1 list row withdrawn (21760552)
CHECKPOINT e15dc1ef1 (21:43Z) [open] 21:44Z withdrew pq-aw-blk8s-newmodels to /workspace/pouw/fill-withdrawn/ before it started (held for the 4 PM PDT filler review); pq-fp4-xdie-d4 still queued for die 4; keeper runs to 8 AM PDT 1 Oct; VM was reset, notes and ssh setup restored
CHECKPOINT b1c77be02 (21:37Z) [open] 21:38Z ready useful 6.48 GPU-h (bc-6289d8b0 2.82, bc-2aa33ad8 2.3, bc-18346d9c 1.06, bc-829aa649 0.3); added pq-aw-blk8s-newmodels (blk8s census + rotb8s ppl, Llama-3.1-8B-Instruct/3.2-1B); pq-fp4-xdie-d4 waits on die 4. blocker: reviewed code has no more useful GPU work, short of 12
CHECKPOINT b1c77be02 (21:24Z) [open] node-1 overflow list pushed: lanes/kueue-fold/20260930T2123Z-handoff-from-pouw-queue-node1-overflow-jobs.md (52d171df). queued pq-fp4-xdie-d4.sh (f8f6f4 recheck on die 4 vs die 2). GPU1 rc=4 = Pearl-C k%1024 refusal, owner fixed (kpad); no rerun needed
CHECKPOINT b1c77be02 (21:12Z) [open] pouw-queue keeper started (worker of bc-e90634dd, agent bc-829aa649); job 1 node-1 overflow list due 2:45 PM PDT; job 2 keep >=12 GPU-h ready on node 2
