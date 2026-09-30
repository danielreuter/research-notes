---
id: 20260930T2128Z-handoff-from-infra-idle-and-unleased-monitors
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node2-ops: two monitors on node 2 tonight: a GPU leased but idle, and a GPU process nobody leased

Daniel wants monitoring to keep jobs honest about their resources. Tonight, in `node_ops.py` or a sibling, alerting through
`alerts.jsonl` as now:
1. **Leased but idle:** a lease whose GPU sits under 10% busy (from the sampler) for more than 5 minutes, outside a timed window. The
   alert names the holder, the lease's `who` and the job. Relay it to the owning coordinator as you do other alerts.
2. **Unleased:** any compute process on a GPU (`nvidia-smi --query-compute-apps`, at most once a minute, and never in a window) whose
   pid isn't under a `gpu-lease` scope or a fill scope. The alert gives its user, command and GPU.
3. **Daily wasters:** add an idle-GPU-h line per holder to the hourly report, so infra can post the top 3 wasters once a day.

Commit, then deploy. No NVML inside windows, which you already enforce.
