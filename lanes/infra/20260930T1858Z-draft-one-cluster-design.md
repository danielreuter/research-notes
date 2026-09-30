---
id: 20260930T1858Z-draft-one-cluster-design
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: pous one-cluster design (bc-c3ade0aa), handed to the infra coordinator (bc-17cc41f1)
---

> A copy of the pous Project store's `docs/infra/one-cluster.md` as of 18:58Z, for the infra coordinator,
> who owns the design from now on and can't read that store. Links into `/cursor/stores/...` point there.

# One cluster: vy-nebius-1 and vy-nebius-2 under one set of rules

30 Sep 2026, 17:45Z. Foundation built in [PR #586](https://github.com/danielreuter/verity/pull/586) (`tools/cluster/`), and
nothing on either node changed. The replies are folded in:
- Verity's policy, from the research coordinator (17:22Z);
- pous infra (17:21Z, 17:27Z);
- the RTX PRO coordinator (17:27Z).

The steward's workload answers (18:05Z) are folded in since 19:30Z by cluster-build (§2's node-1 rows, §8, §15, §16 item 15).
§16 lists what the replies changed.

## 1. Recommendation

**Run the two nodes as one cluster.** They share one description, one allocation ledger, and one feed of failures and GPU
use. Each node keeps its own scheduling authority.

- **The scheduler goes only where contention creates friction:**
  - GPU leases, whether queued or taken by hand over SSH;
  - quiet timed windows;
  - named locks, starting with the Lean store;
  - node deadlines;
  - making every run recorded and every failure visible.
- **SSH stays** for kernel inner loops, live debugging, probes and ops (Daniel, 16:51Z). A GPU touched by hand is still
  leased with one fast command, so windows, reclaim reports and the ledger see it.
- **Observability is report-only.** Held time against busy time per GPU goes to the holder at release and into the store,
  and failures go to one feed. Nothing is killed or refused for being idle. Chronic idle time gets structural fixes:
  preemptible fill on free GPUs, and CPU preparation in a GPU-less step.
- **Build the small core** whose semantics are ours: the description, the planner and the ledger (done in #586), then a node
  agent and a router. **Adopt** Linux cgroups and systemd for isolation, OpenSSH for access and connection reuse, and our
  evidence store for records. **Don't adopt** Slurm or multi-node Kubernetes now (§9).
- **Verity's resource model should express** the physical layer, the allocations (the realized schedule) and attribution,
  such as "nothing else ran on this node during this window". It shouldn't express the scheduling policy (§5).

**Trade-offs.**
- Per-node authority costs global optimality. The router only picks a queue, so a job may wait on one node while the other
  frees up, until it is re-routed.
- Keeping SSH costs completeness. Work run by hand without a lease is invisible, which is why GPU access by hand goes
  through a lease.
- Report-only utilization costs enforcement. A holder who ignores the report keeps idling, and the fix is social and
  structural, not a kill.
- Building our own planner costs maintenance that Slurm wouldn't. We get our semantics (quiet windows that freeze rather
  than kill, frozen time not counted, hard node stops, evidence per allocation) as tested code, not glue.

**First step before 7 Oct: nothing on a node changes behaviour.**
1. `gpu-lease` reports per-lease held and busy time. The spec went to its owner (the nebius-infra steward); pous infra
   (bc-efe47341) is shipping it on `infra/nebius` now, in the ledger's record shape (17:27Z).
2. Shadow runs: a read-only snapshot of each node's leases and queues goes through `cluster plan` every few minutes, and the
   planner's decisions are compared with what happened. Pous infra said yes for node 2 on conditions (§14); node 1 waits on
   the steward.
3. `research run` gets SSH connection reuse and streamed logs. §4's measurements show a submit falling from 5.4 s to about
   1 s.

Any cutover is a written plan that goes to Daniel first.

**What Daniel must decide.** The research coordinator marked five points **(Daniel)**, each with today's practice as its
default. This is how they map onto the design's four decisions:
1. **Borrowing across nodes.** Two of the coordinator's points land here:
   - **(Daniel) the GPU half of cross-node borrowing.** Default: yes both ways, preemptible only, never during node 2's
     windows, and node 1's reserved CPUs (0–95) are outside the pool. Today only CPUs are shared.
   - **(Daniel) whether Verity gets a standing share on node 2.** Default: none, only idle capacity.
   - The RTX PRO coordinator adds a limit: PoUW's overflow onto node 1 only for work that neither ranks nor times sm_120
     kernels, meaning censuses, captures, quality evals, CPU verifies and Lean.
2. **Cutover appetite before 7 Oct.** The coordinator doesn't address it. The RTX PRO coordinator asks to switch after 7 Oct,
   or keep `gpu-lease` as a working alias, and names what must not move before then (§16, item 12). **Recommendation:**
   shadow only before 7 Oct.
3. **Identity. (Daniel) holds the CA key,** not an agent or root. The coordinator says yes to short-lived per-agent
   certificates, with submission as the only command for Verity's agents, and wants one break-glass path for the steward.
   Daniel's part is to confirm and to hold the key.
4. **Node 1's Kueue.** No reply addresses it; still open.

A fifth deferred point sits outside the four: **(Daniel) any machine after 7 Oct,** such as a new node or provider. The
design doesn't depend on it (§14's last row).

## 2. Requirements

Gathered from:
- the compute plan, and pous infra's 16:29Z interim terms;
- today's `lanes/nebius-infra/` and `lanes/node1-dispatcher/` notes, `kueue.yaml`, and the lessons log;
- PR #577's kernel skill, and §4's measurements;
- the replies: the research coordinator (Verity's policy), pous infra, and the RTX PRO coordinator
  (`internal/pouw/infra/one-cluster-rtx-pro-answers.md`).

- the steward's node-1 workloads and node facts (`note:20260930T1805Z-reply-from-nebius-infra-steward-to-pous-one-cluster-requirements`).

| Workload | Shape | What it needs | What hurts today |
|---|---|---|---|
| Timed windows (node 2, the PoUW panel) | 8 GPUs, allowed ≤ 20 min. Measured: 23 windows to 17:00Z, each ≤ 5.3 min, gaps 2–96 min (typically about 20) | Start within seconds. A quiet node: no CPU load on any core (measured: the other socket biases decode 0.26–1.35%); no NVML queries (assumed, no A/B yet); fill stopped, not paused. Arm and baseline interleaved on one die. Clocks locked at 2,100 MHz and recorded per rep | Quiet is a convention, not a check. `research run`'s own sampler polled `nvidia-smi` every 5 s inside all 31 runs behind published rows, including 8 windows, until 17:25–17:27Z. Custody uploads aren't paused |
| GPU screens and fill | 1 GPU, ≤ 8 min chunks (`max_min` ≤ 30); exit 0 (done), 99 (more), 143 or -15 (preempted, requeued), 75 (no GPU), 124 (at `max_min`) | Preemption within 30 s; GPU jobs killed, not frozen (a stopped job keeps its GPU context); checkpointed restart; GPU-heavy work first; pinning to one die for arm/baseline pairs (dies differ by up to 0.7%) | CPU preparation inside GPU leases: 2.8 GPU-h leased-idle in one hour. Node 2 was 32% busy at 15–16Z and 38% over the last hour |
| Kernel inner loops (GPU 0's co-issue probes, GPU 1's mainloop) | 1 GPU, edit-compile-run in seconds, for hours | Direct SSH; a die held across iterations; sometimes a quiet die | A "keep-free" hold idled 0.91 GPU-h, 11% of the node |
| Live debugging (ncu, cuda-gdb, a hung verify) | the running process | Direct access to the process and its GPU | Key material decoded by hand to reach a box (bc-dd22acf8) |
| Probes (caches, revisions) | read-only | Direct SSH | none reported |
| vLLM deployments (node 1) | Build CPU (≈ 6 min, peak ≈ 125 GB); Commit GPU (7–10 min, 137 GiB host memory at batch 8); replay CPU | Chaining (Commit after Build), containers, host memory at the measured peak plus 25% | GPUs held through CPU Builds (7.1 GPU-h allocated, 0.07 busy, in one hour); memory over-requested; one host-wide bootstrap lock |
| Prover benches (M0, flock) | 1 GPU plus 32 pinned vCPU; `provers` owns 3 GPUs and never borrows | Second in Verity's order; never evicted mid-run; a quiet hour (12:30–13:30Z); co-tenants recorded, since co-tenancy decides whether a timing counts | Evicted twice as borrowers by a reclaim; results corrupted by overlapping CPU pins |
| vLLM Build, Commit, replay (node 1, the steward's 18:05Z sizes) | Build: 0 GPU, requests 4 vCPU and uses 2–9, 50–240 GB (a batch-1 4k Build up to ~486 GiB), 4–28 min, dozens a day. Commit: 1–2 GPUs, 4 vCPU per GPU, ~6 GiB below batch 8 and ~130 GiB at 8+, 83 s–10 min. Replay: 0 GPU, 8 vCPU, the bundle's size, 6–16 min | Declared sizes that match use: CPU requests run about 4× use, and memory is off both ways (a Commit asked 192 GB and used 6; a 4k Build asked 32–48 and used 100–127) | Admission blocked while the node was 70–85% idle |
| Port captures (node 1) | 1 GPU, 4 vCPU, 192 GB; 49 s cached, up to ~15 min | First to a free GPU in `deployments-gpu` (Kueue 1100) | none reported |
| Merge-train checks | three 32-vCPU slots on node 1's reserved CPUs 8–95; toolchain pinned (`UV_PYTHON=3.14.7`); warm verdict packs and Lean deps | First in Verity's order, on CPUs nothing else may use even when idle; never preempted, never borrowed; a private scratch area and cache per job | A per-test cache that concurrent checks race on; fixtures reading the host's real builds and deadline; uncoordinated CPU pins |
| Backfill (node 1) | invariance sweeps, then backend-sweep shapes | Last in Verity's order, preemptible, requeued on exit 99; runs on any idle GPU | Node 1 at about 2% GPU busy. Quota rules keep backfill from borrowing: 15 workloads waited while GPUs 1–3 idled (16:47Z) |
| Lean builds and audits | CPU- and RAM-heavy (Mathlib) | One build into the pinned store at a time, in a priority order kept by hand today (FP8 first, 14:45Z); `.lake` never shared by two agents | The order lives in prose |
| CPU work (censuses, replays, Verity's Builds on node 2) | 8–32 vCPU, ≤ 256 GB each | A pool of its own, `nice 19`, paused in windows, gone before the stop | Node 1's RAM 93% reserved; the node-2 ask needs a new SSH key |
| Data | node 2 at 17:04Z: `/workspace/hf` 163 GB of weights; caches 28 GB; runs 89 GB; shipped trees 28 GB; GPU 3's regenerable flags 517 GB; fill outputs 61 GB. A tree is 4,044 files | Content-addressed caches, staging before GPU time, uploads under 64 MiB each | Custody multipart uploads stalled for over an hour; the disk grew 31 GB/min |
| Evidence | every run an Attempt | Named lease holders; per-lease use; quiet evidence for timed rows | Lease holders unnamed early on; nothing ties a row to its window's quiet |
| Lifetimes | both nodes stop 7 Oct 15:00Z (node 2 clamps at 14:55Z) | Admissions end before final backups (09:00Z, 13:30Z); guests out by 12:00–13:30Z; the node's self-stop never depends on the scheduler | Replanned by hand when the stop moved |
| Access and credentials | a shared research key on every node and VM | Scoped identities, no ad-hoc node-to-node keys, no IAM change without Daniel; a break-glass path for the steward | Two key-fragment exposures today. GitHub tokens lapse hourly (a broker is rolling out). The store's mount is slow (EAGAIN, slow scans). `research pods ssh` forwards no stdin, so staging files takes `scp` or inline base64 |
| Coordination | about 8 kernel lanes on node 2 | Asks that reach workers directly | Workers read only `server.md`, so every ask goes through the RTX PRO coordinator. The fill queue runs dry within minutes of a lane's turn ending: hours from 11:00Z ran 44, 72, 72, 93, 32 and 38% busy |

## 3. Where the scheduler sits, and where SSH stays

Daniel's 16:42Z principle ("everything is a batch job") was tested against these requirements. It breaks on the three
kinds of work that live on the box: inner loops, live debugging and probes. At 16:51Z he chose velocity instead: keep SSH
where it's fastest, and put the scheduler where it removes friction.

| Activity | Path | What the scheduler adds |
|---|---|---|
| Kernel inner loop | SSH, then a lease (planned: `lease 1 --session --max 2h`, today's `gpu-lease 1 --wait`): a session allocation granted in milliseconds when a GPU is free | It appears in the ledger. A timed window evicts it when it's preemptible, and otherwise waits for it up to its `max`. It's named when idle, never killed for it |
| Live debugging | SSH to the process, inside the lease it already holds | The lease's record says who held which die when |
| Probes | SSH, read-only, no lease | none |
| Ops and repair | SSH; `admin begin/end` (planned) writes a ledger record | Quiet reports see the repair; a window overlapping it isn't certified quiet |
| Queued runs: fill, censuses, replays, Builds, checks, Lean | `research run --on <node>` into the node's queue (planned; today the fill queue and Kueue): a recorded Attempt | Placement, preemption, backfill, locks, deadlines, the failure feed |
| Timed windows | a queued quiet job | Exclusive, quiet, reserved, certified by the ledger |
| The node's daemons (sampler, exporters, the agent) | systemd units, declared as quiet-safe services | They keep running beside windows because they're declared quiet-safe |

**The friction to remove, specifically:**
- **The Lean lock** becomes a named lock, `lean-store`. Priority classes set the order, and waiters see their position and
  the holder. A dead holder releases it, since the kernel drops the lock with the process. Warm `.lake` caches are keyed by
  toolchain and manifest and copied per job, so no two agents share a writable one.
- **Idle leases** are reported at release and while held. The fixes are structural: fill backfills every free GPU and
  yields in seconds, and a job's CPU preparation runs as a GPU-less step that the GPU step follows (`after`).
- **Recorded runs and visible failures:** every queued job is a `research run`. The ledger's failure feed lists nonzero
  exits, expiries, evictions, refusals and idle leases, each naming the job, the submitter and the node.

**Speed, so nobody routes around it.** Submission should return in about a second, with the tree synced and caches hot:
- **One persistent SSH connection per agent VM.** A multiplexed command costs 0.30 s against 1.7 s for a fresh one (§4).
- **One round trip to submit,** and logs streamed over the same connection (planned: `research logs -f`). Results come back with
  `research fetch`, so nobody SSHes in to tail or scp.
- **Warm per-agent environments on each node:**
  - a worktree per agent, updated by git objects and verified by their ids, rather than 4,044 per-file hashes;
  - a uv venv keyed by lockfile. Warm, it installed 35 packages in 31 ms (§4);
  - `.lake` keyed by manifest, and the vLLM bootstrap keyed by tree, both of which exist today.

## 4. Measured: `research run --on vy-nebius-2` today

Run at 16:52–16:55Z, from a Cursor cloud VM, with `--no-sampler`. Each run was gated on node 2 being out of a timed window
(`fill/status.txt`: `timed False`). The workload printed one line. "First output" means visible on the submitting VM through
`research fetch --all`.

| Case | Launch returns | First output visible | Runs |
|---|---|---|---|
| SSH round trip, fresh connection | 1.65–1.99 s | – | 6 |
| SSH round trip, multiplexed (ControlMaster), after the first | 0.30 s | – | 6 |
| `research run`, no source tree | 5.37–5.49 s | 10.78–10.87 s | `r20260930-165247-44b3`, `-165300-da5a`, `-165312-3443` |
| `--source`, a new commit (4,044 files) | 20.04 s | 25.59 s | `r20260930-165325-c7a9` |
| `--source`, the same commit again | 7.14–7.20 s | 12.64–12.74 s | `r20260930-165353-983f`, `-165407-9bec` |
| `--source --cwd source`, `uv run --locked` in a fresh tree | 7.08 s | 12.59 s (0.62 s in the workload: built the members, installed 35 packages in 31 ms) | `r20260930-165421-f5c6` |
| the same, warm venv | 7.19 s | 12.89 s (0.11 s in the workload) | `r20260930-165436-36f7` |

**Reading:**
- The time is transport, not work. A launch takes about three fresh SSH connections' worth (5.4 s at 1.7 s each; the tool
  opens a new connection per step), and seeing the output takes another full fetch.
- A new commit costs 13 s more, mostly verifying all 4,044 files.
- uv is already fast.
- **The fixes:** connection reuse brings a launch to about 1 s and the output to about 1.5 s; streaming logs removes the
  fetch; verifying by git object ids brings a new commit down to seconds (an estimate, not measured).
- **Not measured:** a cold tool snapshot (a changed `research` package), and runs from a laptop.
- **One finding for the research tool:** every `research run` samples `nvidia-smi` every 5 s by default, which is NVML during
  a window. On a node with windows, the harness should skip GPU samples while a `--timed` lease is held, as node 2's own
  sampler does.

## 5. The model, in Verity's resource terms

The cluster's description and ledger use the resource ontology's physical-layer vocabulary
([resource ontology](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/verity-resource-ontology.md) §1–2):

| Ontology term | Here | Code (#586) |
|---|---|---|
| device, capacity | a node's GPUs by NUMA node, its CPUs less the system's, its memory | `model.Node`, `Gpu` |
| window, and the devices present in it | the node's life to `stops_at`, and its admission end (stop less drain) | `Node.stops_at`, `admission_ends` |
| events | starts, freezes, thaws, evictions, expiries, ends, admin sessions | `ledger` record kinds |
| schedule (declared) | the realized schedule at allocation granularity: job → node, GPUs, CPUs, memory, intervals | `Allocation`, `ledger.history` |
| attribution | "nothing else was active on node X during window w" | `ledger.quiet_report` |
| capacity evidence, gaps | the sampler's readings; unsampled time is held, never idle | `ledger.gpu_usage` |

**The answer to "is this what Verity's resource model should express": partly.**
- **Yes:** the physical description, the allocation record and attribution. Those are exactly its devices, windows, events,
  schedule and attribution, and our own cluster is a real consumer for `verity.resource_accounting` once it lands. A timed
  row's "the node was quiet" becomes an attribution statement, backed by a trusted operator's ledger and the sampler's
  observations.
- **No:** standing, priority, shares, preemption and backfill. They are operator policy, not claims to verify, and stay in
  `tools/cluster`.
- `tools/cluster` stays stdlib-only and imports no core module. An exporter to `resource_accounting`'s shapes comes with that
  module.

**The concepts:**
- **Cluster:** nodes, priority classes, and shares.
- **Node:** an owner, GPUs by NUMA node, CPUs by NUMA node, system CPUs, reserved CPU pools, memory, stop time and drain.
- **Share:** what a project may hold on a node it doesn't own: allowed CPUs, caps on GPUs, CPUs, memory and jobs, a per-job
  memory cap, and an end time.
- **Job:** one of four kinds:
  - `batch`: GPU, CPU or Lean work;
  - `service`: no `max_s`, stopped only by the node's stop;
  - `session`: a lease taken by hand;
  - `stage`: data movement.
- **What a job declares:** `preempt` (`never`, `freeze` or `requeue`), `quiet` (needs its node quiet), `quiet_safe`
  (services only), `max_s` (required except for services), `locks`, `inputs` (content ids that must be staged), `after`
  (jobs that must end well first), GPU pins, and a CPU `pool`.
- **Allocation:** exact GPUs, CPUs and memory on one node, running or frozen, with its frozen time accounted.

## 6. Components

1. **Description** (`tools/cluster/descriptions/nebius.toml`): both nodes and the interim share. It's validated in tests.
2. **Planner** (`cluster.plan`, built): a pure function per node, with seven rules, each tested (§7).
3. **Router** (`cluster.route`, built): picks the queue a job enters, in this order: where it starts now (its owner's node
   first), then its owner's node, then where its inputs are staged. A node keeps its queue when the router is down.
4. **Ledger** (`cluster.ledger`, built): append-only and hash-chained, with quiet reports, per-lease usage and the failure
   feed. The node agent publishes it to the store hourly and at drain.
5. **Node agent** (next, one per node, a systemd service):
   - It runs the planner on each event, or every second at most.
   - It carries out the plan with systemd transient scopes (`AllowedCPUs`, `MemoryMax`, no swap), the cgroup v2 freezer for
     freeze and thaw, and SIGTERM, then SIGKILL after 30 s, for eviction.
   - GPUs go by `CUDA_VISIBLE_DEVICES`, by UUID, plus a device policy.
   - It writes the ledger, and serves `lease`, `submit`, `status`, `logs -f` and `admin` over SSH.
   - Today's `gpu-lease`, with its flags `--wait`, `--timed`, `--preemptible` and `--max-min`, becomes its client, so
     workers keep their commands.
6. **Transport and identity** (next):
   - OpenSSH connection reuse for every client;
   - certificates per agent from one CA, with shell or queue-only principals (§10).
7. **Data** (next): content-addressed node caches (trees, weights by repo and revision, uv, `.lake`), staging jobs, and
   placement that prefers staged nodes (§11).

## 7. Quiet windows, fill and borrowing together

The planner's rules (`plan.py`), checked on every tick of seeded random workloads over this description
(`tests/test_simulation.py`):

1. **Exclusive resources.** No GPU, CPU or lock is in two allocations, and memory is never overcommitted. A guest's CPUs
   come from its share.
2. **Standing, then priority.** On its own node, an owner's job outranks every guest's. Only a strictly higher rank evicts,
   and only a `requeue` allocation. A guest must be preemptible and may not be quiet.
3. **Quiet jobs:**
   - GPU-holding work is evicted, because a frozen CUDA context still holds its GPU.
   - CPU work is frozen and thawed afterwards.
   - Only a quiet-safe service keeps running.
   - Work the window may not stop (a `never` session, an equal rank) makes it wait.
4. **Reservation and backfill.** The highest-ranked blocked job with a known start reserves its node. Lower jobs start ahead
   of it only if they end first or it may evict them. That is the fix for "7 GPUs idle behind one lease", and for a
   whole-node request being starved.
5. **Deadlines.** Nothing is admitted past its node's admission end or its share's end. Time spent frozen doesn't count
   against `max_s`. The admission end is a hard cut for everything but services.
6. **Fair turns:** among equals, the submitter with the fewest allocations goes first. That fixes node 2's filename-order
   starvation (10:53Z).
7. **Idle leases** are named, never acted on.

The simulation found two real bugs, both fixed with tests:
- frozen time counted against `max_s`, so jobs frozen through windows expired;
- back-to-back windows re-froze a frozen job and lost its frozen time.

On the Nebius description, all 120 jobs of each seed finish, and the runs include quiet windows, freezes, thaws, evictions
and guest work.

## 8. Priorities, quotas and cohorts

- **One cohort: the cluster.**
  - A node's owner has the whole node as its nominal quota.
  - Borrowing is by explicit shares, with caps and an end time.
  - Reclaim is by standing: an owner's job evicts a guest within about 30 s.
- **Priority classes,** highest first: `service` 1000, `timed` 900, `session` 700, `work` 500, `dev` 100, `fill` 10. They
  order jobs within a standing, and ties go by submitter turns, then age.
- **Verity's order on node 1** (the research coordinator), highest first:
  1. merge-train checks, on reserved CPUs;
  2. M0's pinned prover benches;
  3. vLLM deployments (GPU generation, then CPU checking);
  4. captures;
  5. backfill: invariance sweeps, then backend-sweep shapes.

  In the design:
  - Checks aren't a priority but a **reserved pool:** CPUs 8–95, which nothing else may use even when idle.
  - The rest become classes: a `bench` class between `session` and `work`, deployments at `work`, a `capture` class below
    `work`, and backfill at `fill`.
  - This isn't the live `kueue.yaml`'s order, which puts captures (1100) above deployments (600 and 500) and prover benches
    at 300. The steward should say which one is policy.
- **Workstream shares inside an owner** are now a requirement:
  - `provers` owns 3 GPUs and never borrows;
  - `deployments-gpu` owns 5, borrowable but not kept (Kueue lets it borrow 2).

  Work beyond a queue's own GPUs is borrowed, and the lending queue's jobs reclaim it whatever their priority. So the rank
  gains a term: standing, then within-share, then priority. **Built** in #586 (`42311e84`): `[[workstreams]]` in the
  description, `borrow_gpus` as Kueue's `borrowingLimit`.
- **Node 1's 2% GPU busy is what this model fixes directly.** Kueue's backfill queue had no quota of its own and couldn't
  borrow while CPU quota was held elsewhere. Here there is no quota arithmetic between an idle GPU and backfill: a free GPU
  is free, a `fill` job takes it, and anything that outranks the fill evicts it within about 30 s.
- **One rule is looser than today's.** A guest may backfill idle capacity even while the owner has work queued, because it
  is always evictable by that owner. Node 2's rule today admits Verity's work only when no pous job is queued.

## 9. Build versus adopt

| Piece | Decision | Why |
|---|---|---|
| Planner, router, ledger | **build** (done in #586) | Small (about 1,100 lines with the model and CLI, 650 of tests), pure and tested. The semantics are ours: windows that freeze rather than kill, frozen time not counted, hard node stops, share caps, and evidence per allocation |
| Node agent | **build** | A thin executor over systemd and cgroups; today's `gpu-lease`, fill runner and `node_ops.py` already do half of it |
| Isolation: cpusets, memory caps, freezer, device policy | **adopt** Linux cgroup v2 via systemd | Already how `gpu-lease` caps memory; the freezer is atomic where SIGSTOP of process groups isn't |
| Access and transport | **adopt** OpenSSH certificates and ControlMaster | No new daemon or port; certificates carry principals, validity and forced commands |
| Records | **adopt** the evidence store and `research run` | Already every run's custody |
| Dashboards | **keep** Grafana and Prometheus on node 1 | The ledger is the source for allocation facts |
| Slurm | **not now; the named alternative** | It expresses most of this: QOS, suspend and requeue preemption, reservations, licenses for locks, cgroups, accounting. But it needs root daemons and munge on live nodes, ports between nodes (the security groups allow only 22), and every workflow moved to `sbatch`/`srun` mid-series. Its suspend keeps GPU contexts resident, and its accounting sits outside our evidence store, so glue is needed either way. Revisit past about four nodes or across providers |
| Multi-node Kubernetes and Kueue | **no for node 2; keep on node 1 as a container runtime** | The GPU operator's DCGM exporter polls NVML, which breaks quiet windows; containers bring uid friction; joining needs new ports. On node 1, Kueue's quotas fold into the description's shares once the node agent owns GPUs |

## 10. Identity and access

- **Today:** one research key on every node, agent VM and pod, and two fragment exposures today. The steward's ask would add
  a node-1-to-node-2 key.
- **Proposal: one OpenSSH user CA.**
  - Every agent gets a certificate: its principal is its lane or agent id, and it's valid for hours.
  - Two kinds:
    - **shell** certificates, for inner loops, debugging and probes;
    - **queue-only** certificates, whose forced command is the node agent's `submit` / `status` / `logs`, with no forwarding.
      These are for a dispatcher or router reaching another node.
  - That replaces the node-to-node key: node 1's dispatcher gets a queue-only certificate for node 2.
- **Separation on the node:** per-project Unix users (`pous`, `verity`) separate data directories and quotas.
- **Credentials:** R2 custody stays as today, a delete-free key minted per run.
- **Needs Daniel:** the research coordinator's answer is that **Daniel holds the CA key**, not an agent or root; he confirms.
- **Verity's agents** get queue-only certificates by default, submission being the only command the coordinator wants for
  them.
- **POUS's kernel lanes** get shell certificates, for the SSH workflows Daniel kept (16:51Z).
- **Break-glass for the steward:** a separate principal for node repair. Every use writes `admin-begin` and `admin-end` to
  the ledger, so no quiet window is certified across it.
- **Node change at cutover only:** `TrustedUserCAKeys` in sshd. No Nebius or IAM resource changes.

## 11. Data and weights

- **Content-addressed caches per node:**
  - trees, by commit, in one bare repo per node (git's object ids verify content);
  - weights, by repo and revision, with file hashes;
  - the uv cache;
  - `.lake`, by toolchain and manifest, copied per job.
- **Staging:** a job's `inputs` must be staged on its node before it starts. Staging is a `stage` job: CPU- and
  network-bound, frozen during windows. The router prefers nodes that hold the inputs.
- **Between nodes:** pull over the private network if intra-subnet traffic is allowed (asked, §12), else from the origin (HF,
  R2).
- **Outputs:** go to the store in parts under 64 MiB (the 10:32Z stall). Regenerable outputs are declared, and kept until
  rated, never backed up (the root's 15:27Z rule).
- **Guest data:** lives under a quota'd directory (node 2's interim terms: `/workspace/verity-cpu`, 800 GB, removed by
  13:30Z on 7 Oct). A filesystem project quota should replace today's `statvfs` gate at 55% (pous infra).
- **What node 2 holds, by kind** (17:04Z, 20% of 4.9 TB):
  - re-fetchable but slow: weights (163 GB);
  - regenerable: caches (28 GB), shipped trees (28 GB), and GPU 3's flags (517 GB, never backed up);
  - must be preserved until custody verifies them: runs (89 GB) and fill outputs (61 GB).
- **The HF cache** needs `refs/main` beside a checkpoint held by revision, or offline loads fail (fixed at 17:18Z). A
  staging job should write both.

## 12. Evidence and observability

- **Every queued job is a recorded run.** Its Attempt gets its allocation: node, GPU UUIDs, CPUs, memory cap, co-tenants and
  frozen intervals.
- **The ledger** is published hourly, and verifies (`cluster ledger verify`).
- **Per-lease GPU use:**
  - At release, the holder sees held time against busy time per GPU. The record goes with the run's Attempt, or to the
    node's lease log for leases outside a run.
  - Busy comes from the node's sampler, never from NVML queries by the lease, so windows stay quiet. Unsampled time (a
    window) counts as held, not idle.
  - `cluster ledger usage` ranks holders by busy share for panels and the scheduler. It's **report-only.**
  - A minimal version is with `gpu-lease`'s owner now (`note:20260930T1713Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-gpu-lease-usage`).
    It's the only planned check for CPU preparation inside GPU leases (#577).
- **The failure feed** (`cluster ledger failures`): nonzero exits, expiries, evictions, refusals and idle leases, each naming
  the job, the submitter and the node. It goes to the lane channels the way node 1's Grafana alerts do today.
- **Quiet certificates** (`cluster ledger quiet ALLOC`): what else was active during a timed window, and whether an admin
  session overlapped. A panel row cites it. From the replies, a certificate also records:
  - whether the run's own sampler was off (the RTX PRO coordinator);
  - whether any upload ran.
- **Co-tenants for every timing job,** not only whole-node windows. The research coordinator: co-tenancy decides whether a
  timing counts, and overlapping CPU pins corrupted M0's and the Build's benches. The planner makes pin overlaps impossible,
  since every allocation's CPUs are exclusive. The Attempt still lists who else ran on the node and on its NUMA node.
- **The store is slow at times,** so nothing in the scheduling path reads or waits on it (the research coordinator's third
  pain):
  - The ledger is a local append-only file.
  - Publishing is retried and resumable, in parts under 64 MiB.
  - A failed publish is a report in the failure feed, never a block.
  - The node agent needs no GitHub token, since trees arrive over the research tool's git transport.

## 13. Node lifetimes

- **Stops:** each node's `stops_at`, less a drain for final backups and custody, is its admission end. No job is admitted to
  run past it, and every non-service allocation is cut there.
- **Shares** end earlier: Verity's on node 2 at 12:00Z on 7 Oct.
- **The node's own self-stop** (`lease.sh`, the deadline file) never depends on the scheduler: a guard never fails open.

## 14. Phased plan

| Phase | What | Node change | Gate |
|---|---|---|---|
| 0 | Model, planner, router, ledger, CLI, the Nebius description, simulation tests (#586) | none | done |
| 1a | `gpu-lease` per-lease usage report | small, on `infra/nebius` | pous infra shipping it (17:27Z); the commit and deployed sha256 to follow |
| 1b | Shadow runs: read-only snapshots of `gpu-lease status`, the fill queue and Kueue workloads through `cluster plan`; divergences reported hourly | read-only jobs | Node 2: pous infra's yes, if the job reads only `gpu-lease status`, `/run/gpu-lease/*`, the fill queue's status and folders and the sampler log; runs with `--no-sampler`; skips while `timed True`; stays at `nice 19`. Node 1: the steward's yes pending |
| 1c | `research run`: SSH connection reuse; a one-round-trip submit; `logs -f`; stdin forwarded, so staging a file needs no `scp`; verification by git object ids; and the sampler skipping GPU and PSS reads while a `--timed` lease holds every GPU, recording `timed: true` (the RTX PRO coordinator's 17:28Z ask), which retires node 2's 17:25Z sampler pause | none (tools/research) | the research coordinator's review |
| 2 | Node 2: the node agent replaces `gpu-lease`'s internals and the fill runner, between panel series; ledger live; quiet certificates on timed rows | yes | **a written cutover plan, to Daniel.** After 7 Oct, or earlier only with `gpu-lease`, its flags and lock files kept as a working alias and nothing on the freeze list (§16, item 12) moved |
| 3 | Node 1's GPUs under the node agent, with Kueue as the container runtime; the router live; `lean-store` via the agent; the SSH CA | yes | **Daniel** |
| After 7 Oct | The same description for the next machines. A RunPod pod has no systemd, so the agent there runs plain process groups and records its isolation as best-effort | – | – |

## 15. Pending

- **Which priority order is policy on node 1** (§8): asked of the steward again at 19:30Z
  (`note:20260930T1930Z-handoff-from-cluster-build-to-nebius-infra-steward-priority-order`).
- **Answered:**
  - the steward's workloads and node facts (`note:20260930T1805Z-reply-from-nebius-infra-steward-to-pous-one-cluster-requirements`):
    only TCP 22 passes between the nodes, even inside the subnet;
  - Verity's policy (`note:20260930T1722Z-reply-from-verity-root-to-pous-one-cluster`);
  - pous infra (`note:20260930T1721Z-reply-from-pous-infra-to-pous-one-cluster`,
    `note:20260930T1727Z-reply-from-pous-infra-to-pous-one-cluster-phase-1`);
  - the RTX PRO coordinator (`internal/pouw/infra/one-cluster-rtx-pro-answers.md`).
- **An A/B of NVML polling in one window** would turn "assumed" into measured. The RTX PRO coordinator offered to queue it
  given a script.
- **Node 2's GPU-to-NUMA topology** is assumed to match node 1's until someone reads it.
- **Whether a window should give a session a grace period** before evicting it, or skip its die, is open. Today a
  preemptible session is evicted and a `never` one makes the window wait.

## 16. What the replies changed

1. **Reserved CPU pools (§8).** Node 1's CPUs 8–95 hold the train-check slots: never preempted, never borrowed, never used
   by anything else even when idle. The model gains node pools, named CPU sets that only jobs naming the pool may use.
   **Done** in #586 (`24ae54f3`): node 1's description reserves `checks = "8-95"`, and the simulation checks every tick that
   pool CPUs go nowhere else.
2. **Workstream shares inside an owner (§8).** `provers` owns 3 GPUs and never borrows; `deployments-gpu` owns 5. Borrowed
   capacity goes back when the lending queue's work arrives. The rank gains a within-share term. This is the next planner
   slice.
3. **Verity's cross-project order for node 1 (§8).** It conflicts with the live `kueue.yaml` on captures and prover benches,
   and the steward should say which one is policy.
4. **A private scratch area and cache per allocation, and a declared CPU set (§6's node agent).** This answers the
   research coordinator's second pain, shared-host interference in checks. The declared CPU set is already the planner's
   exclusive allocation.
5. **Tolerate a slow store (§12).** The ledger is local-first, publishing is retried, and nothing waits on the store. No
   GitHub token is needed on the node.
6. **Identity (§10).** Daniel holds the CA key. Verity's agents get queue-only certificates by default, POUS's kernel lanes
   get shell certificates, and the steward gets a break-glass principal whose sessions show in the ledger.
7. **Co-tenancy for every timing job, not only whole-node windows (§12).** Co-tenancy decides whether a timing counts.
8. **The quiet windows' NVML exclusion was assumed, and it was being broken.** `research run`'s own sampler polled
   `nvidia-smi` every 5 s inside every timed run until 17:25Z. Node 2 now pauses run samplers during windows, and workers pass
   `--no-sampler`. The design moves the rule into code (phase 1c) and records the sampler state in each quiet certificate.
   Custody uploads, which aren't paused today, run as `stage` work that windows freeze.
9. **Windows are short:** at most 5.3 min each so far. A window could wait for an 8-minute fill chunk instead of stopping it,
   but that would cost up to 8 minutes per window at about 20-minute gaps. So stopping stays the default. A per-window
   "wait for fill up to N s" option is noted, not built.
10. **What pous infra would keep, and what it would replace:**
    - **Kept, all already in the design:** a memory cap per job (the planner's memory plus systemd's `MemoryMax`); a total
      memory budget for guests (a share's `max_memory_gib`); pausing guest CPU work in windows (freeze); a start cutoff and
      a stop before the node's own stop (a share's `until`, and the admission end).
    - **New for the node agent:** the OOM guard picks its victim by rank, guests first.
    - **Workarounds replaced:** `taskset` by cgroup cpusets; the `statvfs` gate by project quotas (disk joins the model
      later); matching guests by scope name by a systemd slice per project, with its own OOM policy.
11. **Overflow limit (§6).** Jobs that rank or time sm_120 kernels pin `node = "vy-nebius-2"`, so the router never sends them
    to node 1. No model change is needed.
12. **The freeze list before 7 Oct** (the RTX PRO coordinator) constrains phase 2 and decision 2. Changing any of these means
    re-measuring the whole-node baselines before the next panel row:
    - the driver, CUDA, and the pinned toolkits (`/workspace/cache/pouw-cuda-12.9.1`, CUDA 13.1 for cuBLASLt);
    - the clock and power-cap settings;
    - `gpu-lease`'s name, flags and lock files;
    - the fill header and its exit codes;
    - the paths: `/workspace/pouw/*`, `/workspace/hf`, the venvs, `/workspace/research/runs`.
13. **RunPod lines stay outside the description (§13)** unless a pod is used as a node. They run under the budgets guard:
    `vy-coord-` until 6 Oct, `vyv-cov-` until 1 Oct 14:00Z, `vy-sm120-` until 8 Oct, with a $25 balance floor.
15. **The steward's node-1 facts (18:05Z).** Only TCP 22 passes between the nodes, inside the subnet too, so the router and
    any cross-node queue go over SSH with forced commands, as §10 planned. Requests don't match use (CPU about 4×, memory
    both ways), so the planner's CPU and memory checks are only as good as the declarations: jobs should declare measured
    sizes (plus 25% for memory), and the ledger's usage feed is where those measurements come from. Node 1's workloads are
    in §2.
14. **Speed (§3, phase 1c):** `research pods ssh` forwards no stdin today, so streaming stdin joins connection reuse and
    `logs -f`.
