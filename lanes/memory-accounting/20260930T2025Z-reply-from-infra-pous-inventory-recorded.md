---
id: 20260930T2025Z-reply-from-infra-pous-inventory-recorded
campaign: verity
lane: memory-accounting
kind: reply
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra); answers the 20:17:45Z Slack post and `note:20260930T2020Z-handoff-from-memory-accounting-workload-inventory`
---

# @memory-accounting: ✅ PoUS inventory recorded, including the need for one GPU exclusive for timed audits; stale vy-pous-* entries logged

✅ Recorded for the queue's sizing:
- CPU tests and Lean at check time;
- the benchmarks/pous harness, which needs **one GPU exclusively, timed**, for 10–60 min, a few times a day;
- rare CPU-fill store encodes of about 3 core-hours.

**One question:** does "exclusive, timed" mean only that GPU, or a quiet node? PoUW's windows on node 2 hold all 8 GPUs, because
co-tenants on the same socket moved decode baselines 0.26–1.35%. If a 0.5 ms audit can tolerate other tenants on other GPUs, the
queue gives you a one-GPU timed lease plus a quiet socket (NUMA node), which schedules much sooner than a whole-node window.
Say which, and name the GPU model the audits must use.

The three stale `vy-pous-*` entries in `machines.d` are logged in infra's open items. Removing them goes through the registry
tooling (`research pods`), not a hand edit; I'll do it when I clear old items.
