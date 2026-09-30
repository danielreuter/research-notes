---
id: 20260930T2207Z-alert-gpu-idle-while-work-is-waiting-ebe703a0
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# GPU idle while work is waiting: 1 firing on vy-nebius-1

- **gpu 2**, since 2026-09-30T21:08:30Z: GPU 2 has been under 5% busy (DCGM engine-active, now 0%) for 15 minutes while 34 Kueue workloads or ready jobs wait. The dispatcher refills the queue; root checks after 30 minutes.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
