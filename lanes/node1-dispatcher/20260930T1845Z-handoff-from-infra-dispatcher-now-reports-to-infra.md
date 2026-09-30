---
id: 20260930T1845Z-handoff-from-infra-dispatcher-now-reports-to-infra
campaign: verity
lane: node1-dispatcher
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b)
---

# node1-dispatcher now reports to the infra coordinator; the GPU-idle alerts are yours to act on

For node 1's dispatcher (bc-70706bc3). In Daniel's new Project, infra, a fresh coordinator (me), takes over node1-dispatcher from
the research coordinator (`note:20260930T1730Z-reply-from-verity-root-project-restructure`). Write to `lanes/infra/` when you're
blocked or need a decision. Everything else stays in your checkpoints.

- **Alerts:** the "GPU idle while work is waiting" and "pod holds a GPU at 0%" alerts on vy-nebius-1 are yours to act on. The
  latest are 18:37Z (GPUs 0, 5 and 7 under 5% with 5 workloads waiting) and 18:28Z (a replay on a GPU). I've asked the steward to
  route them to `lanes/infra/` as well as to your copy.
- **What I need:** one line in `lanes/infra/` saying why GPUs idle while work waits, if it isn't the known cause. The known cause is
  the quota rules keeping the backfill tier from borrowing (`note:20260930T1722Z-reply-from-verity-root-to-pous-one-cluster` §7).
  Also say whether a Kueue quota change would fix it. That change needs a written plan to Daniel, and I carry it.
- No new rules: never print secrets, and no live-node change without a written plan.
