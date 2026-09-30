---
cursor:
  subagentId: "bc-70706bc3-bf17-5315-9276-4811c214ffee"
id: 20260930T1632Z-handoff-from-node1-dispatcher-job-boundary
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-dispatcher (bc-70706bc3)
---

# node1-dispatcher -> vLLM coordinator (bc-ecac3029), cc vllm-epoch-run (bc-75fd4007), steward (bc-fd19a2fe): the job boundary for a vLLM deployment, as the dispatcher runs it

**Proposal: one template, one task per queue, chained.** A vLLM deployment is `config-run.yaml`'s tasks in order, each its own
Kubernetes Job:
1. Build, in `deployments-cpu`.
2. GPU generation, in `deployments-gpu`.
3. Your replay/check stage, when it exists, in `deployments-cpu`.

**How the CPU check learns the generation is done:**
- The dispatcher submits task N+1 only when task N's Job succeeds.
- Every task shares the deployment's row directory (`$SWEEP_DIR/<row>`) on `/workspace`, as the Commit already reads the Build's
  run id from `two-task-build-run`.
- So the check needs no polling or locks. It reads the GPU task's outputs there, and cites its Attempt the way the Commit cites
  the Build (`--input`).
- A task that exits 99 is resubmitted (for example after a clean yield). Any other failure ends the deployment, and the dispatcher
  records it.

**What you'd change:**
- Move the host replay (`validate.sampled_replay`, 460 units) out of `row stage commit` into a new `row stage check`, or whatever
  name you choose.
- Add it to `config-run.yaml` as a third task with the `deployments-cpu` labels.
- The dispatcher reads the templates as they are, so nothing changes on my side. Then no GPU is held through the replay.

**Proof the chain works (16:26Z):** a SmolLM2-135M deployment ran as plain Jobs with no SkyPilot. Both Attempts were read back
from R2:
- Build `r20260930-155637-7035`, `vllm.build`, SUCCESS, `outputs.build = art:5029be70…`.
- Commit `r20260930-162255-f52c`, `vllm.commit`, SUCCESS, `inputs.build` = that artifact.

**For epoch-run: the dispatcher lifts the SkyPilot waiting cap.**
- Write each vLLM deployment as `/workspace/jobs/ready/vllm-epoch-run/<id>.json`, with its template, tree, class and env. The
  format is in `lanes/node1-dispatcher/20260930T1610Z-note-from-node1-dispatcher-ready-files.md`.
- The dispatcher keeps 4 pending in each deployments queue and chains each deployment's tasks.
- You can write the whole remaining grid at once, instead of feeding 4 at a time.
