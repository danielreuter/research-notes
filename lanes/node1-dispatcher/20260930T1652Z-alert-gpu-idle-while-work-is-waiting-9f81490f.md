---
id: 20260930T1652Z-alert-gpu-idle-while-work-is-waiting-9f81490f
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 3 firing on vy-nebius-1

- **gpu 1**, since 2026-09-30T16:47:30Z: GPU 1 has been under 5% busy (DCGM engine-active, now 4m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 2**, since 2026-09-30T16:47:30Z: GPU 2 has been under 5% busy (DCGM engine-active, now 545.9m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 3**, since 2026-09-30T16:52:30Z: GPU 3 has been under 5% busy (DCGM engine-active, now 67.5m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
