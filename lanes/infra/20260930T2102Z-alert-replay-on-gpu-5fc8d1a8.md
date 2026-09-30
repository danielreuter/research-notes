---
id: 20260930T2102Z-alert-replay-on-gpu-5fc8d1a8
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
tags: [replay-on-gpu]
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0% [replay-on-gpu]: 1 firing on vy-nebius-1

These Commits are in `validate.sampled_replay`: the CPU replay runs while the pod still holds its GPU, by design until Daniel rules on moving replay off the GPU. Not a stall, but the GPU counts as idle.

- **gpu 2, pod gpu-316-ce1b86e4-head, namespace default** (job cov-g206; lane vllm-epoch-run; row qwen3-30b-a3b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-09-30T21:01:30Z: Pod default/gpu-316-ce1b86e4-head has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
