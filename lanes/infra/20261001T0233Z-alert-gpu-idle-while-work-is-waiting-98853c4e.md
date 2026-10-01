---
id: 20261001T0233Z-alert-gpu-idle-while-work-is-waiting-98853c4e
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 2 firing on vy-nebius-1

- **gpu 3**, since 2026-10-01T02:32:30Z: GPU 3 has been under 5% busy (DCGM engine-active, now 2.779%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 7**, since 2026-10-01T02:32:30Z: GPU 7 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 3 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
