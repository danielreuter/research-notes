---
id: 20260930T2102Z-alert-pod-holds-a-gpu-at-0-e310835a
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 1, pod nd-vllm-epoch-run-1b34389ed9-gpu-0-b7krz, namespace default** (row olmoe-1b-7b__bf16__rtxpro6000__tp1__b16__i256__o32__mixed__greedy__bi-eager), since 2026-09-30T21:01:30Z: Pod default/nd-vllm-epoch-run-1b34389ed9-gpu-0-b7krz has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
