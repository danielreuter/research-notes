---
id: 20261006T0917Z-alert-pod-holds-a-gpu-at-0-f376566c
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 7, pod gpu-pool-1791277469063-9xhlp, namespace default**, since 2026-10-06T09:16:30Z: Pod default/gpu-pool-1791277469063-9xhlp has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
