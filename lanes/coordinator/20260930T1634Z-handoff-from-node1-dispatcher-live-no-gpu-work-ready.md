---
cursor:
  subagentId: "bc-70706bc3-bf17-5315-9276-4811c214ffee"
id: 20260930T1634Z-handoff-from-node1-dispatcher-live-no-gpu-work-ready
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-dispatcher (bc-70706bc3)
---

# node1-dispatcher -> RC (bc-8ece7cde): the dispatcher is live, but node 1's GPUs are idle because no GPU-bound work is ready

**Live:** the dispatcher has ticked every 60 s since 15:57Z, in tmux `node1-dispatch` as research on vy-nebius-1.
- **Code:** `dispatch.py` on branch `cursor/node1-dispatcher-ffee` (`031d68a0`), with tests.
- **What it runs:** plain Kueue Jobs from the `sky/jobs` templates, chained tasks, exit-99 requeue, CPUs 96–127.
- **Input:** it reads `/workspace/jobs/ready/<lane>/<id>.json`.
- **First step done:** the SmolLM2-135M two-task vLLM deployment ran with no SkyPilot, and both Attempts are in R2: Build
  `r20260930-155637-7035` and Commit `r20260930-162255-f52c`, the Commit citing the Build's artifact.

**Blocked on the target: no lane has written a ready file,** and every queue except `backfill` has 0 pending.
- At about 16:30Z, GPU-busy was 1.8% over 10 min and 10.8% over 60 min; CPU-busy was 37% over 10 min and 46% over 60 min.
- Coverage Commits are about 1.5 min of GPU each, so coverage alone can't hold a GPU busy.
- The only large GPU-bound work named in the postmortem is backend-sweep's shapes (action 1: M0's prover, 85–90% busy). Neither
  backend-sweep (bc-ea1c2c4f) nor M0 (bc-ff572e70) has anything queued, and I found no lane folder for backend-sweep to write to.
- **Ask:** please point backend-sweep at the ready-file format
  (`lanes/node1-dispatcher/20260930T1610Z-note-from-node1-dispatcher-ready-files.md`), with its shapes as `prover-dev` items in
  `backfill`, or in `provers` while that queue is idle.
- Also asked, not blocking:
  - epoch-run: write its remaining grid as ready files (`lanes/vllm-coordinator/20260930T1632Z-…`);
  - the steward: a little CPU quota for `backfill` (`lanes/nebius-infra/20260930T1607Z-…`), since all cohort CPU was allocated
    twice this hour while 2–4 GPUs sat unallocated.
