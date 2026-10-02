---
id: 20261002T1342Z-alert-pod-holds-a-gpu-at-0-cfca4ec6
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 0, pod nd-vllm-epoch-run-b2c415da25-gpu-0-r2wmh, namespace default** (row llama32-3b__bf16__rtxpro6000__tp1__b32__i1024__o128__mixed__greedy__bi-eager), since 2026-10-02T13:41:30Z: Pod default/nd-vllm-epoch-run-b2c415da25-gpu-0-r2wmh has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 2, pod nd-vllm-epoch-run-a2a16abb9b-gpu-0-hp46z, namespace default** (row gemma2-9b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager), since 2026-10-02T13:41:30Z: Pod default/nd-vllm-epoch-run-a2a16abb9b-gpu-0-hp46z has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
