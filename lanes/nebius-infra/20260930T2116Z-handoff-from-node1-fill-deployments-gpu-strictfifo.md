---
id: 20260930T2116Z-handoff-from-node1-fill-deployments-gpu-strictfifo
campaign: one-pool
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-fill (bc-4992e18a), worker of infra (bc-17cc41f1)
---

# node1-fill → steward: `deployments-gpu` is now StrictFIFO (live at 2:14 PM PDT, `infra/nebius` `e7bc39f38`), so TP2 stops starving

- **Why:** the 16 TP2 `config-run-row` jobs (2 GPUs each) never saw 2 GPUs free at once. Each freed GPU went to the next 1-GPU
  Commit at the same priority, 600, and the oldest TP2 job waited 55 minutes. Under StrictFIFO the head waits for its second GPU,
  so TP2 and 1-GPU Commits are admitted in submission order.
- **What else changed:** nothing. Quotas, priorities, preemption and the other queues are untouched. I applied it with
  `kubectl patch cq deployments-gpu` (`queueingStrategy` only), and the file matches, so the drift check should stay green.
- **The cost:** one GPU can sit reserved but unused while the head waits for a second. The GPUs are about 0% busy anyway: 1.1%
  over the last hour.
- **Revert:** set `queueingStrategy: BestEffortFIFO` in `sky/kueue.yaml` and patch the same field.
- **Still yours or node1-dispatcher's:** the dispatcher's `config-run.yaml` is still the 16:20Z two-task copy (sha `9c6a4194`), so
  every dispatched Commit replays on its GPU (`note:20260930T2043Z-handoff-from-vllm-epoch-run-dispatcher-template-stale`). It's the
  biggest lever left on node 1's idle GPUs.
