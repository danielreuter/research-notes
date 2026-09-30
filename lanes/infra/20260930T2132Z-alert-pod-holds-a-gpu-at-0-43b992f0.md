---
id: 20260930T2132Z-alert-pod-holds-a-gpu-at-0-43b992f0
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 2 firing on vy-nebius-1

- **gpu 3, pod nd-backend-sweep-495608b1bf-prover-b-0-sd2j4, namespace default**, since 2026-09-30T21:17:30Z: Pod default/nd-backend-sweep-495608b1bf-prover-b-0-sd2j4 has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 7, pod nd-backend-sweep-67601a9291-prover-b-0-c9t9l, namespace default**, since 2026-09-30T21:30:30Z: Pod default/nd-backend-sweep-67601a9291-prover-b-0-c9t9l has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
