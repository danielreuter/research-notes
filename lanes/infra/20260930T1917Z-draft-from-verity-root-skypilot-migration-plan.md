---
id: 20260930T1917Z-draft-from-verity-root-skypilot-migration-plan
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: verity-root
---

> Copy of verity-root's `docs/skypilot-migration-plan.md`, posted for infra on request
> (`note:20260930T1905Z-handoff-from-infra-alert-sink-one-change-and-docs`). Links of the form
> `/cursor/stores/bc-36415049-…/docs/X.md` point into verity-root's store; ask verity-root for any you need.

---
cursor:
  subagentId: "bc-8b690dd6-3bc8-526d-a047-80506d6fecd8"
---

# Moving compute to SkyPilot: one standing RTX PRO 6000 cluster

**For:** Daniel. **Written:** Tue Sep 29, about 7:55 PM PT, by the SkyPilot trial worker. **It builds on:**
- the [hands-on trial](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/compute-layer-evaluation.md) (about $0.14 spent);
- the final spec in [compute utilization](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/compute-utilization.md);
- the merge-queue and website inventories in `internal/skypilot-migration/`.

## Decisions for you

| # | Decision | Recommendation |
|---|---|---|
| 1 | **Approve the spec and open the Nebius account now** | **Approve** 32× RTX PRO 6000 as four 8-GPU servers, in one Nebius managed-Kubernetes cluster in `us-central1`, on demand. Steady state is **$60.15/h ($43.9k/month)**, reached on the ramp 16× → 24× (BF16) → 32× (FP8), with about $40k for the first 30 days. **Then:** create the account on a Mercury card and add one service-account key for us as a Cursor secret. We file the quota request (32 `gpu-rtx6000` GPUs), run the capacity check and ask for a commitment quote. If the cap stays at $50/h, stop at 24×. |
| 2 | **Who holds the RunPod key** | **Only the SkyPilot API server**, as a Kubernetes Secret. With our patch and `runpod: remote_identity: NO_UPLOAD` set for the whole server, no pod gets it. This replaces "only Vercel holds the RunPod key", and the spend broker is dropped. We send the patch upstream. |
| 3 | **The RunPod lines** | **Three lines:**<br>• **the interim vLLM line** on L40S/H100 at **$150/day**, which closes about day 10, after the port's FP8 re-baseline;<br>• **PoUS timed runs** on exclusive RTX 4090s with local NVMe;<br>• **captures**, about $0.5/h together with PoUS.<br>Today's other RunPod lines close as their work moves. |
| 4 | **The site's job queue** | **Keep `/api/jobs` as the list of work, the dedupe key and the event log.** Retire its claim, lease and renew routes once an in-cluster dispatcher launches SkyPilot jobs from it. The dispatcher only makes outbound calls to the site. |
| 5 | **A standing cluster-steward agent** | **Yes.** It owns the backfill list, reports utilization per tier every day, runs the timing windows on S4, and recommends scaling up or down every week. |
| 6 | **Donated clusters** (you had chosen pull runners) | **Defer.** A donor's Kubernetes becomes one more kubeconfig context for SkyPilot. Pull runners stay the fallback for a donor who won't allow inbound access. |

## Reference design: Shopify, and where we differ

Shopify runs persistent managed Kubernetes on Nebius and GCP, with SkyPilot as the launcher and a policy plugin plus Kueue on top ([Shopify Engineering, Jan 26 2026](https://shopify.engineering/skypilot)). We take the pattern whole.

| Shopify | Ours | Where we differ |
|---|---|---|
| Persistent clusters on two clouds; SkyPilot only launches onto them | One cluster of identical servers: one region, one image and driver, one data layer. SkyPilot launches onto it and also provisions RunPod for the edges. | We let SkyPilot provision RunPod, because the edge hardware (L40S, H100, 4090, captures) is rented by the hour and varies. |
| A policy plugin routes by accelerator, injects pod config and rejects a job without a cost-owner label | Our budget policy, from the trial's prototype:<br>• `RTXPRO6000` and CPU-only requests go to the cluster; every other GPU goes to RunPod.<br>• It injects the Kueue queue and priority, node roles, the cache mounts and the termination grace.<br>• It rejects a job without a `budget-line` label. | Shopify only reports costs (showback). We also enforce dollar caps, but only on RunPod. |
| Kueue quota groups per team, fair share, and priorities with preemption | A ClusterQueue per lane and per role, in one cohort. Priorities, highest first: merge-train checks, interactive boxes, lane research, backfill. | vLLM filler rows can't be preempted (5–11 h, no checkpoint yet), so they sit in a queue of their own that nothing borrows from. Timing gets an exclusive server. |
| Shared uv and Hugging Face caches, mounted automatically; volumes cleaned after 7 unused days | Lean toolchains and bundles, cargo and SP1, uv, vLLM weights and wheels, and store fixtures, on the shared filesystem. The steward removes entries unused for 7 days. | Lean's bundles are keyed by toolchain and manifest, so every train reuses them. The toolchains are baked into the image. |
| A GPU reaper that kills jobs below 20% utilization for a sustained period | Kueue's quotas, plus a reaper that cancels jobs sitting idle for 30 minutes (no CPU, GPU or I/O) and notifies their lane. Together they replace our guards and leases for standing work. | Our provers and vLLM rows barely use their GPUs (0–6%, 0–2%), so a GPU-utilization threshold would kill real work. Our reaper judges idleness on the whole host. |
| `dev: true` one-GPU interactive boxes, exempt from the reaper | The interactive tier: one box per lane on S1 (1 GPU and 16 vCPUs). It's exempt from the reaper and autodowns after 30 minutes with no job or SSH session. | The same idea. |

## Hardware

**One Nebius managed-Kubernetes cluster in `us-central1`:**
- **Servers:** four `gpu-rtx6000` servers (`8gpu-192vcpu-1744gb`: 8× RTX PRO 6000 with 96 GB each, sm_120, FP8/FP4; 192 vCPUs with AVX-512; 1,744 GiB), at $1.80 per GPU-hour all-in.
- **System nodes:** 2 small ones ($0.26/h), which run the API server, Kueue, the git mirror, the dispatcher and the steward's exporters.
- **One node image:** driver 580.x, CUDA 13, and sm_120 torch/vLLM.
- **Storage:** an 8 TiB ReadWriteMany shared filesystem, plus 3 TiB of network-SSD scratch per server.
- **No CPU pool.**
- **Later:** `us-central1` also sells the B200, so the frontier-model server can join this cluster.

**Server roles (Kueue quotas plus node labels and taints):**

| Server | Role | Queues it admits |
|---|---|---|
| **S1** | Checks, Lean, verifiers, prover development, dev boxes | `merge-train` (guaranteed 128 vCPUs and 1 TiB, which filler can never borrow), `interactive`, `lane-research`, `backfill` |
| **S2, S3** | vLLM filler: about 5 rows per server after the port; before it, the port's capture runs, sweeps and re-verification | `vllm-filler`, pinned to these two by node label, with no borrowing either way. `backfill` fills them until rows arrive. |
| **S4** (at 32×) | Exclusive timing, and backfill between windows | `timing` (taint `timing=exclusive`), `backfill`. Never vLLM rows. |

- **Checks on S1:**
  - its host equals six 32-vCPU / 256 GB check boxes;
  - a burst of checks borrows S4's cores between windows, or preempts backfill;
  - cold Lean audits should take 20–25 minutes on the 3.9 GHz Xeon, against 15–17 on 5 GHz parts, which isn't worth a second provider.
- **Before ordering:**
  - Nebius confirms capacity for four servers;
  - we ask whether an 8-GPU VM is single-tenant on its host, and whether `nvidia-smi` can lock clocks inside it (timing on S4 depends on both);
  - we ask whether MIG works inside the VM.

**Quota requests** (`us-central1`):
- 32 `gpu-rtx6000` GPUs;
- about 16 non-GPU vCPUs for the system nodes;
- 8 TiB of shared filesystem;
- 12 TiB of network SSD;
- one public IP or load balancer for the API server's ingress.

## Target architecture

- **The SkyPilot API server:**
  - **Where it runs:** in the cluster, from SkyPilot's Helm chart, on the system nodes. Its state is in our existing Neon Postgres, so a restart loses nothing.
  - **How to reach it:** TLS ingress, one SkyPilot service-account token per lane, and basic auth for you. Telemetry is off.
  - **What it drives:** one kubeconfig context (this cluster, through an in-cluster service account) and RunPod, through its native backend with our patch and pinned zones for CPU pods.
  - **Its policy:** the budget policy, with the routing and injection above.
- **Kueue:** one cohort `verity` with the queues under "Keeping it busy". GPU and CPU quotas cover the cluster, and the policy's dollar caps cover only RunPod.
- **Source ships by `git push`, never by clone or workdir upload:**
  - a small in-cluster git mirror keeps a bare repository on the shared filesystem;
  - `research` and the merge queue push the exact commit to it, over `kubectl exec` with the same `ext::` transport `research run --on` uses over SSH today;
  - jobs check out that commit with `git worktree add --detach` onto node scratch;
  - no GitHub token and no anonymous clone is needed. SkyPilot's workdir upload cost 44 s on every `exec` in the trial.
- **Shared warm caches:**
  - **Baked into the image:** uv, elan, the pinned Lean toolchain and Rust (today's `tools/check/pod_setup.sh`).
  - **On the shared filesystem:**
    - `/cache/lake/<toolchain>-<manifest hash>`, the Lean bundles (about 26 GB per toolchain);
    - `/cache/uv`, `/cache/cargo` and `/cache/sp1`;
    - `/cache/verity-tests`, the per-test cache;
    - `/data/fixtures`;
    - `/data/models`: vLLM weights, about 150 GB plus the FP8 checkpoints;
    - vLLM wheels and C++ twins.
  - **On node scratch:** a per-node copy of the weights.
- **Evidence:** every job runs its workload as `research run --tool …` inside the pod. That publishes the Attempt to R2 with custody before the pod exits, using an evidence-store token that can't spend, issued through the site's token approvals and mounted as a Secret. The merge gate reads Attempts as it does now. Nebius egress and R2 ingress are both free.
- **An agent's workflow:**
  - **Submit:** `research run --on sky --tool check -- …` pushes the commit, then calls `sky jobs launch` with the lane's labels, tier and budget line, and prints the run id.
  - **Dev box:** `research box up` runs `sky launch -c <lane>-dev --gpus RTXPRO6000:1` in the interactive tier; then `ssh <lane>-dev`, with the caches mounted.
  - **Results:** `research inspect` and the evidence store, as now; `sky logs` for live output.

## Keeping it busy

| Queue (Kueue priority) | What runs | Where, and how much | Preempts |
|---|---|---|---|
| `merge-train` (1000) | Merge-train checks, Lean builds and record regenerations | S1: 128 vCPUs and 1 TiB guaranteed (8 checks at 16 vCPU); bursts borrow S4's cores | everything preemptible below |
| `interactive` (500) | Dev boxes | S1: 1 box per lane, up to 4 GPUs | `lane-research`, `backfill` |
| `lane-research` (100) | Prover development, verifiers, sweeps; one ClusterQueue per lane | S1's other GPUs: 2 per lane nominal, borrowing idle GPUs and S4's between windows | `backfill` |
| `vllm-filler` (separate, not preemptible) | vLLM rows: the port's sm_120 re-baseline epochs, then filler | S2 and S3 only, about 10 rows, about 300 GPU-hours a day | nothing; nothing borrows from it |
| `timing` (exclusive) | Timed GPU runs, in windows the steward schedules | S4 whole: backfill is evicted before each window | `backfill` on S4 |
| `backfill` (1) | The steward's list | 0 nominal; borrows anything idle on S1, S4, and S2–S3 before rows arrive | nothing |

- **Preemption is instant by design:**
  - backfill pods get a 5 s termination grace (the trial measured the default 30 s as most of the 35 s handover);
  - backfill items checkpoint and are idempotent;
  - they run as SkyPilot managed jobs, so a preempted item is requeued rather than lost. A preempted SkyPilot cluster just disappeared in the trial, and we verify on day 0 that managed jobs recover.
- **The backfill queue is never empty.** It's fed from a `backfill.toml` in the notes, in this order:
  1. uncached full test runs (`check --fresh` on `main` and on open PR heads, and bisection checks);
  2. red-team batteries;
  3. parameter sweeps;
  4. re-verifying stored proofs with the Lean verifier;
  5. sm_120 hardware capture sweeps.
- **The cluster steward** is a standing agent. It:
  - keeps at least a day of backfill queued, and books S4's timing windows;
  - posts utilization per queue every day: Kueue's admitted and pending workloads, CPU, RAM and GPU per host, published to the store;
  - recommends a size every week: grow when `merge-train` or lane work waits more than 10 minutes at p90, and shrink when backfill fills more than 40% of the cluster for a week;
  - cordons a node that fails two setups, and cleans the caches.

## What stays ours

- **Merge trains, the queue, verdict reuse and the gate:** `queue.py`, `merge.py`, `tools/check/verdicts.py`, `check.py`, and the site's trains (stage 1.5). SkyPilot doesn't do any of the merge queue's jobs, so they stay ours:
  - **Publishing the result.** A check publishes its Attempt with custody from the pod. Checks haven't moved until a train lands on a check that ran on the cluster.
  - **One check per commit.** The site's jobs row holds the key (commit, tool) and the SkyPilot job id, and the dispatcher won't launch a duplicate while a live job or a verdict exists.
  - **Unschedulable jobs.** The dispatcher watches SkyPilot's job state and Kueue's `Workload` conditions, and raises `job.unschedulable` once a job has been pending past its start deadline, naming the queue and the resources.
  - **Broken workers.** Merge checks run with `max_restarts_on_errors: 0`, and restart only on infrastructure exits such as the preflight's exit 3. A node that fails setup twice is cordoned, so a retry lands elsewhere.
- **The evidence store** (R2 and Neon) and its site routes.
- **`research`**, as a thin wrapper over `sky`: labels, git push, `research run` inside the pod.
- **Budgets:** `budgets.toml` stays the one file, but the admin policy reads it instead of the guard, and only for RunPod.
- **Vercel** keeps the website, the merge-queue state and App credentials, the jobs table and events, and the database and evidence-store token approvals.

## What we retire

| Path | Replaced by | Retired |
|---|---|---|
| `tools/research/src/research/pods/lease.py`, `pods/sh/lease.sh`, `pods/sh/pod_guard.sh`, `pods/workproc.py` | Kubernetes and Kueue for standing work; SkyPilot autodown plus the policy's dead-man for RunPod | once RunPod runs through SkyPilot |
| `pods/guard.py` (the budgets guard); `pods/budgets.py` (the parser moves into the policy) | The admin policy | the same |
| `pods/runpod.py`, `pods/registry.py`, `pods/connect.py`, `pods/drain.py`; `machines.toml` and `machines.d/` | SkyPilot's RunPod backend, cluster list, `ssh <cluster>`, and custody published by each job | the same |
| `remote.py`'s SSH machine path (shipping, claim by run id, fetch) and `mem.py` (ramlock admission) | The git mirror, SkyPilot jobs, and Kubernetes requests | once the lanes have moved |
| `notes.py`'s pod functions: `probe_pods`, `running_pods`, `load_fleet`, `pod_view`, `terminate_pod`, `reap_lines`, `stale_reap_lines`, `reap_custody`, `run_custody`, `run_custody_r2` | SkyPilot status and the steward agent. Lane liveness stays. | once RunPod runs through SkyPilot |
| `cli.py`'s `research pods …` | `sky` | the same |
| Their tests: `test_budgets*.py`, `test_guard_fail_closed.py`, `test_pod_guard_daemon.py`, `test_pod_lease.py`, `test_pods_connect.py`, `test_pods_create_once.py`, `test_pods_drain.py`, `test_pods_registry.py`, `test_mem_admission.py`, `test_remote_ship_*.py` | The policy's tests | with the code |
| `tools/check/pod_setup.sh` | The image build (it moves; it isn't deleted) | day 0 |
| #442's `jobs/dispatch.py`, and the setup gate's done marker | The in-cluster dispatcher | day 1 |
| The site: `POST /api/jobs/claim`, renew and leases in `lib/jobs/service.ts`, the `jobs-expire-leases` cron, pull `workers` | The dispatcher (the jobs, events and audit parts stay) | once checks have moved |
| The spend broker proposal, and the token budget fields | Nothing: never built, and already being removed | now |
| The CI pool `vy-coord-*`; the control pod `vy-control-verity` and its guards | The cluster | checks moved; RunPod through SkyPilot |

Kept on purpose: `pods/part.py` and `pods/health.py` (hardware checks, run once per node and per RunPod pod), `pods/mem_guard.py` (the laptop guard), and the disk floor.

## Cutover

Day 0 is the day the Nebius account opens. Each step keeps today's path running until its exit test passes, and a slipped milestone just holds the fleet at its size.

| Day | Fleet | What moves | Exit test | $/h (fleet + RunPod) |
|---|---|---|---|---|
| 0 | none | We file the quota and check capacity. Then we build the cluster, system nodes, shared filesystem and image, and install the SkyPilot API server (Helm, the patch, the policy, telemetry off), Kueue with the six queues, the git mirror, the caches and the backfill list. The steward starts. | A job runs in each queue; a merge-train job preempts backfill; a managed backfill job is requeued after preemption; a check publishes an Attempt | 0 + 6.5 |
| 1 | **16×** (S1, S2) | **Checks and Lean builds** move to S1 through the dispatcher, in shadow for the first trains: each train's check runs both on the CI pool and on S1. S2 runs the port's capture runs (the sm_120 GEMM correspondence, the FA2 capture, the BF16 step), sweeps and backfill. | Two trains land on S1 checks. Then the `vy-coord-` line goes to $0/day and the CI pods terminate. | 30.0 + 6.5 |
| 2–4 | 16× | Checks run warm on the shared cache. The FP8 captures start on S2. **Lanes** move one at a time to `research run --on sky` and dev boxes; each lane's RunPod line closes as it moves. | Each lane's first recorded run on the cluster | 36.5 |
| 5–6 | **24×** (+S3) | **BF16 lands:** S3 runs the BF16 re-baseline (13 rows, 5–9 h each), then BF16 filler. | The BF16 epoch's rows are written | 44.8 + 6.5 |
| 8–9 | **32×** (+S4) | **FP8 lands:** FP8 rows are re-baselined; S2 and S3 become filler (about 10 rows); S4 becomes the exclusive timing server. | The FP8 epoch's rows are written; the first timing window runs on S4 | 59.7 + 6.5 |
| ~10 | 32× | The interim vLLM line and the current RunPod epoch close; the L40S/H100 records stay the reference. PoUS and captures launch through SkyPilot under the policy's caps. Then the retire table goes, including the control pod. | No pod left outside SkyPilot | **60.2** |

If Nebius lacks capacity for the next server on the day, the waiting filler runs on RunPod RTX PRO 6000 pods ($2.09/h, the same SKU) until it frees.

## Cost and sizing

From [compute utilization](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/compute-utilization.md). "Fleet" is the GPUs plus system nodes, scratch and the shared filesystem. RunPod is the interim vLLM line at $150/day (about $6/h) until the port, and about $0.5/h for PoUS and captures after it.

| Size | Servers | Fleet $/h | Fleet $/month | Total $/h before / after the port | vLLM rows after the port | Timing |
|---|---|---|---|---|---|---|
| 16× | 2 | 29.96 | 21.9k | 36.0 / 30.5 | 5 | drain S1 for a window |
| 24× | 3 | 44.80 | 32.7k | 50.8 / 45.3 | 10 | drain a server (rows finish within 11 h) |
| **32×** | **4** | **59.65** | **43.5k** | **65.7 / 60.2** | **10, with S4 held for timing** | **S4, exclusive and standing** |

- **The first 30 days** cost about $40k.
- **Against today:** we spend about $9.3k/month now, all on demand, with 955 GPU pods created in two weeks, 13 minutes on average to first work, and checks at 33 minutes median.
- **Discounts:** Nebius offers up to 35% off for multi-month commitments. Ask once utilization is known: 32× would be $37–46/h for GPUs.
- **Stepping down** costs nothing, since every size is on demand.
