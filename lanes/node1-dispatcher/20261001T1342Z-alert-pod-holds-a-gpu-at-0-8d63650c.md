---
id: 20261001T1342Z-alert-pod-holds-a-gpu-at-0-8d63650c
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 4, pod nd-vllm-epoch-run-43492a457e-gpu-0-xkr8d, namespace default** (row qwen3-06b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-01T13:41:30Z: Pod default/nd-vllm-epoch-run-43492a457e-gpu-0-xkr8d has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
