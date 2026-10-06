---
id: 20261006T2144Z-alert-pod-holds-a-gpu-at-0-e45930d9
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 1, pod gpu-pool-1791322333822-th9hj, namespace default**, since 2026-10-06T21:43:30Z: Pod default/gpu-pool-1791322333822-th9hj has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 6, pod gpu-pool-1791322333823-bmfcz, namespace default**, since 2026-10-06T21:43:30Z: Pod default/gpu-pool-1791322333823-bmfcz has held GPU 6 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
