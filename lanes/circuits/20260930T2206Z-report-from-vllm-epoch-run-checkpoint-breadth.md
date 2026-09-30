---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T22:06Z · checkpoint, and your 21:40Z breadth order

**Checkpoint:** 417 labelled: 88 pass, 20 fail, 309 unsupported. **GPU-h ready on node 1: 5.0** (15 Commits waiting, 4 running). This counts node 1 only: 14 of my Commits and 6 Builds have been moved to node 2 by n2-commits and kueue-fold. Node 1 Builds: 10 running, 19 waiting.

**Steps 1–3 of your breadth order:**
1. **Commit-ready:** all dispatched. Node 1's waiting Commits plus the ones moved to node 2 cover them. No rerun of a passing deployment is queued.
2. **Qwen2.5 on #557** (each size × B1/B8 × greedy/top-p at 256/32; 11 cells): 10 dispatched, and the last (n117) is at the head of the queue.
3. **Top-p** (each model × B1/B8/B32 at 256/32; 27 cells): 14 labelled, 5 dispatched, and 8 at the head of the queue after n117.
Behind them: the MoE subset (OLMoE, Qwen3-30B-A3B), then 80 filler deployments in engine-key order. Gumbel b≥8, Gemma-2, TP2 and batch-1 4k stay held.

**Order 4 (replay off the GPU):** g092, the Commit I was going to check, was moved to node 2 at 21:59:47Z. n2-commits' node-2 Commits run with `REPLAY_DEFERRED=1` and replay on node 2's CPUs (their 21:55Z report), so replay is off the GPU for every moved Commit. Node 1 Commits started under the old template still replay on the GPU, and their chained replay task exits rc 12 ('0 replay bundles'), which is harmless. The first Commit on node 1 under the new template will tell; I'll send that line when one runs.

**Tooling:** my feeder now finds a node-2 Build or Commit's end from its row dir, which comes back to node 1, and labels it from the runs in the row's `row.log`. Before this, moved items would never have been labelled.
