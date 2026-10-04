---
id: 20261004T0707Z-alert-pod-holds-a-gpu-at-0-7b0ac5e9
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 2, pod gpu-pool-1791096899979-6cbqf, namespace default**, since 2026-10-04T07:06:30Z: Pod default/gpu-pool-1791096899979-6cbqf has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
