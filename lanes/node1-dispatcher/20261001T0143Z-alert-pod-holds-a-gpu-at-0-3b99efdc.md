---
id: 20261001T0143Z-alert-pod-holds-a-gpu-at-0-3b99efdc
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 0, pod nd-proofs-bf16-hi-b66b92f676-prover-b-0-2w582, namespace default**, since 2026-10-01T01:30:30Z: Pod default/nd-proofs-bf16-hi-b66b92f676-prover-b-0-2w582 has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
