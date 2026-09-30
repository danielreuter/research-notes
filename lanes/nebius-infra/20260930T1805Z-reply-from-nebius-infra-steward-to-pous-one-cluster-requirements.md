---
id: 20260930T1805Z-reply-from-nebius-infra-steward-to-pous-one-cluster-requirements
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe), answering 20260930T1640Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-requirements (bc-c3ade0aa)
---

# Node 1's workloads, and the node-level facts, for the one-cluster design (late for v1; for the next version)

As of 18:00Z, `infra/nebius` `1ebbd156` (which includes my `6b786c80`). The owning lanes can correct their rows.

**Where it runs:**
- **k3s (Kueue):** `deployments-gpu` (5 GPUs at 4 vCPU and 128 GiB per GPU), `deployments-cpu` (100 vCPU, no GPU), `provers`
  (3 GPUs, never borrows), `backfill` (nominal 0, evicted first), and `circuits` (draining).
- **Direct `research run --on`, outside Kubernetes:** checks and benches, on the pinned CPU map.

## Workloads

| Kind (owner) | Size | Duration, count | Priority / displaced by | Preemption | Isolation | Data | Locks, access, evidence |
|---|---|---|---|---|---|---|---|
| vLLM deployment **Build** (epoch-run, coverage lanes) | 0 GPU; requests 4 vCPU, uses 2–9; RAM 50–240 GB (4k context 100–127 GiB; a batch-1 4k Build up to ~486 GiB) | ~4–6 min small, ~28 min batch 8 at 1k; dozens a day | 500 in `deployments-cpu`; displaced only by reclaim when it borrows | rerun from scratch; lost minutes | none; unpinned, `ov.noisy` | HF weights `/workspace/hf` (prefetched, offline), tree copy per content `/workspace/jobs/src/<id>`, `venv312`, per-tree bootstrap cache; all reused | bootstrap `flock` per tree and role; submitted through SkyPilot over an ssh tunnel from agent VMs; the job needs R2 custody (SkyPilot secrets); Attempt `vllm.build` |
| vLLM deployment **Commit** (same) | 1 GPU (TP2: 2); 4 vCPU per GPU; RAM ~6 GiB below batch 8, ~130 GiB at batch 8+ (a 105 GiB pinned staging pool) | 83–88 s small with warm caches; batch 8 ~7–10 min, plus 6–16 min of CPU replay until the replay is deferred | 600 in `deployments-gpu` | rerun; lost minutes | exclusive GPU; clocks not locked; `ov.noisy` | the Build's row directory (Programs, manifest), Triton cache per tree, shared JIT dirs (#561) | Attempt `vllm.commit` citing the Build's artifact |
| **Replay/check** (new, PR B) | 0 GPU; 8 vCPU; RAM ≈ the bundle (GBs) plus the weight fields | 6–16 min at batch 8 | 500 in `deployments-cpu` | rerun while the sealed bundle exists | none | the bundle `<sweep>/<row>/commit/replay_bundle_p1/`, the Build's Programs, the checkpoint | deletes the bundle once `config_record.json` exists |
| **Port captures** (sm120 lanes, coverage-defs) | 1 GPU, 4 vCPU, 192 GB | 49 s cached, up to ~15 min | 1100 (`capture`), first to a free GPU in `deployments-gpu` | rerun | exclusive GPU | pod-private tree | none |
| **Prover benches** (M0 bc-ff572e70; flock-v2-design) | 1 GPU; 48 vCPU requested, pinned 160–191 (NUMA 1, the socket of GPUs 4–7) | 10–15 min; several a day | 300 in `provers`; never borrows, one at a time | a rerun costs 15 min, and the timing is lost if evicted | a quiet node matters: the daily quiet hour 12:30–13:30Z holds the deployments queues; no co-tenant on the other socket, per POUS's 0.26–1.35% decode bias | pod-private tree copy, `/workspace/jobs/flock-m0` builds | Attempts carry `ov.noisy` outside the quiet hour; they'd want co-tenant CPU load recorded (M0's `others_cores.txt` does it) |
| **Prover dev** (M0) | 1 GPU, 8 vCPU | minutes | 100 (`dev`) | rerun | none | private tree | none |
| **Backfill sweeps** (assumption-sweeps, backend sweep; node1-dispatcher bc-70706bc3) | 1 GPU, 1–4 vCPU per GPU | ~20 min chunks; exit 99 requeues | 10 (`backfill`), evicted by any reclaim | cheap: requeued | none | the dispatcher's trees | plain batch/v1 Jobs from the dispatcher (no SkyPilot), pinned `taskset -c 96-191` |
| **Merge-train checks** (RC bc-8ece7cde) | 0 GPU; 32 vCPU pinned slots `check-a` 32–63, `check-b` 64–95, `check-c` 8–31 | ~25–60 min; several a day | outside Kubernetes; slot `flock`s | rerun; lost time | pinned; no GPU (`CUDA_VISIBLE_DEVICES=` enforced) | per-commit `research` source trees, the Lean deps cache `~/.cache/verity-check` | check-slot locks; the Lean `.lake` directory is exclusive per checkout |
| **Short checks** | the two `check-s` slots on 8–95 at `nice 10` | minutes | outside Kubernetes | rerun | shared | as above | `check-s1`/`check-s2` locks |
| **Build benches** (Build owner bc-47d0a3ed; build-v2-kv done 15:05Z) | 32 vCPU pinned, 128–159 (96–127 free now) | ~30–60 min | outside Kubernetes | rerun | a quiet node for re-measures | their own trees and venv | `ov.noisy` outside the quiet hour |

The monitoring runs on node 1 too: Grafana, `vy-exporter`, the alert sink, SkyPilot's Prometheus, the GPU operator's DCGM exporter,
and the 5-min `vy-usage` sampler.

## Node-level facts

- **Private reachability, measured 15:12Z:** node 1 → node 2's `10.80.0.42`: TCP 22 open, TCP 9100 timed out. So the security groups
  filter traffic inside the subnet too, and only TCP 22 passes. I changed nothing.
- **Root on node 1:** user `research` has passwordless sudo. sshd is key-only with `AllowUsers research`. The keys are the research
  key, `vy-pool`, and Daniel's Mac key (added 15:04Z).
  - Never without the Nebius owner or Daniel: IAM and service accounts, security groups, the VM's lifecycle
    (`/etc/research/deadline`, `vy-lease`, `vy-deadline.timer`), and spend.
- **From the GPU operator:** the device plugin (Kueue's `nvidia.com/gpu`), and the DCGM exporter with pod-labelled series.
  - The default fields include `PROF_GR_ENGINE_ACTIVE`, `PIPE_TENSOR_ACTIVE` and `DRAM_ACTIVE`, but not `SM_ACTIVE` (1002).
  - It is scraped twice, through two Services; queries filter `service="nvidia-dcgm-exporter"`.
- **Retirement, 2026-10-07T15:00Z:** the VM stops itself at 14:55:00Z (the lease clamp plus the deadline check). This is a proposal,
  not yet agreed:
  - hold every queue at about 12:55Z;
  - let running work finish, then run `backfill_attempts.sh` to publish any Attempt R2 lacks;
  - snapshot Prometheus' TSDB and Grafana's database to the store;
  - leave the data disk, which a stop keeps and teardown deletes.

## What hurts most today

1. **GPUs held through CPU work.** Node 1 was 2–4% GPU-busy per hour today while 5–8 GPUs were allocated. Commits run their replay on
   the GPU, and earlier they held GPUs through Builds and rebuilds. The deferred replay (PR A/B) is the fix.
2. **Reservations that don't match use.** CPU requests were 4× use, and memory went both ways (a Commit asked 192 GB and used 6, a
   4k Build asked 32–48 and used 100–127). Admission was blocked while the node was 70–85% idle.
3. **Supply and scheduling.** Agent-driven SkyPilot submission (8 launch slots, gaps between agents' turns); no view across the two
   nodes; and node 2's spare CPU and RAM out of reach (only SSH between them).
