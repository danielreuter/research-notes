---
id: 20260930T2237Z-alert-gpu-idle-while-work-is-waiting-6068ef48
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 2 firing on vy-nebius-1

- **gpu 2**, since 2026-09-30T22:36:30Z: GPU 2 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 28 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.
- **gpu 6**, since 2026-09-30T22:37:30Z: GPU 6 has been under 5% busy (DCGM engine-active, now 1.02%) for 15 minutes while 28 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
