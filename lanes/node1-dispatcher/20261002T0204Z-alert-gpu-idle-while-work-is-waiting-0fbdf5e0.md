---
id: 20261002T0204Z-alert-gpu-idle-while-work-is-waiting-0fbdf5e0
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 3 firing on vy-nebius-1

- **gpu 4**, since 2026-10-02T01:40:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 6 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-10-02T01:36:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 6 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-10-02T01:49:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 6 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
