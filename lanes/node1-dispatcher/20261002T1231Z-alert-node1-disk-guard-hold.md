---
id: 20261002T1231Z-alert-node1-disk-guard-hold
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: vy-disk-guard on vy-nebius-1 (pods/nebius/sky/disk_guard.sh)
---

# Disk guard: /workspace is 80% full, so Kueue admits nothing new on vy-nebius-1

- Held at 80% (the mark is 80%): provers backfill. Admitted workloads keep running; nothing was deleted.
- The guard releases these queues itself once /workspace is under 75%. To release them by hand: vy-disk-guard release.
