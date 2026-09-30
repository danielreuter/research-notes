---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# GPU monitoring practice for the Nebius servers: research findings and what we took from them

Research by [GPU monitoring practice research](bc-9d71f99b-0d2f-5336-ab59-4a900d74b9d0), 16:01Z, Sep 30. The Grafana-specific
lessons are in `grafana-tutorial-lessons.md` beside this file. The stack described is in `infra/nebius`
`pods/nebius/monitoring/`.

## Where our stack stands against the recommendations (16:05Z)

**Already done:**
- **Profiling fields:** node 1's exporter reports them (`DCGM_FI_PROF_GR_ENGINE_ACTIVE`, `PIPE_TENSOR_ACTIVE`, `DRAM_ACTIVE`).
  `SM_ACTIVE` (1002) is not in the default set.
- **Double scrape:** DCGM is scraped twice, through Services `dcgm-exporter` and `nvidia-dcgm-exporter`. Every query and rule
  filters `service="nvidia-dcgm-exporter"`. The pod label arrives as `pod` (checked: there is no `exported_pod`).
- **Pod → queue join:** comes from our own exporter (`vy_pod_queue`), not from `kube_pod_labels`, which lacks the Kueue label. It
  needs no RBAC token, unlike Kueue's HTTPS metrics endpoint.
- **Alerts:** the idle rules and the webhook → markdown receiver are live. The 30 min grouping and the quiet-hour mute are on a
  child policy.
- **Data source:** `timeInterval: 60s` is set.

**Next, and cheap:**
- `keep_firing_for` (about 5 min) on both rules, so a brief kernel recompile doesn't resolve and re-fire an alert.
- A watchdog: an always-firing rule plus a heartbeat file, so a silent monitoring stack gets noticed.
- A daily digest of held vs busy GPU-hours per queue and pod: the "43 vs 1" number, tracked.
- `root_url = http://localhost:3000/`, so links in the alert notes work through the tunnel.
- `DatasourceError` / `DatasourceNoData` routed explicitly.
- A state-timeline panel per GPU: busy, held-idle, unallocated-idle.

**Later:**
- **A custom DCGM metrics CSV:** `SM_ACTIVE`, clock-event reasons (field 112), XID totals, and a 10 s collection interval. A custom
  CSV replaces the default list, so start from `default-counters.csv`.
- **Measurements first:** profiling overhead on the provers, and whether `ncu` runs alongside DCGM on GB202. The research found
  both unverified.
- **Kueue's native metrics:** preemptions, evictions and admission wait. They need RBAC for a scrape token, which is a credential
  decision.
- **Node 2:** see below. It needs POUS and an access decision.

**Skip:** Pushgateway, federation, Thanos or Mimir, per-process labels, chat or email integrations.

## Node 2

Only TCP 22 is open between the servers (measured 15:12Z: port 9100 on 10.80.0.42 times out from node 1). The recommended
pattern is to pull, not push:
- **On node 2:** a textfile or a tiny standard-library exporter built from POUS's 10 s sampler JSONL. It adds no NVML polling.
- **On node 1:** a persistent `ssh -N -L <node1 private IP>:19402:127.0.0.1:<port> node2` (autossh-style, `Restart=always`),
  scraped as a static target, with alerts on `up == 0` and on sampler staleness.
- **The access this needs:** node 1 has to hold a key that node 2 accepts, restricted to that one forward. That's an access change
  on POUS's server, so it goes to POUS and root first.

---

## The research report (verbatim)

### Summary

Keep dcgm-exporter → SkyPilot's Prometheus → Grafana; add recording rules that every chart and alert reads, a Kueue scrape job,
a pull-scrape of node 2 through an SSH local forward, and Alertmanager (or Grafana alerting) posting to a local webhook that writes
markdown. Before anything else, confirm DCP profiling fields actually report on these Blackwell cards (older exporter images drop
them silently: dcgm-exporter issue #707; fixed from 4.5.3-4.8.2, GPU Operator 26.3.2+).

### 1. GPU metrics on the RTX PRO 6000 Blackwell

- **Metrics:**
  - `DCGM_FI_DEV_GPU_UTIL` is the idle detector: 0 means idle, but it overstates how busy a GPU is.
  - `DCGM_FI_PROF_GR_ENGINE_ACTIVE` (on by default), plus `DCGM_FI_PROF_SM_ACTIVE`, measures how busy. NVIDIA: ≥ 0.8 is necessary
    for efficient use, and below 0.5 likely means ineffective use.
  - Clock-event reasons (field 112) are for the noise-sensitive provers.
  - `DCGM_EXPORTER_INTERVAL=10000` changes the collection interval (default 30 s).
- **Pitfalls:**
  - A custom CSV replaces the whole default list.
  - Before Hopper, DCGM profiling holds a driver-wide lock and `ncu` fails. Whether GB202 uses the GPM path is unverified.
  - The only overhead measurement found is on A100: under 1% end-to-end.
  - dcgm-exporter 4.8.3 renamed `Hostname` to `hostname`, so pin the version.
- **Others:** GKE treats the profiling fields as the real utilization metrics. Azure reads utilization with memory and power.
  Modal runs passive health checks plus XIDs, and regrets aggregating per container, which hid one bad GPU in eight.

### 2. Kueue

- `metrics.enableClusterQueueResources: true` enables the quota series.
- Metrics are served over HTTPS on 8443 and check the caller's token, so bind `kueue-metrics-reader` to Prometheus's
  ServiceAccount.
- Chart usage vs nominal, borrowing, pending by status, and preemptions and evictions by reason. For non-checkpointable
  `circuits`, `kueue_evicted_workloads_total{reason="Preempted"}` counts lost work.
- Pitfalls:
  - Kueue counts a GPU from admission, dcgm-exporter from when a container holds it; the gap between them is a panel of its own.
  - Pods carry the LocalQueue name, not the ClusterQueue name.

### 3. Attribution

- DCGM adds `pod` and `namespace` labels to the series of any GPU a pod holds. Join to `kube_pod_labels` with
  `--metric-labels-allowlist=pods=[kueue.x-k8s.io/queue-name,skypilot-cluster-name]` (SkyPilot's guide does this), in one recording
  rule.
- Pitfalls:
  - `exported_` label collisions with `honor_labels: false`.
  - Double scrapes.
  - Processes outside Kubernetes show as unallocated but busy.

### 4. Idle alerts as markdown files

- **Rules:** `for: 10m` with `keep_firing_for: 2m`.
- **Receiver:** a standard-library webhook receiver writing one file per alert fingerprint, and appending "resolved at" when it
  resolves. Include the pod's CPU at alert time: high CPU with an idle GPU means a CPU phase, and both low means a lock wait.
- **Heartbeat:** a Watchdog alert touches a heartbeat file, and a cron job writes `MonitoringDown.md` if it goes stale.
- **Daily digest:** held vs busy GPU-hours per queue.
- **Thresholds:** first-hand policies use windows of hours (Princeton's Job Defense Shield defaults to 120 min). Evidence for
  10-minute thresholds is thin, so expect volume.
- **Actionable only with work:** an unallocated idle GPU is actionable only while Kueue has pending admissible work.

### 5. Dashboards

Keep 12239 and 1860. Add one dashboard, provisioned from a file, that reads only the recording rules:
- a state timeline per GPU across both nodes;
- held vs busy GPU-hours per queue;
- Kueue usage vs nominal, with borrowing;
- pending and admitted workloads;
- preemptions by reason;
- per-pod CPU with GPU busy overlaid.

CoreWeave counts a node as busy only when every GPU is at least 50% active.

### 6. Months

- Dashboards and alerts read only `gpu:*` and `pod:*` recording rules, so a renamed exporter field touches one rule.
- Keep everything in git.
- Prometheus stores about 1–2 bytes per sample. The 43 GB size cap, not the 1000-day setting, bounds retention: an estimated
  10–40 GB a year.
- The history lives in the SkyPilot release's PersistentVolumeClaim, so check its reclaim policy before any reinstall.

### 7. Node 2 over SSH only

- **Pull:**
  - Node 2 writes `gpu.prom` atomically, with `Hostname`, `gpu`, `UUID` and `holder` labels plus a sampler-timestamp gauge.
  - It's served on node 2's `127.0.0.1`, either by node-exporter or by a 30-line standard-library server.
  - Node 1 runs `ssh -N -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes -L <node1-ip>:19100:127.0.0.1:9100 node2`
    as a systemd service with `Restart=always`, scraped as a static target.
- **Alerts:** `up{job="node2"} == 0`, and staleness over 60 s.
- **If gaps matter:** Prometheus agent mode on node 2 remote-writing through the tunnel (it buffers about 2 h), or a `promtool`
  backfill from the JSONL.
- **Avoid Pushgateway:** no `up` signal, and stale series linger.

### Unverified or thin

- GB202's GPM path, and whether Nsight coexists with DCGM profiling.
- Profiling overhead on Blackwell.
- The `exported_` labels on our scrape job.
- 10-minute idle thresholds.
- The storage estimate.

### Sources (from the report)

1. [dcgm-exporter issue #707](https://github.com/NVIDIA/dcgm-exporter/issues/707) ·
   [DCGM changelog](https://docs.nvidia.com/datacenter/dcgm/latest/release-notes/changelog.html) ·
   [GPU Operator platform support](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/platform-support.html) ·
   [dcgm-exporter releases](https://github.com/NVIDIA/dcgm-exporter/releases) ·
   [default-counters.csv](https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/etc/default-counters.csv)
2. [DCGM profiling module](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html) ·
   [DCGM field identifiers](https://docs.nvidia.com/datacenter/dcgm/latest/reference/field-identifiers.html) ·
   [installing dcgm-exporter](https://docs.nvidia.com/datacenter/dcgm/latest/installation/install-dcgm-exporter.html)
3. [DCGM issue #56](https://github.com/NVIDIA/DCGM/issues/56) ·
   [OSC: Nsight vs DCGM](https://www.osc.edu/resources/technical_support/known_issues/nsight_gpu_profiler_not_working_due_to_dcgm_conflict) ·
   [NERSC profiling tools](https://docs.nersc.gov/tools/performance/nvidiaproftools/) ·
   [Nsight Operator troubleshooting](https://docs.nvidia.com/nsight-operator/Troubleshooting/index.html) ·
   [NVML GPM functions](https://docs.nvidia.com/deploy/nvml-api/group__nvmlGpmFunctions.html) ·
   [A100 overhead paper](https://itu-dasyalab.github.io/RAD/publication/papers/euromlsys2023.pdf)
4. [GKE DCGM metrics](https://cloud.google.com/kubernetes-engine/docs/how-to/dcgm-metrics) ·
   [AKS GPU observability](https://learn.microsoft.com/en-us/azure/aks/best-practices-gpu-observability) ·
   [Modal: GPU health](https://modal.com/blog/gpu-health)
5. [Kueue metrics](https://kueue.sigs.k8s.io/docs/reference/metrics/) ·
   [Kueue Prometheus setup](https://kueue.sigs.k8s.io/v0.19/docs/tasks/manage/observability/setup_prometheus/) ·
   [common Grafana queries](https://kueue.sigs.k8s.io/docs/tasks/manage/observability/common_grafana_queries/) ·
   [pending workloads in Grafana](https://kueue.sigs.k8s.io/docs/tasks/manage/monitor_pending_workloads/pending_workloads_in_grafana/)
6. [SkyPilot Kueue example](https://docs.skypilot.ai/en/latest/reference/kubernetes/examples/kueue-example.html) ·
   [SkyPilot GPU metrics setup](https://docs.skypilot.ai/en/latest/reference/api-server/examples/api-server-gpu-metrics-setup.html) ·
   [cast.ai GPU cost monitoring](https://cast.ai/blog/gpu-cost-monitoring-kubernetes/)
7. [Princeton Jobstats](https://princetonuniversity.github.io/jobstats/setup/gpu_node_scripts/) ·
   [Job Defense Shield](https://princetonuniversity.github.io/job_defense_shield/alert/zero_gpu_util/) ·
   [Uber: Ray on Kubernetes](https://www.uber.com/us/en/blog/ubers-journey-to-ray-on-kubernetes-resource-management/) ·
   [CoreWeave training-job panels](https://docs.coreweave.com/observability/managed-grafana/kubernetes/training-jobs)
8. [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/) ·
   [Prometheus: when to push](https://prometheus.io/docs/practices/pushing/) ·
   [Prometheus agent](https://github.com/prometheus/prometheus/blob/main/docs/prometheus_agent.md) ·
   [Grafana 12.4 contact points](https://grafana.com/docs/grafana/v12.4/alerting/configure-notifications/manage-contact-points/) ·
   [Run:ai GPU profiling metrics](https://run-ai-docs.nvidia.com/saas/platform-management/monitor-performance/gpu-profiling-metrics.md)
