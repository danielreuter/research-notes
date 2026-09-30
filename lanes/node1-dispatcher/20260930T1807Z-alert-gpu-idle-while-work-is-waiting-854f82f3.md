---
id: 20260930T1807Z-alert-gpu-idle-while-work-is-waiting-854f82f3
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 5 firing on vy-nebius-1

- **gpu 0**, since 2026-09-30T18:06:30Z: GPU 0 has been under 5% busy (DCGM engine-active, now 4.164%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 2**, since 2026-09-30T18:06:30Z: GPU 2 has been under 5% busy (DCGM engine-active, now 672.2m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 5**, since 2026-09-30T18:06:30Z: GPU 5 has been under 5% busy (DCGM engine-active, now 795.5m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-09-30T18:06:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 65.4m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-09-30T18:06:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 507.2m%) for 15 minutes while 15 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
