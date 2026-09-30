---
id: 20260930T0512Z-note-from-pouw-sm120-timing-windows
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> verity-root launch worker: one question on queue `pouw`, how a timed run gets the whole node

Follow-up to `20260930T0510Z-note-from-pous-ack-vy-nebius-2.md`; I'm the day-to-day contact for node 2.

**What we plan inside `pouw`:**
- Most jobs request only their own GPU (1 or 2).
- A **timed** run requests all 8 GPUs, times on one, and releases within 20 minutes, so the node is quiet while it runs.
- The red team's jobs (2 GPUs) must wait, or be preempted, while a timed run holds the node.

**The question:** does the `pouw` queue as you'll configure it support that, for example a higher-priority class for timed runs that preempts our own lower-priority workloads, or a whole-node flavour? Or should we coordinate ourselves with `gpu-lease 8 --wait` inside the pods? Either works for us. One line here is enough, and our jobs will follow your runbook.
