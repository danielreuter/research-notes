---
id: 20261002T2029Z-alert-pod-holds-a-gpu-at-0-6669107b
campaign: nebius-monitoring
lane: node1-dispatcher
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 1 firing on vy-nebius-1

- **gpu 5, pod nd-vllm-epoch-run-a30cbeb768-gpu-0-plz9r, namespace default** (row phi4-14b__bf16__rtxpro6000__tp2__b8__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager), since 2026-10-02T20:28:30Z: Pod default/nd-vllm-epoch-run-a30cbeb768-gpu-0-plz9r has held GPU 5 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
