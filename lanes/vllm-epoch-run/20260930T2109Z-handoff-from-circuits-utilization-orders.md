---
id: 20260930T2109Z-handoff-from-circuits-utilization-orders
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits orders: node 1 GPUs busy is the top priority (≥60% by 3:30 PM PDT, ≥80% by 6:00 PM PDT); keep ≥12 GPU-h ready

Thanks for the 1:50 PM report. Daniel's targets (2:06 PM PDT): node 1 ≥60% GPU-busy on useful work by 3:30 PM, both nodes ≥80% by
6:00 PM. Node 1 was 4% busy 1–2 PM with all 8 GPUs allocated. In this order:

1. **Keep the GPU queue full:** at least 12 GPU-h of ready work in `deployments-gpu` at all times, in engine-key order: the 77
   top-p reruns, the 91 TP2 (root's 2-GPU `config-run-row`), the 29 Pythia-160M, and the rest of the runnable grid. Put
   "GPU-h ready" in every checkpoint. Don't wait for trains: run from your pre-merge branch.
2. **Kill GPU holders that do nothing:** cancel any Commit with no `commit.log` progress for 20 minutes (Gemma-2's hangs held GPUs
   for 50–90), label it with the stage it hung in, and hold its model. Gemma-2 stays held (39); its fix is backlog for now.
3. **Builds to node 2** (`n2_build.sh submit`, up to 6 in flight), keeping node 1's Build share full too. Only send models whose
   weights are staged there: Mistral-7B and Qwen3-30B-A3B aren't (six failed, node2-ops' 2:05 PM handoff to kueue-fold). I've asked
   @infra to stage them or list what is; until then, route those two families' Builds on node 1.
4. **Replay off the GPU:** I've asked @infra to refresh the dispatcher's `sky/jobs` and `sky/submit.sh` to `infra/nebius` `896d14cd`+.
   When it's done, check that the first dispatched Commit defers (a replay task appears and the GPU frees after the committed run),
   then tell me in one line. Keep PR B on every run branch.
5. **#557 swap:** go with `cursor/coverage-v1-2622` = main + #503 + #557 + #598/#599, without #483/#501 (both closed at 1:19 PM
   PDT), and rerun the Qwen2/2.5 deployments plus the 156 labelled `pending #535`.
6. **Chunked prefill:** agreed, label the 16 `-cp` `unsupported` ("execution label needs code in engine/build.py"); it's backlog.
   Prefix caching `-pc` as you said.

Blockers go to me in `lanes/circuits/` at once (I relay to @infra on Slack); results and numbers in your checkpoints.
