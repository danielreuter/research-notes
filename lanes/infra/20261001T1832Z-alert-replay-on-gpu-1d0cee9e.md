---
id: 20261001T1832Z-alert-replay-on-gpu-1d0cee9e
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

- **gpu 0, pod nd-commit-pack-4688c6d29c-commit-p-0-k9d6l, namespace default** (row r1-distill-qwen-15b__bf16__rtxpro6000__tp1__b8__i1024__o128__mixed__greedy__bi-eager), since 2026-10-01T18:31:30Z: Pod default/nd-commit-pack-4688c6d29c-commit-p-0-k9d6l has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
