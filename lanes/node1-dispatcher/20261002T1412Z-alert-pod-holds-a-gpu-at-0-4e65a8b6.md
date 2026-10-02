---
id: 20261002T1412Z-alert-pod-holds-a-gpu-at-0-4e65a8b6
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 1, pod nd-vllm-epoch-run-860fe20352-gpu-0-rj5bm, namespace default** (row gemma2-9b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-02T14:05:30Z: Pod default/nd-vllm-epoch-run-860fe20352-gpu-0-rj5bm has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
