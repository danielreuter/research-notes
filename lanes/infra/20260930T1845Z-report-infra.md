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
