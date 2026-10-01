---
id: 20261001T0501Z-alert-pod-holds-a-gpu-at-0-d76930ba
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 5, pod nd-vllm-epoch-run-ce773b421d-gpu-0-wq4kc, namespace default** (row olmoe-1b-7b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__greedy__bi-eager), since 2026-10-01T05:00:30Z: Pod default/nd-vllm-epoch-run-ce773b421d-gpu-0-wq4kc has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 6, pod nd-vllm-epoch-run-ce773b421d-gpu-0-wq4kc, namespace default** (row olmoe-1b-7b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__greedy__bi-eager), since 2026-10-01T05:00:30Z: Pod default/nd-vllm-epoch-run-ce773b421d-gpu-0-wq4kc has held GPU 6 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
