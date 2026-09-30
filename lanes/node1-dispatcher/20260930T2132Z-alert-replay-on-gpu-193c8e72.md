---
id: 20260930T2132Z-alert-replay-on-gpu-193c8e72
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
tags: [replay-on-gpu]
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0% [replay-on-gpu]: 1 firing on vy-nebius-1

These Commits are in `validate.sampled_replay`: the CPU replay runs while the pod still holds its GPU, by design until Daniel rules on moving replay off the GPU. Not a stall, but the GPU counts as idle.

- **gpu 1, pod nd-vllm-epoch-run-f53f4a4305-gpu-0-zkl4w, namespace default** (row qwen3-30b-a3b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager), since 2026-09-30T21:20:30Z: Pod default/nd-vllm-epoch-run-f53f4a4305-gpu-0-zkl4w has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
