---
id: 20261001T0423Z-alert-pod-holds-a-gpu-at-0-014645d6
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 4, pod nd-vllm-epoch-run-b9320d7745-gpu-0-kv82w, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b32__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-01T04:22:30Z: Pod default/nd-vllm-epoch-run-b9320d7745-gpu-0-kv82w has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
