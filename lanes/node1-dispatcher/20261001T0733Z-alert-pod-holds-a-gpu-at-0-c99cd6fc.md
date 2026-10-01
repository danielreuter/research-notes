---
id: 20261001T0733Z-alert-pod-holds-a-gpu-at-0-c99cd6fc
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 4 firing on vy-nebius-1

- **gpu 4, pod nd-vllm-epoch-run-5d3e9e6936-gpu-1-gvqqd, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T07:31:30Z: Pod default/nd-vllm-epoch-run-5d3e9e6936-gpu-1-gvqqd has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 5, pod nd-vllm-epoch-run-47a14bf90d-gpu-1-xbsk8, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-01T06:54:30Z: Pod default/nd-vllm-epoch-run-47a14bf90d-gpu-1-xbsk8 has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 6, pod nd-vllm-epoch-run-39bb5ebdf5-gpu-1-l5wv2, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-01T07:26:30Z: Pod default/nd-vllm-epoch-run-39bb5ebdf5-gpu-1-l5wv2 has held GPU 6 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 7, pod nd-vllm-epoch-run-6ab8bfe198-gpu-0-px7hc, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b16__i1024__o128__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T07:31:30Z: Pod default/nd-vllm-epoch-run-6ab8bfe198-gpu-0-px7hc has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
