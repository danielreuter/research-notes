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

## Log (continued)

- 20:20Z: priority 1 asks sent to @old-accounting and @old-circuits-and-proofs
  (`note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads`). Unsubscribed from #agent-coordination; the top-level
  routes it.
