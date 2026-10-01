---
id: 20261001T2155Z-alert-gpu-idle-while-work-is-waiting-334ba6bd
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 6 firing on vy-nebius-1

- **gpu 0**, since 2026-10-01T21:49:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 1**, since 2026-10-01T21:26:30Z: GPU 1 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 2**, since 2026-10-01T21:30:30Z: GPU 2 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 4**, since 2026-10-01T20:54:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-10-01T21:28:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-10-01T21:14:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
