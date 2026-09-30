---
id: 20260930T1650Z-alert-pod-holds-a-gpu-at-0-a59a8015
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 1, pod gpu-248-ce1b86e4-head, namespace default** (job cov-g246; lane vllm-epoch-run; row smollm2-135m__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-09-30T16:49:30Z: Pod default/gpu-248-ce1b86e4-head has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 7, pod m0-v3-a16b-270-ce1b86e4-head, namespace default** (job m0-v3-a16b; lane flock-netlist (M0)), since 2026-09-30T16:49:30Z: Pod default/m0-v3-a16b-270-ce1b86e4-head has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
