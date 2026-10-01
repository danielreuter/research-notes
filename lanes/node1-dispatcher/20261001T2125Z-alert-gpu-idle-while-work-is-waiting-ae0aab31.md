---
id: 20261001T2125Z-alert-gpu-idle-while-work-is-waiting-ae0aab31
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 4 firing on vy-nebius-1

- **gpu 0**, since 2026-10-01T21:15:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 3**, since 2026-10-01T20:54:30Z: GPU 3 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 4**, since 2026-10-01T20:54:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-10-01T21:14:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
