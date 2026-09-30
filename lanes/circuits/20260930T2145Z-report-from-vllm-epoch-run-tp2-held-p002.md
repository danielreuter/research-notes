---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
status: open
---

CHECKPOINT 0178e309a (22:02Z) [open] 3:04 PM PDT: TP2 Commit crash (p002-2, likely no NCCL_P2P_DISABLE) routed to owner + gpuless lane; epoch-run: re-render 4 pending old-template Commits, T3 command; infra: front TP2 reference. Acted on inbox: kueue-fold n2-commits owner.
CHECKPOINT 0178e309a (21:54Z) [open] Daniel's rule applied: owner-approved items only, each names its research question, no filler (note:20260930T2154Z-..., note:20260930T2155Z-...). cov-g217 cross-node check awaits owner's yes. Kernel Q answered (#557).
lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T21:45Z · on your 21:38Z TP2 hold and kueue-fold's 21:26Z requeue

- **TP2 is stopped** (`TP2_MAX 0`), and all 102 TP2 deployments are held in `grid_deferred_tp2` until vllm-tp2-gpuless-build lands. **Crossed wires:** I had already deleted the
  15 waiting TP2 Jobs (cov-p004-2 … p085-2) at 21:40Z, before your handoff arrived, so node1-fill has nothing to deactivate. They're archived and won't be resubmitted.
- **`cov-p002-2`'s times, as you asked:** the 2-rank Build **passed in 955 s** (both GPUs held and idle), and the word check passed. The **Commit crashed after 68 s**:
  rank 1 hit `torch.AcceleratorError: CUDA error: an illegal memory access was encountered` (`Worker_TP1`). It's labelled `fail` with that cause (run
  `r20260930-212250-262e`, log `/workspace/jobs/cov/cov-p002-2/<row>/commit.log`). That's a TP2 finding for the GPU-less-Build lane to know about: the Commit, not
  just the Build, fails on sm_120 at TP2 (Llama-3.2-1B, batch 1, 1k).
- **Node 2:** I'm tracking kueue-fold's requeued g058, g069, g080 and g125 under their original keys, and not rerunning them on node 1. n061/n062 are Pythia (the Build
  refuses partial rotary), so their requeue will fail its Build again; they're labelled `unsupported`. Since `n2_build.sh offload --loop` now moves held node-1 Builds to
  node 2 by itself, I'll stop hand-submitting to node 2 and keep node 1's Build queue deep.
- **Order 4 (replay off the GPU):** still owed. g092, the first Commit under the new template, is waiting for a GPU.
