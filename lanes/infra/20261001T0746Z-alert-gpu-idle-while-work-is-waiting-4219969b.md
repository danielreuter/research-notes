---
id: 20261001T0746Z-alert-gpu-idle-while-work-is-waiting-4219969b
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 4 firing on vy-nebius-1

- **gpu 1**, since 2026-10-01T07:15:30Z: GPU 1 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 1 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 4**, since 2026-10-01T07:15:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 652.8m%) for 15 minutes while 1 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-10-01T07:15:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 1.129%) for 15 minutes while 1 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-10-01T07:15:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 1 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
