---
id: 20260930T1722Z-alert-gpu-idle-while-work-is-waiting-a0ba189b
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 3 firing on vy-nebius-1

- **gpu 0**, since 2026-09-30T17:17:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 11 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 4**, since 2026-09-30T17:15:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 94m%) for 15 minutes while 11 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-09-30T17:21:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 856.5m%) for 15 minutes while 11 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
