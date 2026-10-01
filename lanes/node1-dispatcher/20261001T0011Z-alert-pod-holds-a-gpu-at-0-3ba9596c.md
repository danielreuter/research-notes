---
id: 20261001T0011Z-alert-pod-holds-a-gpu-at-0-3ba9596c
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 5, pod nd-vllm-coverage-6b81531e17-gpu-1-srbw2, namespace default** (row qwen25-15b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager), since 2026-10-01T00:10:30Z: Pod default/nd-vllm-coverage-6b81531e17-gpu-1-srbw2 has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
