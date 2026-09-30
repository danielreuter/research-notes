---
id: 20260930T2118Z-handoff-from-infra-phase-split-kueue-fold
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# kueue-fold: in the node-1 fold, the GPU is booked only for a job's GPU phase; each phase is its own Workload, chained

**Requirement: the GPU is booked only for the GPU phase** (Daniel, 2:16 PM PDT). This applies to `research run --queue` and to the node-1 fold.
- **Phases:** a job declares its phases, for example `--phase cpu:prep --phase gpu:commit --phase cpu:replay`, or a spec with a list of phases. Each phase is its own allocation, chained by the queue. CPU phases run in CPU slots on either node, and the GPU lease covers only the GPU phase.
- **Kueue can't release a GPU mid-Workload,** because it books the pod set at admission for the Workload's whole life. So on node 1 each phase is its own Workload, the way the three-task template with `REPLAY_DEFERRED: auto` already works.
- **The costs, handled explicitly:**
  - **Hand-off between phases:** outputs go to node-local disk and are passed by path, and the replay bundle can be about 90 GB. Chain phases on the same node by default.
  - **A re-queue gap before the GPU phase:** reserve the GPU phase when the CPU phase is about to finish.
  - **Lost warm state:** model load and CUDA init happen again in the GPU phase, so warm the weights on local disk.
  - **More ledger rows.**
- **Failure feed:** a GPU phase whose GPU sits under 10% busy for 5 minutes goes to the failure feed as `gpu-idle-in-phase`, with its owner.
