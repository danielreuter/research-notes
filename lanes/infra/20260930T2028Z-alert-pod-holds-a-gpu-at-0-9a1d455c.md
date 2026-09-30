---
id: 20260930T2028Z-alert-pod-holds-a-gpu-at-0-9a1d455c
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 4 firing on vy-nebius-1

- **gpu 1, pod gpu-335-ce1b86e4-head, namespace default** (job cov-m007; lane vllm-epoch-run; row gemma2-2b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager), since 2026-09-30T20:00:30Z: Pod default/gpu-335-ce1b86e4-head has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 3, pod gpu-329-ce1b86e4-head, namespace default** (job cov-m005; lane vllm-epoch-run; row gemma2-2b__bf16__rtxpro6000__tp1__b16__i256__o32__mixed__greedy__bi-eager), since 2026-09-30T19:31:30Z: Pod default/gpu-329-ce1b86e4-head has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 5, pod nd-backend-sweep-9c730cf434-prover-b-0-jf8b8, namespace default**, since 2026-09-30T20:27:30Z: Pod default/nd-backend-sweep-9c730cf434-prover-b-0-jf8b8 has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 7, pod gpu-331-ce1b86e4-head, namespace default** (job cov-m006; lane vllm-epoch-run; row gemma2-2b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager), since 2026-09-30T19:33:30Z: Pod default/gpu-331-ce1b86e4-head has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
