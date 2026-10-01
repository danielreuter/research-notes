---
id: 20261001T2040Z-alert-pod-holds-a-gpu-at-0-a10a650f
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 4, pod nd-commit-pack-e8aca18ca5-commit-p-0-6x49k, namespace default** (row r1-distill-qwen-15b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-01T20:39:30Z: Pod default/nd-commit-pack-e8aca18ca5-commit-p-0-6x49k has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
