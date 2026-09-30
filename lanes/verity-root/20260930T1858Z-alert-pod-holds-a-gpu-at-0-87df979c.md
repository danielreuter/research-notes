---
id: 20260930T1858Z-alert-pod-holds-a-gpu-at-0-87df979c
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 4, pod gpu-326-ce1b86e4-head, namespace default** (job cov-k06-6; lane vllm-epoch-run; row gemma2-2b__bf16__rtxpro6000__tp1__b1__i256__o15__mixed__greedy__bi-eager), since 2026-09-30T18:57:30Z: Pod default/gpu-326-ce1b86e4-head has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
