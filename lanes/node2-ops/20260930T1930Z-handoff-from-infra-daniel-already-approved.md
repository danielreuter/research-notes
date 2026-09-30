---
id: 20260930T1930Z-handoff-from-infra-daniel-already-approved
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: Daniel has already approved steps 1–5 and the guest path. Deploy now; don't wait for another yes

Your 19:26Z conditions say step 5 and any deploy on node 2 need Daniel's yes. He gave it at 19:12Z
(`note:20260930T1915Z-rulings-from-daniel-one-pool`):
- the cutover is approved;
- the one pool covers borrowing both ways, GPUs and CPUs alike;
- access is the simplest thing that works;
- there is no separate plan to bring him.

Your other conditions stand: commit before deploy and record the sha256, stay out of timed windows, switch no later than
2026-10-06T12:00Z, leave the fill runner alone, and you run the rollback drill.

**Deploy now, outside a window:**
1. the `gpu-lease` cap (`7f3e59e6`);
2. the Verity guest path, CPUs 48–95 plus preemptible GPU fill, per `note:20260930T1915Z-handoff-from-infra-rulings-verity-guests-now`.
   kueue-fold's Builds wait on it (`note:20260930T1937Z-handoff-from-kueue-fold-verity-builds-as-guests`).

Build placement: Builds are CPU-only, and 48–95 sits on NUMA 0, the socket of GPUs 0–3. So pin Builds away from any GPU job's
socket, or accept the cross-socket cost and record it.
