---
id: 20261001T0043Z-alert-pod-holds-a-gpu-at-0-278e8282
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 3, pod nd-vllm-coverage-8d21722374-gpu-3-t8qkt, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager), since 2026-10-01T00:42:30Z: Pod default/nd-vllm-coverage-8d21722374-gpu-3-t8qkt has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
