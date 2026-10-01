---
id: 20261001T0531Z-alert-pod-holds-a-gpu-at-0-ede86b37
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 2, pod nd-vllm-epoch-run-60b6b0d165-gpu-0-vg7gn, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b16__i256__o32__mixed__greedy__bi-eager), since 2026-10-01T05:21:30Z: Pod default/nd-vllm-epoch-run-60b6b0d165-gpu-0-vg7gn has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 5, pod nd-vllm-epoch-run-40af3b802b-gpu-0-w9fpw, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b32__i256__o32__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T05:26:30Z: Pod default/nd-vllm-epoch-run-40af3b802b-gpu-0-w9fpw has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
