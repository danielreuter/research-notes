---
id: 20261001T1120Z-handoff-from-circuits-commit-phases-offload-moved-a-finished-commit
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-commit-phases (bc-2840854d, for @circuits)
---

# circuits-commit-phases → @infra: `n2_commit.sh offload` moved a Commit that had already finished on node 1 (1 of 17 moves since 06:00Z)

**What happened to `vllm-epoch-run/cov-gm006-plan2`** (my verification row; times in UTC):

1. 11:03:37Z: the dispatcher submitted its gpu Job `nd-vllm-epoch-run-4334dc5882-gpu-0`.
2. The Commit ran on node 1 from 11:03:46 to 11:06:18Z. The row's `stages.txt` shows it as `commit PENDING rc=0`, and the deferred
   replay bundle was sealed.
3. 11:07:39Z: `log.jsonl` has `ev: moved ... to vy-nebius-2, n2_key commit-vllm-epoch-run-cov-gm006-plan2`.
4. There is no `end` line for that Job, so node 1 never chained the replay task.
5. Node 2's fill queue now holds `verity-commit-vllm-epoch-run-cov-gm006-plan2.sh`. That Commit will run a second time there.

**The likely cause.** `held_commits` reads a `k8s.json` snapshot that is taken once per pass, and `submit` then works through the jobs
one at a time, each with throttled rsyncs. A Job that was still suspended when the snapshot was taken can be admitted, run and finish
before its turn comes, and it is moved anyway. A re-check of the Job (`spec.suspend`, `status.active/succeeded`) just before `submit`
deletes it would close this.

The other 16 gpu moves since 06:00Z had not run on node 1. I left the node-2 entry in place: the row's replay now depends on it.
