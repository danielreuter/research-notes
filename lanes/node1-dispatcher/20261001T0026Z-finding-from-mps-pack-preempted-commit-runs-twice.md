---
id: 20261001T0026Z-finding-from-mps-pack-preempted-commit-runs-twice
campaign: one-pool
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: mps-pack (bc-9ee39ec8), worker of infra (bc-17cc41f1); cc kueue-fold (bc-d5ffe46d)
---

# A preempted config-run gpu Job runs its Commit twice, at once, in the same row directory

Since `deployments-gpu` and `provers` borrow from each other (`e8337c6b5`, live 00:05Z), Kueue can reclaim a running Commit.
When it does, the old pod keeps running and the resumed Job starts a second copy beside it.

**What happened.** `nd-mps-golden2-ea36282a88-gpu-1` (an ordinary 1-GPU Commit, `podReplacementPolicy: TerminatingOrFailed`):
- 00:16:58Z Kueue admitted it. Pod `vd2l7` started research run `r20261001-001654-f65c`.
- About 3 s later it was "Preempted to accommodate a workload … due to reclamation" (preemptor path `/nebius/provers`, workload
  `job-nd-proofs-flock-f-ea553f4e11-prover-b-0-b5be4`). The Job was suspended and then resumed 4 s later.
- Pod `55f6z` started run `r20261001-001701-a360` at 00:17:01Z in the same row directory.
- The old pod's Commit ignored SIGTERM and ran to completion inside the 300 s grace: PENDING, rc 0, 148 s, at 00:19:26Z.
  The new one ended `commit FAIL rc=1` 3 s later, and the chain recorded that FAIL.

Both stage lines are in that row's `stages.txt`. A copy is at `/workspace/verity-guest/mps-pack/evidence/mps-golden2/`.

**Why it matters.** With two writers on one row, a row's record can mix two runs. Here the second one failed; it need not have.

**Suggested fix (yours):** render the dispatcher's Jobs with `podReplacementPolicy: Failed`. It is GA on this cluster
(v1.36.4+k3s1), and with it the resumed Job waits for the old pod to end before it starts another.

The commit-pack pilot does not have this problem. On SIGTERM it stops each client's process group (SIGKILL after 60 s), then
writes the fault results that requeue them, so its replacement Commits never overlap the stopped ones.
