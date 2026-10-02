---
id: 20261002T0811Z-alert-pod-holds-a-gpu-at-0-9a042be3
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 2, pod nd-proofs-vllm-mo-6a134c680c-prover-b-0-wjqkd, namespace default**, since 2026-10-02T08:10:30Z: Pod default/nd-proofs-vllm-mo-6a134c680c-prover-b-0-wjqkd has held GPU 2 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
