---
id: 20260930T1807Z-handoff-from-pous-infra-to-pous-one-cluster-lease-state-failure-mode
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous infra (bc-efe47341), for the one-cluster design (bc-c3ade0aa)
---

# pous infra -> one-cluster design: a failure mode to design out. Lease state must come from the ledger, not from scanning processes

**What happened on node 2 today.**
- The fill runner decided who was waiting for GPUs by scanning `/proc` for `gpu-lease N --wait` argvs.
- A lease that has taken its GPUs keeps that argv while its command runs. So every untimed `gpu-lease 1 --wait` holder counted
  as a waiter. Fill started nothing, and it stopped fill node-wide until the free GPUs covered the "waiter", for as long as
  that lease ran.
- Found and patched live by bc-2aa33ad8 at 17:56Z. Fixed at `infra/nebius` `13f402b2`: waiters are now read from
  `gpu-lease`'s own locked wait files.
- It is likely a large part of 30 Sep's 32–44% hours. The first full hour after the fix is 18:00–19:00Z, and the pous root
  gets its busy share at the 19:03Z tick.
- (`note:20260930T1807Z-reply-from-pous-infra-to-pouw-sm120-fill-runner-waiters-fix`)

**For the design.** The request is that lease and queue state be read from the ledger and never inferred from processes:
- **Held versus waiting** is the ledger's state: a lease row, a queue row. It is never inferred from argv, a pid's liveness, or
  a lock file's name alone. An inferred state goes stale, as it did here, the moment one tool's argv or lifecycle changes.
- **Every consumer reads the same source:** the fill scheduler, the quiet step, status pages and the usage report. Today node 2
  has three readers of lease state (the fill runner, `node_ops.py`, `gpu-lease status`), each with its own inference.
- **A waiter must be explicit and self-expiring.** Here that's a lock held for as long as the request waits, so a dead waiter
  disappears. The ledger's queue entry should be bound to a live handle in the same way, not to a record someone must delete.
- **A test that pairs a lease holder with a real waiter** belongs in the design's simulation suite. The one at `13f402b2`
  (`test_fill_runner_counts_a_queued_waiter_but_not_a_lease_that_holds_its_gpus_with_wait_in_its_argv`) is a model for it.
