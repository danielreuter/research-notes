---
id: 20260930T1547Z-alert-pod-holds-a-gpu-at-0-9aef9128
campaign: nebius-monitoring
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 5, pod gpu-209-ce1b86e4-head, namespace default**, since 2026-09-30T15:46:30Z: Pod default/gpu-209-ce1b86e4-head has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
