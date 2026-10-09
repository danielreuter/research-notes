---
id: 20261009T1047Z-alert-node1-disk-guard-hold
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: vy-disk-guard on vy-nebius-1 (pods/nebius/sky/disk_guard.sh)
---

# Disk guard: /workspace is 78% full, so Kueue admits nothing new on vy-nebius-1

- Held at 78% (the mark is 78%): deployments-cpu deployments-gpu provers backfill circuits. Admitted workloads keep running; nothing was deleted.
- The guard releases these queues itself once /workspace is under 75%. To release them by hand: vy-disk-guard release.
