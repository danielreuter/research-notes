---
lane: pouw-queue
kind: report
created: 2026-09-30T21:12Z
status: open
---

CHECKPOINT e15dc1ef1 (23:16Z) [open] 23:16Z node 2: timed window holds 8/8 GPUs, fill paused. PoUW ready 5.4 GPU-h: bc-7442ca43 4.33 (gpu2-h2hash-die0..7, queued 4:12 PM PDT after the 3:16 drop of GPU 2's per-die hash bench), bc-e6a46970 1.07 (fp8gc-die0..7). Verity guests 1.0. No proposals
CHECKPOINT e15dc1ef1 (22:30Z) [open] 22:31Z node 2: PoUW ready 1.66 GPU-h (bc-2aa33ad8 1.39 hsplit-w0, still queued despite the 3:16 PM drop; bc-0de2d624 0.27 per-die baselines), 7 PoUW GPUs running; Verity guests 8.5 GPU-h queued; 0/8 idle. No proposals. Both pq jobs withdrawn
CHECKPOINT e15dc1ef1 (22:19Z) [open] 22:19Z target changed: no 12 GPU-h watermark; proposals only when an owner would say yes (none tonight). Node 2: PoUW ready 3.48 GPU-h (bc-2aa33ad8 1.42, bc-0de2d624 1.07, bc-18346d9c 1.0), Verity guests 8.5 queued, 1/8 GPUs idle. Both pq jobs stay withdrawn
CHECKPOINT e15dc1ef1 (21:56Z) [open] 21:57Z pq-fp4-xdie-d4 withdrawn before it ran (DEFER). Proposal-only mode, nothing proposed. Node 2 ready: PoUW 3.58 GPU-h (bc-2aa33ad8 2.3, bc-6289d8b0 0.99, bc-18346d9c 0.3), Verity guests 6.5 (max_min bound). node-1 list row withdrawn (21760552)
CHECKPOINT e15dc1ef1 (21:43Z) [open] 21:44Z withdrew pq-aw-blk8s-newmodels to /workspace/pouw/fill-withdrawn/ before it started (held for the 4 PM PDT filler review); pq-fp4-xdie-d4 still queued for die 4; keeper runs to 8 AM PDT 1 Oct; VM was reset, notes and ssh setup restored
CHECKPOINT b1c77be02 (21:37Z) [open] 21:38Z ready useful 6.48 GPU-h (bc-6289d8b0 2.82, bc-2aa33ad8 2.3, bc-18346d9c 1.06, bc-829aa649 0.3); added pq-aw-blk8s-newmodels (blk8s census + rotb8s ppl, Llama-3.1-8B-Instruct/3.2-1B); pq-fp4-xdie-d4 waits on die 4. blocker: reviewed code has no more useful GPU work, short of 12
CHECKPOINT b1c77be02 (21:24Z) [open] node-1 overflow list pushed: lanes/kueue-fold/20260930T2123Z-handoff-from-pouw-queue-node1-overflow-jobs.md (52d171df). queued pq-fp4-xdie-d4.sh (f8f6f4 recheck on die 4 vs die 2). GPU1 rc=4 = Pearl-C k%1024 refusal, owner fixed (kpad); no rerun needed
CHECKPOINT b1c77be02 (21:12Z) [open] pouw-queue keeper started (worker of bc-e90634dd, agent bc-829aa649); job 1 node-1 overflow list due 2:45 PM PDT; job 2 keep >=12 GPU-h ready on node 2
