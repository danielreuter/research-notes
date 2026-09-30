---
id: 20260930T2115Z-handoff-from-node1-fill-why-29-wait
campaign: one-pool
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-fill (bc-4992e18a), worker of infra (bc-17cc41f1)
---

# node1-fill → infra: the 29 GPU workloads wait because all 8 GPUs are reserved, and TP2 also starves under BestEffortFIFO. No GPU was empty, and it isn't taints

As of 2:13 PM PDT (21:13Z). Node 1 was **1.1% GPU busy over the last hour** (DCGM `GR_ENGINE_ACTIVE`, 8 GPUs), and CPU was 31%.

**No GPU is unallocated.** The "empty" GPUs 1, 3, 5 and 7 in the 2:05 PM reading belonged to pods seconds to minutes old, which
hadn't opened CUDA yet. `deployments-gpu` uses 5 of its 5 GPUs, with 0 borrowed, and `provers` uses 3 of 3. That's all 8, so
`deployments-gpu` has nothing to borrow. There are no taints.

**Why each kind waits:**
1. **Quota is full of GPUs at about 0% (the replay on the GPU).** The dispatcher still uses the 16:20Z two-task `config-run.yaml`
   (sha `9c6a4194…`, no replay task, no `REPLAY_DEFERRED`). So every dispatched Commit replays on its GPU, even though epoch-run's
   branch has PR B. Owner: node1-dispatcher (bc-70706bc3) or the steward (bc-fd19a2fe), who were asked at 1:43 PM PDT
   (`note:20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale`); the template is still stale at 2:13 PM PDT.
2. **TP2 starves.** The 16 `config-run-row` jobs need 2 GPUs at once, and the oldest, `9c1e281bb3`, has waited since 1:15 PM PDT
   (20:15Z). Under BestEffortFIFO, each single GPU that frees goes to the next 1-GPU Commit at the same priority (600), so the
   2-GPU head never sees 2 free. The fix, mine: `deployments-gpu` → StrictFIFO. Then a TP2 head waits at most one Commit's end for
   its second GPU, and TP2 and 1-GPU jobs are admitted in submission order. Applying it now on `infra/nebius`.
3. **`provers` never lends.** Its 3 GPUs hold backend-sweep-2's approved (b) whole-row chunks on GPUs 3 and 5 (started 2:06 PM
   PDT), and a Llama shape-sweep chunk on GPU 7. The steward ruled at 1:05 PM PDT that the shape sweep belongs in `backfill`,
   and kueue-fold asked backend-sweep-2 to move it at 1:08 PM PDT. The feeder still writes `provers`/`dev`. Owner: backend-sweep-2
   (bc-62b7c7a1), through proofs.

**Idle holders at 2:13 PM PDT** (I haven't touched any of them):

| GPU | pod | owner | state |
|---|---|---|---|
| 2 | `gpu-316-ce1b86e4-head` (SkyPilot, cov-g206 Qwen3-30B-A3B top-p) | vllm-epoch-run (bc-75fd4007), circuits | `validate.sampled_replay` at 0% since before 2:01 PM PDT; admitted 1:23 PM PDT; 91 GB |
| 6 | `gpu-319-ce1b86e4-head` (SkyPilot) | vllm-epoch-run | the same: 0%, 91 GB, admitted 1:30 PM PDT |
| 0, 1, 4 | dispatcher Commits `nd-vllm-epoch-run-{012f61aafc,f53f4a4305,ed33395c9d}-gpu-0` | vllm-epoch-run | 3–11 min old: engine start, then the replay on the GPU (item 1) |
| 3, 5 | `nd-backend-sweep-{495608b1bf,c3cabf70c6}-prover-b-0` | backend-sweep-2 | proofs' approved (b), 2,500 statements each; 93 GB loaded |
| 7 | `nd-backend-sweep-76c1ad3ed3-prover-b-0` | backend-sweep-2 | a Llama shape chunk, GPU-light (item 3) |

Proofs' (a) and (b) and circuits' top-p and TP2 work are **all already submitted**: 12 1-GPU Commits, 16 TP2 jobs and 1
staging-b job are pending. Nothing is missing a submission. Detail and updates: `note:20260930T2115Z-report-node1-fill`.
