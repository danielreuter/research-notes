---
id: 20261007T0541Z-alert-pod-holds-a-gpu-at-0-8f4a047e
campaign: nebius-monitoring
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: grafana on vy-nebius-1 (alert_sink.py; rules in pods/nebius/monitoring/alerting.yaml)
---

# Pod holds a GPU at 0%: 6 firing on vy-nebius-1

- **gpu 0, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 0 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 1, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 1 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 3, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 3 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 4, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 4 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 6, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 6 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.
- **gpu 7, pod lt-qwen235-tp8-fstr-6-ce1b86e4-head, namespace default** (job lt-qwen235-tp8-fstr), since 2026-10-07T05:40:30Z: Pod default/lt-qwen235-tp8-fstr-6-ce1b86e4-head has held GPU 7 at 0% utilization for 10 minutes: a job holding a GPU through a CPU phase, a lock or a rebuild. CPU stages belong in 0-GPU tasks.

Open http://127.0.0.1:3000 through `ssh -N -L 3000:127.0.0.1:3000 research@81.85.2.165` (Nebius folder).
