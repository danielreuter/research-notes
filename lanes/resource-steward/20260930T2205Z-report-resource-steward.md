---
id: 20260930T2205Z-report-resource-steward
campaign: verity
lane: resource-steward
kind: report
status: open
repo: danielreuter/verity
origin: resource-steward (bc-b154b9ef-b9e0-560b-857b-56c2d5530ead), worker of the infra coordinator (bc-17cc41f1)
---

# resource-steward: disk, RAM and cache policy for vy-nebius-1 and vy-nebius-2

The steward's only job is keeping disk, RAM and other resources on the two GPU nodes from being overwhelmed (Daniel's ruling,
2:52 PM PDT 30 Sep). It owns disk, cache and RAM policy on both nodes. It runs until the nodes stop at 7 Oct 14:55Z
(7:55 AM PDT). It is woken by a 20-minute timer, by top-level posts in `#agent-alerts`, and by `*alert*` notes in
`lanes/infra/`, `lanes/node2-ops/` and `lanes/resource-steward/`. It stays silent unless a threshold is crossed or it acts.

## 1. Policy

### Delete without asking
Only with no open files (`lsof +D`), and only at `nice 19 ionice -c3`:
- check scratch untouched for more than 2 h: `~/.cache/verity-check/lean-audit-scratch-*`, other scratch a finished check
  left, and `/tmp/pytest-of-research/*` (20 GB on node 1's root disk now);
- benchmark scratch (`/workspace/research/tmp-bench` and the like);
- LRU entries of regenerable caches, only while their filesystem is over its watermark, oldest first, down to 5 points under
  it: `~/.cache/uv`, `/workspace/cache/uv`, `/workspace/jobs/cache/{uv,triton}`, `~/.triton`, `~/.cache/vllm`, and
  harness venvs under `/workspace/cache`. Never `~/.cache/verity-check/lean-deps` or `circuit-check` (check's verdict caches;
  their owner is the check, and run `r20260930-213917-d6b3` is moving them to `/workspace`);
- shipped source trees `/workspace/research/src/<sha>` older than 24 h that no running run references (checked against every
  running run's `launch.json`/`status.json` and `lsof`). The oldest tree now is from 05:22Z, so none qualifies before
  1 Oct 05:22Z (10:22 PM PDT tonight).

Every deletion is logged in §4 (path, size, age). Slack hears of it only if it frees over 50 GB.

### Ask the owner first
The steward asks on Slack `--as infra`, prefixed "resource-steward:", tags the owning handle, and waits for a yes:
- weights in `/workspace/hf` and `/workspace/jobs/hf` (@circuits, @proofs, @compute-accounting);
- replay bundles, sealed or `.partial` (@circuits);
- `/workspace/pouw/*` (@compute-accounting);
- `/workspace/research/runs/*` entries, preserved or not (the owning lane, through its coordinator);
- anything else it isn't sure of.

Anything destructive beyond this policy goes to Daniel as a blocking `#ask-daniel` card.

### Hard stops
- Node 2's `/workspace` at 55%: no new jobs start. node2-ops' runner enforces it; the steward only verifies it. Verified
  22:10Z: `fill_runner.py` refuses new **Verity guest** jobs at `FILL_VERITY_DISK_PCT` = 55. PoUW's own fill isn't under
  that stop, so at 55% the steward asks @compute-accounting to hold new PoUW fill that writes to disk.
- Node 1's `/workspace` at 85%: the steward asks kueue-fold, the nebius-infra steward and @circuits to hold new Builds and Commits.
- Root disk under 45 GB free: no new check starts (check's own preflight floor, `tools/check/preflight.py`, is the same 45 GB).
- Replay RAM is reserved before a Commit is admitted: the steward flags any node where the replay RAM to come is over half of
  its available RAM (after `/workspace/ramlock` reservations).
- Never delete unpreserved run outputs. Never touch `/workspace/pouw/gpu3-fp8`. Nothing runs on node 2 while
  `/workspace/pouw/fill/status.txt` says `timed True` (the tick skips node 2's probe then).

### Thresholds (the probe's watermarks)
| metric | node 1 | node 2 |
|---|---|---|
| `/workspace` used | alert 80%, hard 85% | alert and hard 55% |
| root free | alert < 60 GB, hard < 45 GB | same |
| inodes used, either filesystem | 80% | 80% |
| inode growth, either filesystem | > 100k files/h | same |
| RAM available | < 10% | < 10% |
| replay RAM to come | > ½ available | > ½ available |
| GPU memory at 0% util | > 20 GiB for 15 min | same |
| finished runs without custody, older than 1 h | > 10 | > 10 |

Replay RAM to come is counted differently on each node. On node 1 it is Kueue's pending `*-replay-*` Workloads, each at
max(its memory request, 90 GB). On node 2 it is the queued `verity-replay-*` fill jobs at max(`mem_gb`, 90 GB), plus each
running `verity-commit-*` at 90 GB, since each queues a replay when it ends; a queued Commit reserves nothing until it runs.
The 90 GB floor is a Phi-3/Mistral batch-8 bundle; the requests (64 GB) are lower. GPU idle comes from node 1's Prometheus
(DCGM) and from node 2's sampler JSONL, never from NVML. A run has custody on its node when it has `.custody`, `.fetched`
or `preserved.json`.

### Overlaps: one owner
- Disk, cache and RAM decisions on both nodes: **resource-steward**.
- Enforcement: node2-ops keeps its OOM guard (`node_ops.py`) and its job-start disk stop (the fill runner), but hands disk and
  cleanup decisions to the steward.
- The nebius-infra steward's node-1 disk reporting folds into the steward.
- GPU idle-in-lease and unleased GPUs as job norms stay with node2-ops and kueue-fold (`publish_pool.py`, `pool_n1.py`).
  The steward's 15-minute, 20 GiB rule is about memory held; it doesn't re-alert a GPU those monitors already flagged.
- Handoffs: `note:20260930T2205Z-handoff-from-resource-steward` in `lanes/node2-ops/` and `lanes/nebius-infra/`.

### Daily
At 8 AM PDT (15:00Z), a summary in `#agent-coordination` (`--as infra`, "resource-steward:"): headroom per node and
resource, what was deleted, what waits on an owner, and trends (from each node's `~/.local/state/resource-steward/history.jsonl`).

## 2. Probe
- `tools/research/src/research/pods/nebius/resource_probe.py` on `infra/nebius` (`233f451f2`, then `7bcf2fc5f`: inode growth
  is measured against a base reading at least 15 min old), with its test `tools/research/tests/test_nebius_resource_probe.py`
  (12 tests).
- Deployed at `~/resource-steward/bin/resource_probe.py` on both nodes (sha256 `765bc846…`, `infra/nebius` `542169a73`, 22:33Z), by
  install and rename.
- The tick is `lanes/resource-steward/tools/tick.sh`: the probe on both nodes (node 2 skipped in a timed window), plus new
  resource `*alert*` notes. It exits 1 only for a new kind of breach, a HARD stop, a failed probe or a new alert note; a known
  breach prints as `known:` and exits 0. `tools/bootstrap.sh` restores the agent VM after a reset (no secrets).
- It reads statvfs, `/proc/meminfo`, the ramlock dir, Kueue (node 1) or the fill queue (node 2), Prometheus (node 1) or the
  sampler JSONL (node 2), and the run dirs. It takes 0.1–0.8 s at `nice 19`, and never deletes, stops a process or touches NVML.
- Exit codes: 0 means all clear, 1 a breach (one line each), 2 a failed source (never read as all clear).
- Each node keeps its state and history in `~/.local/state/resource-steward/`.

## 3. Baseline (30 Sep 2:55–3:05 PM PDT, 21:55–22:05Z)
| | node 1 (vy-nebius-1) | node 2 (vy-nebius-2) |
|---|---|---|
| root | 155 GB free of 265 (42%), inodes 5% | 199 GB free (26%), inodes 3% |
| `/workspace` | **71%**, 1.58 TB free of 5.39 TB, inodes 35% | **36%**, 3.46 TB free, inodes 11% |
| RAM available | 1,308 GB of 1,800 (73%); shmem 91 GB | 1,531 GB (85%) |
| ramlock reservations | none | none |
| replay RAM to come | 4 pending replay Workloads × 64 GB request (360 GB at the floor), ½ available = 654 GB: OK | 0 (14 Commits queued, none running): OK |
| GPUs holding memory at 0% | GPU 0 (53 GB) and GPU 2 (49 GB), 15 min+, both `nd-vllm-epoch-run-*-gpu-0` in `deployments-gpu`; `pool_n1` flags them too | none |
| runs without custody, > 1 h | 1 (`r20260930-080414-bae0`, failed) | **13**: see §5 |
| `~/.cache/verity-check` | 35 GB (lean-deps 34, circuit-check 0.9); no scratch | 35 GB (lean-deps 34); no scratch |
| uv / Triton / vLLM caches | `~/.cache/uv` 1.0 GB, `/workspace/cache` 26.5 GB, `/workspace/jobs/cache` 20.0 GB | `/workspace/cache` 29.1 GB, `/workspace/jobs/cache` 0.5 GB, `~/.cache/vllm` 44 MB |
| weights | `/workspace/hf` 2.92 TB | `/workspace/hf` 175 GB, `/workspace/jobs/hf` 121 GB |
| `/workspace/research/runs` | 57 GB (344 dirs) | 122 GB (572) |
| `/workspace/research/src` | 162 GB (181 trees, oldest 05:22Z) | 38 GB (272) |
| `/workspace/research/trees` | 62 GB | — |
| `/workspace/jobs` | **517 GB** (runs 149, flock-sweep2 87, probe-jit 80, cov 76, store 38, src 34, flock-v2 19, flock-m0 18, venv312 11) | 140 GB |
| `/workspace/pouw` | — | 1.36 TB |
| `/tmp` (root disk) | 21 GB, 20 GB of it `pytest-of-research` | 3 GB |
| replay bundles found | 1 × 0.56 GB (`research/runs/cfgtp2-cpu`); the 60 GB and 11 GB `.partial` bundles in `probe-jit` are gone | none |

Node 1's `/workspace` has grown from 69% at 2:24 PM PDT to 71%, and `/workspace/jobs` from 398 GB to 517 GB. At 1.58 TB
free, it reaches the 80% alert after about 0.48 TB more. The trend line starts with the next ticks.

## 4. Deletions
None yet: no filesystem is over its watermark, there's no check scratch on either node, and no source tree is 24 h old.

## 5. Waiting on an owner
- Node 2 has 13 finished runs older than 1 h without custody, which is over the threshold of 10:
  - three are node2-ops' hourly backups that stalled in multipart custody: `r20260930-081105-b32f` (17 GB),
    `-091913-2c58` (17 GB) and `-102051-0e13` (3.9 GB), superseded by chunked backups since 10:27Z;
  - ten are small smoke runs (104 KB to 1.2 MB: `true`, `sha256sum` and `bash`) between 14:34Z and 18:55Z, with no lane set.

  Nothing is deleted. The handoff asks node2-ops to publish them or confirm they can be marked superseded. (15 at
  3:40 PM PDT.)
- @proofs (backend-sweep-2): whether the `out/classes` trees of `73-sweep-shape.sh MODE=sampled-stage` rows (35–60 GB
  each in node 1's `/workspace/jobs/runs/<run>/`) are regenerable and may go once proved, and whether the feeder can hold
  new rows or clean up after itself. Asked at 3:43 PM PDT
  ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790808184589359)), reply wanted by 4:15 PM PDT.

## 6. Log
- 21:54–22:10Z (2:54–3:10 PM PDT) first turn: set up; took the baseline; committed the probe (`233f451f2`, `7bcf2fc5f`) and
  deployed it on both nodes; wrote this policy; sent handoffs to node2-ops and nebius-infra. Armed the timer
  `sub_2e3eb17f-7145-4485-98f4-f7b34e205e8c` (every 20 min), the daily summary `sub_4f6daaa1-65b4-4661-a34c-164a12906876`
  (15:00Z, 8 AM PDT) and the `#agent-alerts` subscription `sub_f6fd3baf-37fd-4fd9-9065-0f6312611b38` (top level, until 3 Oct
  22:09Z, renewed on every wake).
  Over thresholds now:
  - node 2: 13 runs without custody (handed to node2-ops);
  - node 1: GPUs 0, 2 and 4 hold 48–52 GiB at 0% for 15 min+ (`nd-vllm-epoch-run-*-gpu-0` in `deployments-gpu`),
    already flagged by `pool_n1`'s `gpu-idle-in-lease`, so the steward doesn't re-alert them.
  No Slack post.
- 22:20–22:33Z (3:20–3:33 PM PDT) tick: the agent VM had been reset, and `tools/bootstrap.sh` restored it. A false idle
  on node 1's GPU 0: DCGM's 15-min window spanned a pod handover (the new pod started 22:16Z). Fixed in the probe
  (`a38ac68a2` + `542169a73`): on node 1 a GPU is idle only when one pod held it for the whole window, and GPUs that
  `pool_n1` already flags idle-in-lease are recorded in `idle_gpus_pool_flagged` rather than re-alerted. Known: node 2's
  13 runs without custody (with node2-ops). No deletions, no Slack post.
- 22:40–22:45Z (3:40–3:45 PM PDT) tick:
  - **Node 1 `/workspace` at 77%, up from 71% at 3:05 PM PDT** (about 4–5 GB/min). `/workspace/jobs` went 517 → 736 GB:
    `jobs/runs` 149 → 304 GB, mostly backend-sweep-2's sampled-stage rows (`out/classes`: `r20260930-210718-2f89` 59 GB
    done, `-220453-9cce` 48 GB, `-220453-b99a` 40 GB done, `-220551-3af1` 35 GB, `-223358-1749` 17 GB); `cov` 76 → 144 GB;
    `probe-jit` 80 → 104 GB. The 80% alert is due about 4:20 PM PDT, the 85% hold about 5:15 PM PDT. Asked @proofs on
    Slack (above). Nothing in the policy's delete-without-asking list frees a useful amount: the caches are about 46 GB, and
    no source tree is 24 h old.
  - Node 1 gained 1.47M inodes/h: a one-off. The check-cache move (`r20260930-213917-d6b3`) ran at 22:10Z; `~/.cache/verity-check`
    is now a symlink to `/workspace/research/cache/verity-check`, and root is at 183 GB free.
  - Node 2 root gained 154k inodes/h (3% used). A timed window was running at 22:45Z, so nothing was looked at there.
  - RAM: answered nebius-infra's memory-requests alert with a request policy: Builds 160 → 48 GB, Commits below batch 8
    170 → 64 GB, limits unchanged (`note:20260930T2243Z-handoff-from-resource-steward-ram-requests`, in `lanes/nebius-infra/`
    and `lanes/vllm-epoch-run/`).
- 23:00–23:45Z (4:00–4:45 PM PDT) ticks:
  - Node 1 `/workspace` fell back to 72% by 4:00 PM PDT. @proofs and the old research coordinator answered at 3:44 and
    3:45 PM PDT ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790808184589359)): `out/classes` is
    regenerable. The feeder now prunes after each prove (`PRUNE=1`) and keeps at most 2 deployments on disk. They gave their
    yes to delete the surplus, but the lane had cleared it already: at 4:45 PM PDT one running row's 1 GB was left. Nothing
    deleted by the steward; closed in the thread.
  - Fixed `tools/tick.sh`: the breach key dropped the node's digit, so node 2's new inode-growth breach read as node 1's
    known one.
  - Node 2 `/workspace` is gaining about 117k inodes/h (12% used). The driver is `research/src` (about 320k new entries/h,
    one tree shipped per run), and the same holds on node 1. The policy's 24 h cleanup of unreferenced trees starts with the
    one-off timer `sub_27548cd0-02bb-4360-91f0-e8bcf31c9e86` at 1 Oct 05:30Z (10:30 PM PDT).
  - Node 2's runs without custody are up to 21:
    - node2-ops said yes to deleting the three superseded whole-node backups
      (`note:20260930T2215Z-reply-from-node2-ops-unpublished-runs`). They stay anyway, because the steward never deletes an
      unpreserved run output. Node 2 is at 37%, with no pressure.
    - Eight new small PoUW check runs launched without `--custody-r2`: asked @compute-accounting to fetch or publish them and
      to launch with custody ([thread](https://computeverification.slack.com/archives/C0C5RCXL66N/p1790811792332849)).
    - The ten earlier smoke runs: node2-ops names bc-0f3f8a2f, bc-efe47341 and the nebius-infra steward as likely
      submitters; they stay (under 3 MB).
- 00:00Z (5:00 PM PDT) tick: node 1 `/workspace` is gaining about 336k inodes/h (40% used; space 70%).
  - The driver is `research/src`: about 5–10 trees shipped an hour, each with its own `.venv` (about 22k files) and often a
    Lean `.lake`, so about 24–30k inodes a tree.
  - With the policy's 24 h cleanup (first at 05:30Z), steady state is about 4–7M inodes for `src`, which should keep the
    filesystem under the 80% inode alert.
  - If it doesn't, the next step is to ask the research tool's owner to share one venv per lockfile across trees.
  - No action now.
- 00:20Z (5:20 PM PDT) tick: node 2's inode growth (about 112k/h, `research/src`, as at 23:40Z) came back after dipping
  under the threshold for one tick. `tools/tick.sh` now remembers a breach kind for 6 h, so a metric that flaps around its
  watermark doesn't wake the steward each time. No action.
- 00:40Z (5:40 PM PDT) tick: **node 1 `/workspace` inodes at 42% and rising 0.7–1M/h**, which is 80% in about 8 h (around
  1:40 AM PDT) and exhaustion around 6 AM PDT.
  - The driver is `research/src`: 196 trees hold 4.15M inodes, 3.57M of them in 167 trees older than 6 h (2.28M in 114 trees
    older than 12 h), and none is 24 h old. Each tree carries its own `.venv`. A missing tree is shipped again from the node's
    bare git repo (`remote.ship_source`).
  - A cleanup sooner than 24 h is deletion beyond the policy, so it went to Daniel as blocking card
    `01933aa8-6663-4d2e-989c-7b2d983bddfd` ([card](https://computeverification.slack.com/archives/C0C5UCA0S0Z/p1790815323264569)):
    6 h (recommended), 12 h, or keep 24 h, deadline 11 PM PDT, with a timing correction in its thread. A one-off timer at
    06:00Z checks it.
  - Probe `b27322950` (sha256 `ccf53b63…`, both nodes): inode growth is now HARD when the watermark is under 12 h away, so a
    known breach that escalates still wakes the steward; it had been hidden as `known:`.
  - Node 2 was in a timed window and was skipped.
