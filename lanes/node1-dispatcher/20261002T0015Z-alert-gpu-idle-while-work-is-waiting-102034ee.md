---
id: 20261002T0015Z-alert-gpu-idle-while-work-is-waiting-102034ee
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 6 firing on vy-nebius-1

- **gpu 0**, since 2026-10-02T00:14:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 3**, since 2026-10-02T00:14:30Z: GPU 3 has been under 5% busy (DCGM engine-active, now 11.2m%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 4**, since 2026-10-02T00:14:30Z: GPU 4 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-10-02T00:14:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 204.2m%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-10-02T00:14:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 1.102%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-10-02T00:14:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
