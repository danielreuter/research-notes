---
id: 20261001T0833Z-alert-pod-holds-a-gpu-at-0-cf92da70
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 2, pod nd-n2-build-60246dc74c-gpu-0-cm4zj, namespace default** (row qwen3-30b-a3b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-01T08:29:30Z: Pod default/nd-n2-build-60246dc74c-gpu-0-cm4zj has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 4, pod nd-vllm-epoch-run-5d3e9e6936-gpu-1-gvqqd, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T08:28:30Z: Pod default/nd-vllm-epoch-run-5d3e9e6936-gpu-1-gvqqd has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
