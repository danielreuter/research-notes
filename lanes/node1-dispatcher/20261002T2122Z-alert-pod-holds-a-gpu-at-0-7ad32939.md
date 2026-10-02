---
id: 20261002T2122Z-alert-pod-holds-a-gpu-at-0-7ad32939
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 0, pod nd-vllm-epoch-run-a04d1f2855-gpu-0-6tqkc, namespace default** (row phi4-14b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-02T21:21:30Z: Pod default/nd-vllm-epoch-run-a04d1f2855-gpu-0-6tqkc has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 3, pod nd-vllm-epoch-run-a04d1f2855-gpu-0-6tqkc, namespace default** (row phi4-14b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-02T21:22:30Z: Pod default/nd-vllm-epoch-run-a04d1f2855-gpu-0-6tqkc has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
