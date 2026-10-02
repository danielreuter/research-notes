---
id: 20261002T0902Z-alert-pod-holds-a-gpu-at-0-b06a661c
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 0, pod nd-proofs-bf16-hi-3a6896abf2-prover-b-0-sf6s9, namespace default**, since 2026-10-02T09:01:30Z: Pod default/nd-proofs-bf16-hi-3a6896abf2-prover-b-0-sf6s9 has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
