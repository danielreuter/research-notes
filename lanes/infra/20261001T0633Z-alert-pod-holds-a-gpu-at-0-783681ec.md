---
id: 20261001T0633Z-alert-pod-holds-a-gpu-at-0-783681ec
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 3, pod nd-vllm-epoch-run-5d3e9e6936-gpu-0-5flhz, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T06:06:30Z: Pod default/nd-vllm-epoch-run-5d3e9e6936-gpu-0-5flhz has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
