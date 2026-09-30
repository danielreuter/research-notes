---
id: 20260930T1837Z-alert-gpu-idle-while-work-is-waiting-4e22948a
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 3 firing on vy-nebius-1

- **gpu 0**, since 2026-09-30T18:06:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 320.8m%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-09-30T18:29:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-09-30T18:23:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 22.9m%) for 15 minutes while 5 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
