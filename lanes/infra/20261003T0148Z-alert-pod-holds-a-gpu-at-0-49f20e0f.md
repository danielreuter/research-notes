---
id: 20261003T0148Z-alert-pod-holds-a-gpu-at-0-49f20e0f
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 1, pod nd-vllm-epoch-run-5827e71d8e-gpu-0-4466f, namespace default** (row qwen3-14b__bf16__rtxpro6000__tp2__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-03T01:47:30Z: Pod default/nd-vllm-epoch-run-5827e71d8e-gpu-0-4466f has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 2, pod nd-vllm-epoch-run-5827e71d8e-gpu-0-4466f, namespace default** (row qwen3-14b__bf16__rtxpro6000__tp2__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-03T01:47:30Z: Pod default/nd-vllm-epoch-run-5827e71d8e-gpu-0-4466f has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
