---
id: 20261002T0932Z-alert-pod-holds-a-gpu-at-0-38c797b8
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 5, pod nd-proofs-vllm-de-090d0c8beb-prover-b-0-626f2, namespace default**, since 2026-10-02T09:09:30Z: Pod default/nd-proofs-vllm-de-090d0c8beb-prover-b-0-626f2 has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
