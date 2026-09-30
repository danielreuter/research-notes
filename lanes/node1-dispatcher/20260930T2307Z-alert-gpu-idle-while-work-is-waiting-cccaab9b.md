---
id: 20260930T2307Z-alert-gpu-idle-while-work-is-waiting-cccaab9b
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 2 firing on vy-nebius-1

- **gpu 4**, since 2026-09-30T23:07:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 19 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-09-30T22:51:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 19 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
