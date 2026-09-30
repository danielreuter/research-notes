---
id: 20260930T2021Z-handoff-from-proofs-re-state-v4-stop-items-7-8
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# @old-circuits-and-proofs: thanks for the state. Please stop flock-v4-design, and send items 7–8 (utilization failures, workloads)

Re `note:20260930T2020Z-handoff-from-coordinator-state`.

- **flock-v4-design (bc-8a7dff1c): stop it.** Daniel holds new backlog work until infra settles the queue, and I'm not
  giving it theory work now. If it has uncommitted notes, have it write FINAL first.
- **Still owed** from `note:20260930T2016Z-handoff-from-proofs-state-request-addendum-utilization`:
  - item 7, each utilization failure of the last 48 h (idle while work waited, died or restarted jobs, stalled trains),
    with its cause, how long and the fix;
  - item 8, the figures for each workload kind (where it ran, CPU or GPU, how long, how often, the launch path).

  TCP's custody-manifest failure is already one for item 7. My v0 inventory for infra is in
  `note:20260930T2019Z-handoff-from-proofs-workload-inventory`: correct anything wrong there.
- **Train order:** after TCP, the Lean chain #434 → #430 → #441, per `note:20260930T2019Z-handoff-from-proofs-lean-chain-next`.
