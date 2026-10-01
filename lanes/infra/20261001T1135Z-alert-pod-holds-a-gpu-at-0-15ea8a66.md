---
id: 20261001T1135Z-alert-pod-holds-a-gpu-at-0-15ea8a66
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 4, pod nd-vllm-epoch-run-f145b4a191-gpu-0-cf7xm, namespace default** (row gemma2-2b__bf16__rtxpro6000__tp1__b64__i1024__o128__mixed__stoch-t0.8-p1__bi-eager), since 2026-10-01T10:34:30Z: Pod default/nd-vllm-epoch-run-f145b4a191-gpu-0-cf7xm has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
