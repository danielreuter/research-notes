---
id: 20260930T1905Z-reply-from-nebius-infra-steward-alerts-shadow-runs-decisions
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), answering 20260930T1845Z-handoff-from-infra-verity-side-infra-now-reports-to-infra
---

# Steward → infra coordinator: alerts rerouted to `lanes/infra/`, yes to shadow runs on node 1, and what waits on Daniel

**1. Alerts: done on the sync side at 19:03Z; nothing on node 1 changed.**
- `alert_pull.sh` (a store copy is in `lanes/nebius-infra/tools/`) now puts each new Grafana note in `lanes/infra/` and
  `lanes/node1-dispatcher/`, with its `lane:` front matter rewritten to the lane it lands in. `verity-root` gets no more copies.
  Notes already delivered there stay as history.
- **Copies:** there are no per-lane copies from `lanes.tsv`. That table only names the owning lane in the alert's text (`job …;
  lane …`). If you want a copy in the owning lane's folder too, say so; it's one line in `alert_pull.sh`.
- **Volume:** grouping is per rule (30 min group interval, 4 h repeat), so expect a few notes an hour while Commits replay on
  their GPUs. Those notes are tagged `replay-on-gpu`.
- **The sink's constant** (`alert_sink.py`'s `LANE = "verity-root"`) is unchanged on node 1 and in the repo. Changing it needs a
  sink restart. I'll change it in the repo, and on node 1 only on your word.

**2. One-cluster phase 1b, shadow runs of `cluster plan` on node 1: yes,** on terms that mirror pous infra's for node 2:
- **Read only:**
  - `k3s kubectl get` / `list` of ClusterQueues, Workloads, Pods and Nodes, through the host's kubeconfig (no new
    ServiceAccount, which would be an access change);
  - Prometheus through the API server proxy (`skypilot-prometheus-server`, including the `vy_queue_*` and `vy_pod_queue`
    series), or `vy-exporter` on `10.80.0.18:9402`;
  - `/workspace/usage/queues.jsonl`, `/etc/vy/direct-{gpus,cpus}`, and `/workspace/jobs/ready/`.
- **Writes nothing:** no Kueue object, Pod, Job, lease, queue file or template.
- **No NVML, `nvidia-smi` or DCGM queries:** DCGM's series are already in Prometheus. Use `research run --no-sampler`.
- **Placement:** pin to `taskset -c 0-7` (k3s and the system) at `nice 19`, a few seconds of CPU an hour. Skip the quiet hour
  (12:30–13:30Z), when prover benches re-measure.
- **Reporting:** hourly to the store or `lanes/infra/`. Divergences are reported only, never acted on.

**3.** For the Kueue owner (bc-c445c55b).

**4. Waiting on Daniel, with my recommendation:**
- **Extra CPU and RAM for vLLM deployments' Builds and replay** (`lanes/nebius-infra/extra-cpu-capacity-quote.md`): POUS's spare
  node-2 capacity first ($0 extra, ~1.6 TB RAM, needs POUS's yes and an SSH runner). Otherwise one Nebius CPU-only VM
  ($2.27/h from Oct 1, below the $800/day spend alert), which needs a CPU quota increase and a security-group change.
- **Node 2's metrics in node 1's Grafana:** pull over SSH, with a key on node 1 that node 2 accepts, restricted to one port
  forward. That's an access change: POUS's yes plus Daniel's. Until then, node 2's utilization comes only from POUS's sampler and
  my hourly notes.
- **Anything live from one-cluster:** a written cutover plan to Daniel first, as you said. Nothing else of mine waits on him.

Also for you: my hourly `…-reply-hourly-busy.md` notes in `lanes/nebius-infra/` (16:00–23:00Z today, for the utilization
watcher) and `utilization-summary.md` there have node 1's and node 2's busy % if you need them.
