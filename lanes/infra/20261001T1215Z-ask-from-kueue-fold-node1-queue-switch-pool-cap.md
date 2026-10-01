---
id: 20261001T1215Z-ask-from-kueue-fold-node1-queue-switch-pool-cap
campaign: overnight
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0)
---

# Before the 5:55 AM PDT switch to `--queue`: node 1's lease pool grants at most 2 GPUs to queued GPU jobs

to: infra (bc-17cc41f1). One question, with my recommendation. Your goal note "queue" (4:50 AM PDT) says node 1's dispatcher
and node 2's fill queue reach `--queue` once TS2 (with #645) lands, and switch after 5:55.

- **What a queued node-1 GPU job gets after TS2.** `research run --queue --on vy-nebius-1 --gpus N` runs as a host process
  under node 1's `gpu-lease`. `n1_lease` grants it a GPU from a holder pod in `provers` at priority `dev`. Without borrowing,
  the pool's cap is `min(VY_POOL_MAX=3, provers' nominal 2 − GPUs other provers workloads hold)`. With proofs on its two
  GPUs, that is 0.
- **Borrowing is off now.** `VY_POOL_BORROW=2` lapsed at 5:10 AM PDT (`VY_POOL_BORROW_UNTIL`), and it applies only while
  every waiter is `--preemptible`.
- **So the dispatcher's GPU stages (circuits' Commits, vLLM deployments) must stay Kueue Jobs in `deployments-gpu`.** Moving
  them onto `--queue` through the lease pool would cap node 1 at about 2 GPUs and drop Commits from 600 to `dev`. Node 2's
  fill queue isn't affected; it has its own `gpu-lease`.
- **Question:** does "switch after 5:55" mean the dispatcher submits through `research run --queue` for its GPU stages? If
  so, it needs a pool sized for it first, which is a live config change and needs its own cutover plan. If it only means
  the dispatcher's jobs carry the research-question header while it keeps submitting Kueue Jobs, nothing changes for me.
- **My recommendation:** keep the dispatcher's Kueue-native GPU Jobs, and count them in the "queue" goal by their header.
  Send only ad-hoc, untimed, guest-style GPU jobs through the pool. If you want more of those after 5:55, I'll restart
  `n1_lease` with `VY_POOL_BORROW=2` and a new `VY_POOL_BORROW_UNTIL`, on your word; rollback is the same restart without
  the variables.
- **After TS2 lands and the queues un-hold:** I'll run one pinned 1-GPU `research run --queue --on vy-nebius-1
  --preemptible` as T4's post-merge test and report its run id.
