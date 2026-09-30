---
id: 20260930T2035Z-draft-one-queue-cutover-and-onboarding
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# One queue: what failed, every workload, what the queue must do, and the cutover order and onboarding pattern

Written 1:35 PM PDT, 30 Sep, for Daniel's priority 1 and the eight "settled" criteria in
`note:20260930T1845Z-report-infra`. It was drafted from the notes stamped 19xx and 20xx in `lanes/infra/`, and from #586 at `1abe668f`.
Two inputs are still due: bc-2aa33ad8's job-level list (`rtx-pro-workloads.md`, 2:00 PM PDT, folded in through an @old-accounting
addendum) and verity-root's `gpu-utilization-postmortem.md`, which hasn't been posted to `lanes/infra/` yet.

**Short cites** used below, each a `note:` id in `lanes/infra/` unless another lane is given:
[OA] `20260930T2025Z-reply-from-old-accounting-utilization-and-workloads` ·
[OCv] `20260930T2020Z-reply-from-old-circuits-and-proofs-utilization-workloads-queue` (the vLLM remit) ·
[OCt] `20260930T2030Z-reply-from-old-circuits-and-proofs-utilization-and-workloads` (the merge trains) ·
[PR] `20260930T2019Z-handoff-from-proofs-workload-inventory` · [CI] `20260930T2024Z-handoff-from-circuits-workload-inventory` ·
[CA] `20260930T2025Z-handoff-from-compute-accounting-pouw-workload-inventory` ·
[MA] `20260930T2020Z-handoff-from-memory-accounting-workload-inventory` ·
[NA] `20260930T2022Z-handoff-from-network-accounting-workload-inventory` ·
[CO] `20260930T2025Z-handoff-from-console-node-inventory-and-utilization-panels` ·
[KF] `20260930T1947Z-handoff-from-kueue-fold-step2-node1-busy-is-the-work-mix`, `20260930T2026Z-handoff-from-kueue-fold-step3-builds-on-node2-live`
and `lanes/vllm-coordinator/20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit` ·
[KFo] `lanes/pous/20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract` ·
[CB] `20260930T2004Z-handoff-from-cluster-build-step3-shadow-running` and `lanes/kueue-fold/20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface` ·
[PLAN] `20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan` · [DES] `20260930T1858Z-draft-one-cluster-design` ·
[N2] `20260930T2016Z-handoff-from-node2-ops-verity-pool-live` and `lanes/kueue-fold/20260930T2015Z-reply-from-node2-ops-verity-pool-live` ·
[RUL] `20260930T1915Z-rulings-from-daniel-one-pool` · [JS] `20260930T1917Z-draft-from-verity-root-job-service-design` ·
[RP] `20260930T1917Z-draft-from-verity-root-runpod-spend-and-check-pod-policy` · [ST] `20260930T1905Z-reply-from-nebius-infra-steward-alerts-shadow-runs-decisions` ·
[AL] the Grafana alerts `20260930T1907Z-`, `1937Z-`, `2007Z-alert-gpu-idle-while-work-is-waiting-*` and `1928Z-`, `1958Z-alert-pod-holds-a-gpu-at-0-*`.

## 1. What failed in the last 48 h

**Scale:** node 2 from 11:05 PM PDT on 29 Sep to 1:00 PM PDT on 30 Sep was about 111 GPU-h: 67 busy (60%), 31 free-idle and 14 leased-idle [OA §A1].
Node 1 was about 1–6% busy for most of the day, and 1.0% over the hour to 12:47 PM PDT [KF][PR]. Node 2 met the target in the
hour to 1:00 PM PDT: 95.1% busy and 100% useful [N2].

| Failure | Cause | GPU-h or impact | Evidence | Queue feature that fixes it |
|---|---|---|---|---|
| **Queue dry: GPUs free, no work queued** | Lanes hadn't written their GPU work. Node 1 waited overnight on #477 and the trains | node 2 ≈ 15 GPU-h; node 1 ≈ 30+ GPU-h to 1:40 AM PDT | [OA A1], [CA A], [OCv A1] | A standing backlog per owner, an hourly "missing work by owner" line, and labelled `filler` only when nothing useful waits |
| **GPU held through a CPU phase** | Prep on the CPU inside a GPU lease (FP4 probes, FP8 repeats, `fp8chain-die*`); a Commit's replay on its GPU (16 min for Phi-3 B8); Builds on the GPU until #536; JIT rebuilds (436 s for 1.5 s of work, fixed by #561) | node 2 ≈ 7.6 GPU-h leased-idle; node 1 is most of its idle GPUs (8 held at 1.8% busy) | [OA A1], [CA A], [OCv A1], [CI], [KF], [AL] pod-at-0% | A `gpus=0` step the GPU step waits on (`after`), and leased-idle per owner in the failure feed |
| **Node 1's quota blocks idle GPUs** | Kueue's nominal quota can't be reclaimed: 2 Commits (priority 600) waited behind sweeps (100); backfill can't borrow; memory reserved 1.49 TB against 110 GiB used; CPU requests about 4× use | 4–6 GPUs idle while 3–12 workloads waited, for more than 30 min at a time; GPU-h unknown | [KF], [OCv A1], [CI], [AL] gpu-idle, [DES §16.15] | One planner with no quota arithmetic between a free GPU and waiting work, workstream reclaim within 30 s, and requests sized from measured peaks |
| **Node 2 lease-tool bugs** (all fixed) | A lease-order stall (7 GPUs behind one lease); one start per tick; a reserved GPU; a `keep-free` hold; the waiters bug (holders read from `/proc` as waiters) | ≈ 6 GPU-h, plus a large share of 8–11 AM PDT | [OA A1], [CA A] | Reservation with backfill, no held-back GPUs, and lease state from the ledger alone |
| **Windows killed long holds** | A timed window preempted five 20-min holds 15 min in | 1.25 GPU-h with no result | [OA A1] | GPU chunks of at most 8 min, enforced through `max_s` |
| **Timed windows disturbed** | `research run`'s sampler polled NVML inside 8–15 timed runs until 10:25 AM PDT; custody uploads, backups and recorded checks aren't paused in windows; CPU load biases decode 0.26–1.35% | the rows at risk; the NVML A/B moved nothing beyond noise | [OA A2, C1], [CA C1], [DES §16.8] | A quiet class: guests evicted, CPU and staging frozen, samplers off, a quiet certificate per window |
| **Host state in checks** | Checks as `research` saw lanes' builds in `/workspace/cp`, the host's deadline and `LEASE_DIR`, and Python 3.14 | about 1 in 3 check failures today | [OCt A2] | A clean job environment and private scratch |
| **Shared mutable caches** | The per-test cache race (3 crashes); the backup tarred `hsplit` state mid-rewrite (an hour of units lost); the JIT lock serialised Commits (warm-ups 137–632 s) | train re-runs; one hour's backup | [OCt A3], [OA A2], [OCv A2] | A private cache per job, shared caches keyed by content, outputs snapshotted before custody |
| **CPU pins overlapped benches** | Checks on 128–191 beside M0's and the Build lane's benches; lane checks opened CUDA on node 1 | corrupted bench plots | [OCt A5], [OCv A2] | Exclusive cpusets from the planner, and CUDA hidden from `gpus=0` jobs |
| **Results stuck or lost at custody** | Multipart uploads over 64 MiB stalled from node 2 for more than an hour; a manifest over 256 KB (3,332 files); a 9.5 GiB upload from the wrong cwd; job 81's attempt never reached the store; #563's missing account artifact; 130 deployments failed closed on staging (#594) | results delayed or recovered by hand | [OA A3], [OCt A6], [OCv A3] | Custody before release, in parts under 64 MiB, with declared outputs; a failed publish is a failure-feed event |
| **Silent failures** | rc 1, 4 or 7 with an empty log (v2-hot ×4, forms rc=4 ×2 on `GPU-0c776bca`, gpu5 prep); `uv run --no-project` can't import `verity`; the offline HF cache lacked `refs/main` | a retry each, plus a person's attention | [OA A1b], [CA A] | The failure feed, with a stderr tail and an owner, posted to `#agent-alerts` |
| **Preemption lost work** | Borrowed-GPU deployments restarted from scratch; M0 evicted twice while borrowing; the runner ignores SIGTERM, and the workload isn't in its process group | reruns | [OCv A2], [DES §2], [OCt A6] | Per-class preemption (`never`, `freeze`, `requeue`), `provers` never borrows, cancel by process group |
| **Idle or unowned spend** | RunPod check pods idle between trains; the PoUS band run at $2.00 against a $1.50 cap; #449's pod recreated with no job; three stale `vy-pous-*` machine entries | dollars, not GPU-h | [OCt A1], [OA A1c], [MA], [RP] | No ad hoc compute, and a daily scan for unowned work |
| **Friction that led agents around the queue** | Launch in 5.4 s and output at 10.8 s; `research pods ssh` forwards no stdin; store EAGAIN; hourly GitHub lapses (fixed by the broker); no CPU-only Kueue template; every GPU ask went through bc-2aa33ad8 | hand-run jobs, relays | [OA A4], [OCv A4], [OCt A7], [DES §4] | One fast `research run` submit for every lane, with logs streamed |

## 2. Workload table

The node is 1 (vy-nebius-1) or 2 (vy-nebius-2); every GPU is an RTX PRO 6000 (sm_120) unless the row says otherwise. The queue class uses
#586's priorities (`service` 1000, `timed` 900, `session` 700, `capture` 600, `work` 500, `bench` 300, `dev` 100, `fill` 10)
and the `checks` pool (node 1, CPUs 8–95).

| Workload | Owner | Node, GPU | Resources | Duration × count/day | Quiet or timed | Preemption | Data | Starts today | Queue class |
|---|---|---|---|---|---|---|---|---|---|
| vLLM Build | circuits (epoch-run, tc-gemm, TP2) | 1 or 2, CPU | 4 vCPU (uses 2–9), 50–256 GB; a 4k B1 needs ~486 GiB, node 1 only | 3 min–3 h; ~500–740 left in the grid | no | requeue | weights `/workspace/hf` read-only; out: a Build dir of GBs | dispatcher Kueue Job; `n2_build.sh` on node 2 | `work`, `gpus=0` |
| vLLM Commit (+FP8) | circuits | 1, 1 GPU | 4–8 vCPU, 6–192 GB | 1.5–15 min warm (+6 cold); ~500+, FP8 7→84 | clock-locked, recorded; not quiet | requeue, never mid-staging | Build dir, per-tree Triton/vLLM caches; out: a replay bundle of several GB | Kueue `deployments-gpu`, engine-key order | `work`, workstream `deployments-gpu`, `after` Build |
| Deferred replay | circuits | 1 or 2, CPU | 8–16 vCPU, ~64 GB | 5–16 min; one per config run | no | requeue | the bundle and Program | three-task template, off until PR A/B | `work`, `gpus=0`, `after` Commit |
| TP2 config run | circuits | 1, 2 GPUs on one host | 8 vCPU, 160–384 GB | unknown; 91 in all | recorded | requeue | TP2 weights | Kueue `config-run-row` | `work`, `gpus=2` |
| sm_120 capture / acceptance | circuits, red team | 1, 1 GPU | 4–16 vCPU, 192 GB | 1–20 min; a few | the clock probe is owner-run | requeue | small records | `submit.sh port-capture` (Kueue 1100) | `capture` |
| Build benchmarks | build-optimization | 1, CPU | 8–64 pinned vCPU | 25–50 min; a few | **quiet CPU** | freeze | private TMPDIR | direct `research run` | `bench`, quiet CPU (gap G5) |
| MoE manifest rebuild | circuits | 1, CPU | 256 GB class | unknown; per Definition change | no | requeue | — | train check, local Build | `work` |
| Lane checks (pytest, lints) | all vLLM lanes | 1, CPU | 16 vCPU, CUDA hidden | 15–45 min; several per PR | no | kill | repo tree | direct `research run` in check slots | `work`, `gpus=0` |
| Merge-train `check` (+`lean-agreement`) | old RC bc-8ece7cde | 1, CPU slots a/b/c | 32 vCPU, ~45 GB disk, per-slot cache | 15–45 min; ~25/day, up to 3 at once | no | **never** | tree in; 0.5–7 GB of run files | `launchv.sh`: `research run --on vy-nebius-1` + flock + taskset | pool `checks`, `preempt=never` |
| PR `check --record` (incl. #326's re-test, PoUW PRs) | PR owners, network-accounting, PoUW | 1, or 2's CPUs 128–191 | CPU slot | 12–80 min; a few + 3–8 PoUW | no; runs in node-2 windows today | rerun | tree; Attempt | `check.py --record --on …` | `work`, `gpus=0`, frozen in windows on node 2 |
| Lean build / audit / re-hash / lean-deps export | Lean lanes, PoUW bc-824e54a2, network, PoUS | 1 (PoUW's on agent VMs today) | 16–32 vCPU, lots of RAM | 10–60 min; ~3 re-hash + per Lean PR | no | may wait | `.lake` private per checkout; ~700 MB bundle | `research run` under a slot's flock | `work`, lock `lean-store` |
| M0 prover bench | proofs (M0 bc-ff572e70) | 1, 1 GPU | 18–32 pinned vCPU | 30–40 min; back to back | quiet hour 12:30–13:30Z; co-tenants recorded | **never** | small | Kueue ready files, `provers` | `bench`, workstream `provers` |
| Backend sweep (stage, then prove) | proofs (bc-62b7c7a1) | 1, 1 GPU | stage CPU; prove ~5 min per 10-shape chunk | ~2 GPU-h + 14 GPU-h approved | no | requeue (exit 99) | Llama-3.2-1B | Kueue ready files, `dev` | `fill`, stage `gpus=0` |
| Red-team reproductions | red team bc-f0bc7e75 | its pod | CPU | varies; rare | no | rerun | — | `research run` | `work` |
| Timed windows (panel, MVP serving, #593) | PoUW (bc-2aa33ad8) | **2 only**, all 8 GPUs | the owner's CPUs | ≤ 5.3 min measured (cap 20); 23 by 10:00 AM PDT | **timed**: clocks at 2,100 MHz, NVML-quiet, CPU paused | never once started | small; custody | `gpu-lease 8 --wait --timed` | `timed`, node 2 |
| Ranking kernel fill (forms grids, CUTLASS sweeps, autotunes, per-die baselines, `hsplit-*`) | PoUW | **2 only**, 1 GPU, `on=` die pins | 8 CPUs, ≤ 128 GB, ~13 GB GPU memory | ≤ 8 min chunks; hundreds (forms: 283) | ranks on node 2's clocks | requeue (SIGTERM, 30 s) | `/workspace/pouw/<lane>/out` | fill queue, `gpu-lease 1 --preemptible` | `work`, node 2, `max_s` ≤ 480 |
| Untimed GPU work (censuses, `fp8chain`/FP4 captures, rechecks, attacker searches, `aw-*` 70B) | PoUW | 2, or **1 as overflow** | 1 GPU, ≤ 20 GB GPU memory | 3–25 min; batches of 15–30 | no | requeue | a few GB per batch | fill queue | `work`; overflow `fill` on node 1 |
| 70B keyed-transform evals, FP4 coverage v4 | PoUW (bc-6289d8b0, bc-f5bf55c8) | 2, or 1 | 1–2 GPUs, 192 GB; a CPU half | 12-min chunks; a few | no | requeue if chunked | 70B weights, tens of GB | fill queue | `work`, `after` CPU prep |
| CPU verifies (window rows, rechecks, v2-hot) | PoUW | 2, CPU | 8–48 CPUs | 9–35 min; 10–30 | frozen in windows | freeze | node-2 window outputs | fill queue on 96–127; `research run` for the 48-process verify | `work`, `gpus=0`, `preempt=freeze` |
| Assessor leases | bc-d7d4b0d1 | 2, GPU 6/7 | 1 GPU | minutes | no | owner-driven | — | `gpu-lease` lock | `session` |
| Interactive kernel loops, live debugging | PoUW workers | 2, 1 GPU | exclusive | many short holds | sometimes a quiet die | owner-driven | local | `gpu-lease 1 --wait` over SSH | `session` (off the queue until G9) |
| PoUS harness timed audits | memory-accounting (paused) | any: 4090, L40S, H100, RTX PRO 6000 | **one whole GPU, exclusive** | 10–60 min; a few on resume | **timed** single GPU, SM clock readable | never mid-run | small | none yet | `timed`, 1 GPU (gap G5) |
| PoUS CPU reference encode | memory-accounting | any, CPU | ~2 GB per process | ≈ 3.1 core-h; rare | no | freeze | 14 GiB store | none yet | `fill`, `gpus=0` |
| Honest-trace run, jitter test | network-accounting (deferred) | 1 GPU (sized on L40S) + its NIC | host NIC | ~15 GPU-h in 5 h chunks; once. Jitter: < 1 h | **quiet, no freeze or SIGSTOP** | never | timestamps | none yet | `timed`, 1 GPU + NIC (gap G5) |
| Backups and staging (hourly `/workspace/pouw`, `n2_build` transfers) | node2-ops, kueue-fold | 2 ↔ 1 over `vy-cluster` | network, disk | hourly, 17.7 GB, 395 units | **exempt from the window pause today** | freeze | 60 MiB parts | `research run`, `rsync` | `stage`, frozen in windows (gap G2) |
| Node daemons (samplers, exporters, `verity-console.timer`, `cluster agent`) | node2-ops, console, infra | both | seconds of CPU | every 5 s to 5 min | quiet-safe | — | panels, ledger | systemd, tmux | `service`, `quiet_safe` (declared, not queued) [CO] |

**Keep off the queue for now:** clock and power experiments (bc-96a2e856), live debugging on a held GPU, and anything touching
`/workspace/pouw/gpu3-fp8` (517 GB, regenerable, never moved or backed up before v2-hot is rated) [OA D5], [OCv D].

## 3. Queue requirements, ranked

Status is checked against #586 at `1abe668f` and the live nodes. **GAP** names who closes it: cluster-build (CB), kueue-fold (KF), or the
research coordinator (RC) for `tools/research`, with CB carrying the ask.

**Must**

1. **One submit path.** `research run` puts a job on the central queue with a declared class, `gpus`, `cpus`, `mem_gb`, `max_s`,
   `preempt`, `quiet`, `node`/`gpu_ids`, `after`, `locks` and `pool` (criterion 1). **GAP (CB + RC):** the model has every field, but
   there is no `cluster submit`, and `research run` has no queue flag. Today it's `--on MACHINE` plus per-node side doors (the fill
   queue, `n2_build.sh`, `dispatch.py`, `submit.sh`).
2. **Timed windows get the whole of node 2 within 5 s, provably quiet.** GPU guests are evicted, CPU work is frozen, no NVML is
   polled, and a certificate is issued per window [OA C1], [CA C1]. Covered: planner rule 3 and the replay (all 26 windows within 1 s [CB]).
   **GAP (CB):** the agent-mode `gpu-lease` isn't deployed yet; custody uploads, backups and recorded checks aren't frozen as
   `stage` work; the run sampler still needs node 2's pause, not code (phase 1c, RC). **Owner's call:** does a one-GPU `--timed`
   lease get the whole node [CB]?
3. **Never hold a GPU through a CPU phase.** A `gpus=0` step, then the GPU step `after` it, with leased-idle reported per owner
   [OA C2], [OCv C1], [CA C3]. The `after` field is built. **GAP (KF):** Build on node 2 → Commit on node 1 is chained by hand in
   `n2_build.sh`; the deferred-replay template waits on PR A/B. **GAP (CB):** leased-idle doesn't reach the failure feed.
4. **No quota between a free GPU and waiting work, on both nodes.** Backfill every free GPU, reclaim within 30 s, and keep the
   workstreams (`provers` 3 GPUs that never borrow; `deployments-gpu` 5). Built in the planner. **GAP (KF):** node 1's executor
   only observes (`nebius1` snapshot); `Start`/`Evict` onto Kueue and the fallback to Kueue's admission aren't built, and neither
   is the guest runner on held idle GPUs [KFo].
5. **Custody before release.** Outputs are published and verified before an allocation or its scratch is reclaimed, in parts under
   64 MiB, with no failure on listing size; a failed publish is a feed event, never a lost result (criterion 6) [OA C8], [OCt C],
   [OCv C6]. **GAP (CB):** the agent has no release gate; **GAP (RC):** the manifest-size failure.
6. **Isolation per job.** An exclusive cpuset, a memory cap with no swap, CUDA hidden for `gpus=0`, private scratch and test cache,
   a clean environment (no host deadline or `LEASE_DIR`), content-keyed shared caches (per-tree Triton/vLLM, `.lake`, uv), and OOM
   victims by rank, guests first [OCt C], [OCv C4–5], [PLAN item 9]. Exclusive CPUs are built; node 2's guest scopes are live [N2].
   **GAP (CB)** for node 2's agent and **(KF)** for node 1's hostPath caches: scratch, clean env and per-tree caches.
7. **Keep node 2's contracts.** The `gpu-lease` alias and flags, the fill header, exit codes 0/99/143/75/124, retry once then
   `failed/`, `prio` with owners' turns, `on=` pins, `GPU_LEASE_WHO`, and frozen time not counted [CA C2], [OA C6]. Covered by the
   adapter and the agent-mode protocol (`652b12a4`), pending deploy.
8. **Failures surface with an owner.** Nonzero exits, evictions, expiries and idle leases reach `#agent-alerts` with a stderr tail
   (criterion 7) [OA A1b]. `cluster ledger failures` exists. **GAP (CB):** routing to Slack, the stderr tail, and node 1's Kueue
   events in the same feed.
9. **Session leases** for kernel loops and SSH debugging, visible in the queue (criterion 1). The model has `session`. **GAP (CB):**
   no `lease 1 --session` client.
10. **Visibility on target.** Hourly GPU and CPU busy per node, useful against filler, queue depth, and "missing work by owner"
    as `infra/*` panels (criterion 5) [OA C3], [CA C4], [CO]. `cluster ledger usage` exists. **GAP (CB):** no `filler` label on a
    job, no panel producer, and the `panels:write` key isn't requested yet.
11. **Placement.** Pin ranking and timed work to node 2, arm and baseline to one die, TP2 to one host, CPUs on the GPU's NUMA node,
    and record the die UUID and clocks per row [OA C5], [OCv C7]. Pins are built; node 2's NUMA map is in the description.
    **GAP (CB):** the planner doesn't prefer NUMA-local CPUs.
12. **Merge-train semantics.** 3 slots × 32 vCPU on CPUs 8–95, never preempted, the allocation recorded on the Attempt, and cancel
    by process group [OCt C]. The pool is built. **GAP (CB + RC):** allocation on the Attempt, and a clean cancel.
13. **A quiet single-GPU class for owners and guests** (PoUS audits, network's honest trace, M0's quiet hour, Build benchmarks'
    quiet CPU) [MA], [NA], [DES §2]. **GAP (CB + KF):** the planner forbids a quiet guest, and node 1 "never sees a quiet job" [CB].
14. **Commits in engine-key order**, so a hot worker reuses one warm engine [OCv C3], [CI]. **GAP (KF):** there's no engine key in the
    model; keep `dispatch.py`'s order behind node 1's executor, or add a key.
15. **Fast submit.** About 1 s to return, `logs -f`, stdin forwarded, and trees verified by git object ids [DES §4], [PLAN item 10].
    **GAP (RC):** phase 1c isn't built.
16. **Named locks** (`lean-store`) with waiters visible; **staging** as `stage` jobs, with the router preferring staged nodes;
    **declared sizes from measured peaks + 25%** [DES §3, §11, §16.15]. Modeled. **GAP (CB):** the executor doesn't enforce locks,
    there's no generic staging, and nothing feeds sizes back.
17. **A daily scan for unowned compute** on both nodes and RunPod (criterion 4). **GAP (CB):** not built.
18. **Rollback in one step per node, drilled** (criterion 8). Node 2: `cluster agent stop` [PLAN]. Node 1: the executor's fallback to Kueue.
    **GAP:** neither drill has been done.

**Must not**

- Change the freeze list before 7 Oct: the driver, CUDA and pinned toolkits, the clocks and power cap, `gpu-lease`'s name, flags and
  lock files, the fill header and exit codes, and the paths `/workspace/pouw/*`, `/workspace/hf`, the venvs and `/workspace/research/runs`
  [OA C]. bc-2aa33ad8's sign-off is **still owed** [OA B8].
- Run guests, samplers, checks, uploads or backups in a timed window; lend node 2's timed dies; move ranking or timed work to node 1.
- Poll NVML or DCGM from the brain on node 2, scan processes for lease state, or put the store or GitHub in the scheduling path.
- Hold a GPU for a CPU-only job, or require `gpu-lease` for one [OCt C].
- Preempt a merge-train check, an M0 bench, a started window, or a Commit mid-staging without a requeue.
- Share mutable caches or a writable `.lake` between concurrent jobs, or give a job write access to another tree's shipped copy.
- Change a job's recorded environment: `CUDA_VISIBLE_DEVICES`, the clock lock, `VLLM_BATCH_INVARIANT`, `VLLM_USE_DEEP_GEMM`,
  `CUBLAS_WORKSPACE_CONFIG` [OCv C].
- Run filler while useful work is queued, or start fill in filename order.
- Drop the `ov.*` / Attempt publication, or lose a finished result when publishing fails.
- Fail open: each node's self-stop and budgets stay independent of the queue.

**One open decision for infra:** verity-root's job service (`research jobs`, the Neon queue [JS]) is a second queue, and Daniel's ruling
6 [RUL] says trains move once "Job queue stage 1" runs a whole train. **Recommendation:** read that as the central queue, and make
`merge-check` a job kind on it, so there is one queue (criterion 1). Confirm with the RC.

## 4. Cutover order

The shadow (`r20260930-195806-59f3`) started at 12:58 PM PDT and runs to 8:58 PM PDT. The earliest point it can meet the 3 h and
6-window bar is 3:58 PM PDT. Guests must be out by 5:00 AM PDT on 7 Oct, and the nodes stop at 8:00 AM PDT that day.

| Wave | Workloads that move | Gate | Who moves them |
|---|---|---|---|
| **0: running now** | The node-2 shadow; vLLM Builds on node 2's guest pool (`n2_build.sh`); Verity CPU jobs through node 2's fill queue (`project=verity`) | Done [CB], [KF], [N2] | cluster-build, kueue-fold, node2-ops |
| **1: node 2 switches to the brain** | Everything on node 2 that goes through `gpu-lease` and the fill queue (windows, kernel fill, untimed GPU work, CPU verifies), with no change to how it's submitted | The shadow's pass bar (every window within 5 s, no safety divergence, footprint); a recorded `check` of #586; bc-2aa33ad8's freeze-list sign-off; the switch outside a window, with 15 min notice; a rollback drill in the first hour [PLAN step 4] | cluster-build builds it; node2-ops switches |
| **2: CPU batch through `research run` to the queue** | vLLM Builds (both nodes), deferred replays (after PR A/B), lane checks, PR `check --record` (#326 first), Lean builds and audits, PoUW CPU verifies, PoUS encode, red-team runs | Gaps 1, 5 and 6 for `gpus=0` jobs; one real job per lane (criterion 3) | each lane's coordinator (the onboarding pattern below); kueue-fold ports `n2_build.sh` |
| **3: untimed GPU work, requeueable** | vLLM Commits, TP2 and FP8; sm_120 captures; the backend sweep; PoUW's untimed GPU work, including node-1 overflow | Node 1's executor acts through Kueue with a fallback (gap 4), after a node-1 shadow; engine-key order and per-tree caches (gaps 14, 6); cross-node `after` (gap 3); an owner evicts a guest within 30 s | kueue-fold (node 1); circuits, proofs and compute-accounting switch their submits |
| **4: pinned and quiet-sensitive** | M0 benches (`provers`), Build benchmarks, node 2's ranking fill submitted to the queue directly, PoUS timed audits, network's honest trace | A quiet single-GPU class with co-tenants on the Attempt (gap 13); `provers` never borrows; bc-2aa33ad8 agrees for ranking fill | proofs, circuits, compute-, memory- and network-accounting |
| **5: merge trains** | Train checks, `lean-agreement`, re-hashes, lean-deps exports | The queue runs one full train end to end: recorded, `lean-agreement` passing, custody published, and accepted by `research merge`. `launchv.sh` stays as a fallback for one day [OCt D] | the RC, then infra takes the machinery [RUL 6] |
| **6: windows and sessions natively** | Timed windows as queued `timed` jobs, not the alias; kernel loops and debugging as session leases | After 7 Oct, or once the freeze list allows; the session client exists (gap 9) | compute-accounting with node2-ops |

## Onboarding pattern (any coordinator)

1. **Split and declare the job.** Put CPU prep in its own `gpus=0` job and keep the GPU step to GPU work only. Use GPU chunks of
   at most 8 min that exit 0 when done and 99 when more remain, and are safe to rerun from the top. Write results under `out/`.
   Declare your measured peak memory plus 25%, and pick the class from §2: a row's "Queue class" column is its answer.
2. **Submit through `research run`.** Once the queue takes your class:
   `uv run research run --queue --class work --gpus 1 --cpus 8 --mem-gb 64 --max-min 8 --preempt requeue [--node vy-nebius-2]
   [--after RUN] [--lock lean-store] --project verity --campaign C --source . --cwd source --declared-output 'out/*' -- CMD`
   (when cluster-build ships it). Until then, use the bridge for your node:
   - CPU work on node 2: node 2's fill queue with a `project=verity` header [N2];
   - Builds: `n2_build.sh submit KEY ITEM.json` [KF];
   - checks: `research run --on vy-nebius-1` as today.

   Timed or quiet runs also take `--no-sampler`. Never start a pod or a job by hand, and don't use `research jobs` for research
   runs.
3. **Watch it.**
   - Now: `research status RUN`, `research inspect RUN` and `research fetch RUN`.
   - When cluster-build ships them: `research logs -f RUN`, `cluster status` (queue position and holder), and
     `cluster ledger usage --since …` (held against busy time).
   - Subscribe to `#agent-alerts`. Your hourly "missing work" line and your panel are in `infra/*`.
4. **On a failure:** the failure feed posts to `#agent-alerts` with the owner, the exit code and a stderr tail (when cluster-build
   ships it). Evictions and exit 143 requeue by themselves. Any other exit is retried once, then held as failed. Read
   `research inspect RUN`, fix the job, and resubmit it; don't retry until it passes. A lost result, a job the queue won't place,
   or anything that looks like the queue's fault goes to a handoff in `lanes/infra/`. Rollback is infra's call.
5. **Report once.** After your first real job passes on the queue, add one line to your inventory note in `lanes/infra/` with its
   run id. That counts toward criterion 3.
