---
id: 20260930T1845Z-report-infra
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1-6227-5fab-bc64-3fa2f224558b), reporting to verity-top
---

# infra: the infra subcoordinator's report

Charter: `note:20260930T1740Z-handoff-from-pous-charter-infra`, plus verity-top's 18:43Z additions (the Grafana alerts, and the
Verity-side infra agents). Inbound handoffs go to `lanes/infra/`.

## Who infra coordinates (through notes unless created by infra)

| Agent | Owns | Channel |
|---|---|---|
| node2-ops (bc-c0738ef6-f6bb-5c95-a44f-8e08ff9f35fd, created by infra) | node-2 ops: tmux daemons, backups, alerts, utilization | `lanes/node2-ops/` |
| bc-efe47341 (old pous infra lane) | node-2 ops until the handover; pouw stops it | `lanes/pous/` |
| bc-c3ade0aa | one-cluster design, [#586](https://github.com/danielreuter/verity/pull/586) | pous store `docs/infra/one-cluster.md` |
| bc-26712550 | live-console exporter (one `panels:write` key request owed) | `lanes/pous/` |
| nebius-infra steward bc-fd19a2fe | node 1 host, monitoring, `infra/nebius` | `lanes/nebius-infra/` |
| Nebius owner bc-96a2e856 | launch, lease, deadline, clocks, IAM | `lanes/nebius-infra/` |
| Kueue owner bc-c445c55b | node 1's Kueue | `lanes/nebius-infra/` |
| node1-dispatcher bc-70706bc3 | node 1's queue refill, backfill | `lanes/node1-dispatcher/` |
| GitHub broker | owner being asked (`lanes/verity-root/`, 18:45Z) | |

## Node-2 ops handover protocol

Only one agent runs ops ticks against node 2. The owner is whichever agent id `/workspace/pouw/infra/ops-owner` names on the node.
Until the old lane writes node2-ops' id there, node2-ops' timers only read that file and end. Its timers run at :05 hourly and at
:02/:17/:32/:47 for alerts. The old lane's hourly tick runs at :03 and its alerts every 15 minutes. The old lane hands over in
three steps: it unsubscribes all its timers, copies its lane scripts to `/workspace/pouw/infra/lane/`, and, as its last act,
writes the owner file.

## Log

- 18:45Z: started. Handoffs sent to nebius-infra, node1-dispatcher and verity-root. The node2-ops lane is launched, and it
  stays in standby until the handover. A cloud-environment build (uv plus the workspace synced) is being tested and will go to
  Daniel for Save.
- 18:47Z: broker: source=broker (infra VM). node2-ops armed in standby (timers sub_1994e728 hourly :05, sub_a8e17710 alerts,
  sub_2c6c7e41 / sub_c41c4216 final backups); owner file absent.
- 18:50Z: asked pouw to have bc-efe47341 run the handover and stop (`note:20260930T1850Z-handoff-from-infra-stop-old-node2-ops-lane`).
- 19:05Z: took ownership of #586, the one-cluster design and the node-2 cutover plan (from bc-c3ade0aa). Launched the
  cluster-build lane (bc-c2e4c12a) for #586 and cutover steps 2–3. It builds but starts nothing on either node until Daniel
  approves. Sent the decisions brief to verity-top. Handoffs: node2-ops (Daniel's priority 2), coordinator (four workers,
  trains), verity-root (one alert-sink change, four docs).
- 19:20Z: Daniel's 19:12Z rulings recorded (`note:20260930T1915Z-rulings-from-daniel-one-pool`, and the brief in the Project
  store at docs/infra-decisions.md). kueue-fold lane (bc-d5ffe46d) launched for the vy-cluster key, node 1's backfill borrowing,
  option-1 CPU Builds on node 2, and the Kueue fold. slack-sync (bc-0c4b24d6) runs groups sync --apply on #592. @infra is
  subscribed to #agent-coordination and #agent-alerts. Slack onboarding notes sent to coordinator, vllm-coordinator, pous and
  console.

## Priority 1 settled: the criteria (infra decides; set 20:20Z)

Priority 1 is settled when all eight of these hold for 24 h in a row. Infra then tells verity-top, and priority 2 (the merge,
feature and idea backlog) starts.

1. **One queue.** `research run` submits every lane's batch and service jobs to the central queue (#586 `tools/cluster`), and
   nothing else does. The only exceptions are interactive kernel loops and live debugging on SSH, which take a session lease
   through the queue and are visible in it.
2. **Both nodes scheduled from it.** vy-nebius-1's GPUs and CPUs are placed by the queue, with Kueue at most a container runtime
   that has no quota logic of its own. vy-nebius-2 is placed by the queue, with `gpu-lease` as an alias, and its timed windows
   get their GPUs within 5 s. There is one ledger for both.
3. **Every lane onboarded.** Circuits, proofs, compute-, memory- and network-accounting, console and infra have each run at
   least one real job through `research run` on the queue, and their workload inventories are in `lanes/infra/`.
4. **No ad hoc compute.** No hand-started pods or jobs on either node outside the queue, and no running RunPod pod without a
   `budgets.toml` line. A daily scan of both nodes and RunPod finds nothing unowned.
5. **Utilization is visible and on target.** An hourly report per node gives GPU busy %, CPU busy % and the useful share against
   the filler share, generated from the ledger and shown in Grafana or the console. The pool is at ≥95% GPU busy with ≥90% of it
   useful work, for any hour in which the lanes have queued work.
6. **Results are safe.** Every queued job's outputs are custodied (preserved) before its allocation is released. Zero results
   lost in the 24 h.
7. **Failures surface.** Nonzero exits, evictions, expiries and idle leases go to the ledger's failure feed and reach
   `#agent-alerts`, and each gets an owner.
8. **Rollback works.** A one-step rollback to the previous per-node scheduling is documented, and drilled once on each node.

## Old open items (logged, not chased; per verity-top 20:15Z)

- Nebius key rotation (Daniel: later).
- RunPod spend ceiling and on-demand policy (inputs in `lanes/infra/20260930T1917Z-draft-from-verity-root-runpod-spend-and-check-pod-policy.md`).
- One task API: job-service design versus SkyPilot migration (drafts from verity-root, 19:17Z). The one-pool queue likely supersedes both.
- Live-console exporter bc-26712550: one `panels:write` key request owed; stop its key retries.
- Slack group descriptions are fixed now; #592 still needs the research coordinator's merge.
- node-2 alerts relayed by node2-ops at 19:20Z: `gpu1-pearlc-forms-b.sh` rc=4 and `fp4-recheck2-verify` failing (pouw owners).
- Land #496 and #531 (proof trains).
- Three stale `vy-pous-*` entries in notes `machines.d`; their pods have been gone since 27 Sep (memory-accounting, 20:17Z).

## Log (continued)

- 20:20Z: priority 1 asks sent to @old-accounting and @old-circuits-and-proofs
  (`note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads`). Unsubscribed from #agent-coordination; the top-level
  routes it.

## Workload inventories received (the queue's sizing)

- **network-accounting (20:22Z):** #326's re-test, one check of about 12 min of CPU (told: recorded check on node 1 now); a
  deferred timed GPU run of about 15 GPU-h (the quiet class, waiting on the queue).
  `note:20260930T2022Z-handoff-from-network-accounting-workload-inventory`.
- **memory-accounting (20:20Z):** paused. On resume: CPU tests and Lean, a one-GPU exclusive timed audit harness (10–60 min, a few
  a day), CPU-fill encodes of about 3 core-hours. `note:20260930T2020Z-handoff-from-memory-accounting-workload-inventory`.
- **proofs (20:19Z):** everything runs on node 1: train checks in slots a/b/c, Lean builds and audits, 1-GPU M0 benches on
  `provers`, and the backend sweep as `dev` backfill. Answered on Slack at 1:21 PM PDT.
- **circuits (20:24Z):** eight kinds, all on node 1's Kueue, limited by CPU for Builds. Told: Builds on node 2 are live now; the
  0%-GPU Commit replay needs PR A/B plus co-location; caches and TP2 recorded. Answered at 1:27 PM PDT.
- **compute-accounting (20:25Z)** and **console (20:25Z):** received, to be folded into the cutover draft.

## Milestones

- 1:08 PM PDT (20:08Z): node 2's Verity guest pool is live. 19–20Z ran at 95.1% GPU busy, 100% useful, which meets the target.
- 1:26 PM PDT (20:26Z): a vLLM Build ran on node 2 as a Verity guest and reproduced node 1's digests (kueue-fold); its Commit is
  queued on node 1.
- 12:58 PM PDT (19:58Z): the cluster-build shadow is running on node 2 (`r20260930-195806-59f3`, 8 h). The replay gate passed
  (`art:7932c81a…`).
- 1:22 PM PDT (20:22Z): the Slack relay passed acceptance from a VM without the token (#592 at `34986255`).

## Targets (Daniel, 2:06 PM PDT, 30 Sep). Infra owns the numbers

| Target | By | Measure | Owner |
|---|---|---|---|
| T1 | 3:30 PM PDT, 30 Sep | node 1 ≥60% useful GPU busy (existing Kueue) | node1-fill, kueue-fold; proofs and circuits submit |
| T2 | 6:00 PM PDT, 30 Sep | both nodes ≥80% useful GPU busy, sustained; CPU ≥60%; timed windows protected | node2-ops, node1-fill, kueue-fold |
| T3 | 11:59 PM PDT, 30 Sep | #586 merged, `research run --queue` live, node 2 switched, first lane job through the queue | cluster-build; merge by the old research coordinator |
| T4 | 12:00 PM PDT, 1 Oct | node 1 on the scheduler; only `research run --queue`, no ad hoc pods; console panel; ≥85% useful over 12 h | kueue-fold, cluster-build, console |
| Standing | always | ≥12 GPU-h of ready, useful work queued per node | node2-ops and node1-fill watch; the lanes keep it queued |

Starting point at 2:05 PM PDT: node 1 at 0.3% GPU (30 min), 29% CPU, 29 GPU workloads pending, and 4 GPUs with no memory
used. Node 2 had all 8 GPUs leased, 0 GPU jobs queued and 24 CPU jobs queued.

## Right resources by construction (Daniel, 2:14 PM PDT). Infra owns it; it's built into the queue

- **One submit path:** `research run --queue --kind K`. The kinds live in the repo (`tools/cluster/kinds*.toml`) and are resolved
  from the submitter's git commit; the commit is recorded in the ledger. There are no node-local templates. (cluster-build,
  `note:20260930T2128Z-handoff-from-infra-job-kinds-registry`)
- **Kinds are phase-pure:** `gpu1`, `gpu2`, `gpu8-timed`, `cpu-s`, `cpu-m`, `cpu-l`. Each has a max wall time (GPU kinds are preemptible
  and take ≤60 min), declared inputs and outputs, a restart mode and an owner. Irregular work is a chain of kinds joined by a
  manifest.
- **Admission:** fail-closed tonight on an unregistered kind, and on a GPU kind with a CPU phase or no max wall. Warn only until T4,
  then fail-closed, on shapes off the menu, missing outputs and GPU kinds over 60 min. The `budgets.toml` line applies to RunPod
  kinds only.
- **Monitors:**
  - leased-but-idle (<10% for >5 min, outside windows) and unleased GPU processes: on node 2 by node2-ops, on node 1 by
    kueue-fold;
  - node 1's template drift check, until the registry replaces the templates;
  - per-kind efficiency (useful ÷ leased GPU-s) in the ledger, shown as a console table (T4).
- **Learning loop:**
  - a monitor hit is fixed in the kind, by its owner;
  - a norm broken twice becomes an admission check (cluster-build);
  - otherwise the norm goes into a "Submitting to the queue" section of `writing-runs/SKILL.md`, once the kinds land;
  - infra posts the daily top-3 wasters at 9 AM PDT (timer `infra-daily-top-wasters`).

## Rulings, 2:52 PM PDT (Daniel)

1. **A resource-steward lane,** under infra, live before the node-2 switch (by 5 PM PDT): it watches disk, RAM, GPU memory, caches,
   bundles, the custody backlog and inodes on both nodes; it wakes on alerts plus a 20-min timer; it acts under a written policy,
   with a blocking card to Daniel for anything beyond it; one owner.
2. **Overnight:** every queue needs its lane owner's explicit yes, and every job names its research question. The kind registry records
   `question`. Idle beats padded.
3. **Focus:** PoUS stays paused; network accounting pauses too (#326's check still goes into the train). Capacity and attention go
   to circuits, proofs and compute accounting.

## T1 result (3:30 PM PDT): MISSED
- **Node 1, 2:30–3:30 PM PDT:** 3.96% GPU busy (DCGM `GR_ENGINE_ACTIVE`, averaged over the 8 GPUs, from node 1's Prometheus), against the 60% target.
- **Delivered-output metric,** now node 1's measure per Daniel's 3:22 PM PDT ruling: 87.3% of leased GPU time delivered for 2–3 PM PDT,
  provisional, on 5.1 of 8 GPU-h leased.
- **Blockers:**
  - the work mix: small-model Commits are GPU-light, and the K=2048 whole-row runs hold GPUs at about 12% while the CPU verifies;
  - Commits dispatched before the 2:15 PM PDT template refresh replay on their GPUs;
  - TP2 is held after a crash.
- **Fixes under way:** MPS packing (the golden match plus one pod, gated on storage), the verify split for the whole row, PR B.

## Daily top 3 GPU wasters, Oct 1 (posted 9:43 AM PDT, ts 1790872988.580989)

Idle GPU-hours over the 24 h to 16:38Z, both nodes, by kind and owner. Node 1 counts held minus busy from DCGM's one reading a
minute (the console's `node1-owners`). Node 2 counts leased minus useful from POUS's 10 s sampler (`nodes.n2.kinds`, the console's
`pool-kinds`), with timed leases left out.

1. **circuits, `vllm-epoch-run`** (node 1's coverage rows): 74.5 idle of 81.5 GPU-h held, 9% busy. That's 57.3 as the dispatcher's
   Kueue Jobs and 17.2 as Sep 30's SkyPilot `gpu-*` jobs (16–21Z, the `cov-m*` rows). Most of it is the CPU verify inside a GPU hold.
   The fix is morning-set item 1: Commits lease their GPU after pod startup (pilot `cov-k01-lease`), target ≤40% held idle.
2. **n2-commits (circuits' bc-698052e1), `verity-commit`** on node 2: 9.2 idle of 9.7 GPU-h leased, 5% useful, plus 0.44 of 0.45
   in `cov-g217-proof`.
3. **proofs, `backend-sweep`** on node 1: 7.8 idle of 8.4 GPU-h held, 7% busy. Proofs' node 1 kinds total 28.9 idle GPU-h.

## Daily top 3 GPU wasters, Oct 2 (posted 9:04 AM PDT, ts 1790957048.288709)

Idle GPU-hours over the 24 h to 16:00Z, timed leases left out. Node 1: held minus busy from DCGM's one reading a minute, by pod
kind from Prometheus (each GPU's series is doubled there, so halved; that matches the console's `held-idle-hourly` lane totals).
Node 2: leased minus useful (`nodes.n2.kinds`).

1. **circuits, `vllm-epoch-run`** on node 1: 22.6 idle of 25.6 GPU-h held, 12% busy (Oct 1: 74.5 of 81.5). 15.3 in the lease
   pool's holders (`gpu-pool-circuits`, 134 pods; 4.7 of it unleased), 7.3 in whole-GPU `nd-vllm-epoch-run-*-gpu-0` (59 pods).
   Moved-back Commits keep their lease since 14:32Z (#829); gemma2-9b's instrumented phase goes to the commit-lease worker.
2. **proofs, `prover-b` pods** on node 1: 18.6 idle of 20.1, 8% busy (Oct 1: 28.9 idle). bf16-hill 8.2 (127 pods), vllm-de 5.3,
   vllm-mo 2.3, zk-k32k 1.4, zk-cell 1.2. Suggested: lease the GPU for the prover's GPU phase only.
3. **n2-commits (circuits' bc-698052e1), `verity-commit`** on node 2: 8.8 idle of 10.6 leased, 17% useful, 51 leases (Oct 1:
   9.2 of 9.7).

Next: circuits' `commit-pack` on node 1, 5.8 idle of 5.9. Node 1 48.1 idle of 53.9 held; node 2 18.0 of 32.8 (5.4 timed, by design).

## Daily top 3 GPU wasters, Oct 3 (posted 12:01 PM PDT, ts 1791054087.093429; timer delivered 3 h late)

Idle GPU-hours over the 24 h to 16:00Z, timed leases left out. Lane totals from node 1's `held-idle-hourly.jsonl` (both nodes
now); node 1 kinds from Prometheus (halved); node 2 kinds from `lease-usage.jsonl`, since `infra-pool.json`'s `nodes.n2` is
paused and has no `kinds`.

1. **circuits, TP8 `runner.sh` lease (`gpu-lease` 8)** on node 2: 31.2 idle of 31.2 GPU-h held, no busy sample. 06:30-09:37Z
   held 8 GPUs while the 235B TP8 Build r20261003-070729-359b ran (2.6 GPU-h tagged `who=research`); 14:30-15:22Z the window's
   Match until it failed on the fold gap. Suggested: lease only for Match and Commit.
2. **circuits** on node 1: 8.5 idle of 9.6 (Oct 2: 22.6 of 25.6). `nd-vllm-epoch-run` 6.0 of 6.8 (14 pods),
   `gpu-pool-circuits` holders 3.6 of 4.6 (57 pods).
3. **n2-commits (circuits' bc-698052e1), fill** on node 2: 6.6 idle of 7.2, 21:00-02:00Z (Oct 2: 8.8 of 10.6).

Next: node 1's provers pool 4.6 of 24.2; memory accounting on node 2 4.3 of 20.1. Node 1 15.2 idle of 36.7 held (Oct 2: 48.1
of 53.9); node 2 44.0 of 67.1 (Oct 2: 18.0 of 32.8).

## Daily top 3 GPU wasters, Oct 4 (posted 9:13 AM PDT, ts 1791130381.636879)

Idle GPU-hours over the 24 h to 16:00Z, timed leases left out (compute accounting's 15:00Z window 4.6, bc-e90634dd's 1.0 and the
3 Oct 18:05Z window 1.0). Lane totals from node 1's `held-idle-hourly.jsonl`; node 1 kinds from Prometheus (halved) and
`lease-usage.jsonl` commands; node 2 kinds from `lease-usage.jsonl`.

1. **circuits, `circuits-tp8`** (2 leases of 8) on node 2: 14.8 idle of 14.8, 16:00-20:00Z on 3 Oct (the Qwen3-235B window
   after its Match stopped on the fold gap). Suggested: hand the lease back when a stage fails.
2. **network accounting's `network_traces` seeds** on node 1 (default pool, counted as proofs/provers): 11.7 idle of 101.9
   (Prometheus `gpu-pool` 13.8, 45 pods). The backfill stopped at 06:56Z under Daniel's no-filler rule.
3. **memory accounting** on node 2: 7.4 idle of 38.9; fill PoUS e2e series (`fill:bc-15ada664`) 5.9 of 39.0 (133 leases),
   erase-calib 0.8 of 5.9.

Node 1 14.1 idle of 104.7 held (Oct 3: 15.2 of 36.7); node 2 35.4 of 105.7, about 29 of 99 without timed windows (Oct 3: 44.0
of 67.1). Gap: node 1's `gpu-lease` records `sampled_s` 0, so its lease-usage busy figures are unmeasured; DCGM is the source.

