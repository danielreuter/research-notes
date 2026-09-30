---
id: 20260930T2118Z-handoff-from-infra-freeze-signoff-and-phase-split
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: the freeze-list sign-off is in (a yes, with 3 conditions), and the GPU may be booked only for a job's GPU phase

**Sign-off** (`note:20260930T2110Z-handoff-from-pouw-sm120-to-infra-cutover-freeze-signoff`, in lanes/infra/): a yes, with three conditions.
1. **A canary after the switch.** Repeat a published row, and roll back if it falls outside the 0.13–0.15% spread.
2. **Quiet recorded per window,** so it can be looked up by run id.
3. **No switch in the last 24 h** before the 7 Oct clamp.

All three are now gates for your switch.

**Requirement: the GPU is booked only for the GPU phase** (Daniel, 2:16 PM PDT). This applies to `research run --queue` and to the node-1 fold.
- **Phases:** a job declares its phases, for example `--phase cpu:prep --phase gpu:commit --phase cpu:replay`, or a spec with a list of phases. Each phase is its own allocation, chained by the queue. CPU phases run in CPU slots on either node, and the GPU lease covers only the GPU phase.
- **Kueue can't release a GPU mid-Workload,** because it books the pod set at admission for the Workload's whole life. So on node 1 each phase is its own Workload, the way the three-task template with `REPLAY_DEFERRED: auto` already works.
- **The costs, handled explicitly:**
  - **Hand-off between phases:** outputs go to node-local disk and are passed by path, and the replay bundle can be about 90 GB. Chain phases on the same node by default.
  - **A re-queue gap before the GPU phase:** reserve the GPU phase when the CPU phase is about to finish.
  - **Lost warm state:** model load and CUDA init happen again in the GPU phase, so warm the weights on local disk.
  - **More ledger rows.**
- **Failure feed:** a GPU phase whose GPU sits under 10% busy for 5 minutes goes to the failure feed as `gpu-idle-in-phase`, with its owner.
