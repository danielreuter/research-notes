---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T21:41Z · on your 21:09Z orders and 21:16Z template note

**Checkpoint:** 411 labelled: 82 pass, 19 fail, 310 unsupported. **GPU-h ready: 4.2** (17 waiting in deployments-gpu, 5 running). Node 1 Builds: 9 running and 0 waiting. Node 2 in flight: 6.

- **Order 2, stalled Commits:** the feeder now checks every pass. A Commit with no `commit.log` output for 20 minutes (60 in the GPU-side replay) has its job cancelled and is marked `hung` with its stage, and its model's unrun deployments are held (`grid_deferred_hung`). None is stalled now. Labelling a cancelled one waits until its attempt is published.
- **Order 3, node 2:** my six failed node-2 Builds (node2-ops 21:05Z) are rerouted: g058 (Mistral), g069 (Phi-3), g080 (Qwen3-30B) and g125 (OLMoE) run on node 1, and n061/n062 (Pythia) are labelled `unsupported`. I asked kueue-fold not to resubmit them (`lanes/kueue-fold/20260930T2128Z-...`). Until it posts the staged-model list, node 2 gets only Llama-3.2-1B, the model that has built there (cov-g153, cov-g188).
- **Order 4, replay off the GPU:** not confirmed yet. The dispatcher fixes an item's template when its first task is submitted, so Commits already in flight still replay on their GPU. The first Commit under the new template (`config-run@c43dba74fa68`) is **g092**, queued since 21:22:53Z. I'll send you one line once it runs.
- **My call, TP2 one at a time:** a 2-GPU `config-run-row` holds both GPUs idle through its CPU Build. With 15 of them waiting, and older than the single-GPU Commits, they would have been admitted first, about 10 idle GPU-hours. I cancelled the 15 before they started, and the feeder now runs **one TP2 at a time** (p002 is running), with single-GPU Commits filling the rest. **Say if you want TP2 faster;** it's one constant (`TP2_MAX`).
- **Pythia:** its Build refuses partial rotary (`_C.rotary_embedding` mutates an operand and no rule accepts it: cos_sin_cache (2048, 16) vs head_size 64). All 29 are labelled `unsupported` with that cause rather than run. The feeder labels any Build-declared refusal the same way now.

**Below target right now (4.2 GPU-h, not 12):** cancelling the 15 waiting TP2 tasks took their queued GPU-hours out of the count, and node 1's Build queue ran dry
while the feeder was paused for about 7 minutes. Builds are what make Commits ready, so node 1 now keeps 12 Builds pending instead of 8, and node 2 has its 6. The
number should climb as those Builds finish (a single-GPU batch-1 or batch-8 Build takes about 5–25 minutes).
