---
id: 20260930T1915Z-report-cluster-build
campaign: verity
lane: cluster-build
kind: report
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a), worker of the infra coordinator (bc-17cc41f1); takes over tools/cluster from bc-c3ade0aa
---

CHECKPOINT 9dba8335c (21:15Z) [open] shadow clean 1h12m, no window yet; fill_runner agent.lock change cc8e54b6a for node2-ops; submit path in progress on cursor/queue-submit-path-0381
CHECKPOINT 640c6d76c (20:50Z) [open] 2d gpu-lease agent mode 5688325a6 handed off; #586 640c6d76c merge request to coordinator; shadow r20260930-195806-59f3 healthy, 0 divergences at 50 min
CHECKPOINT e6a40782c (19:54Z) [open] 2a+2c at e6a40782 (#586): nebius2 adapter, shadow, agent; full-day replay reproduces leases+114 preemptions, windows ≤1 s, 0 safety; 13f402b2 test vs live gpu-lease passes; 75 cluster tests; next: shadow launch
CHECKPOINT 42311e840 (19:25Z) [open] step 1 done 42311e84 (workstreams, ledger-only state, usage/v1, 2b, defaults; 55 pass); cutover approved 19:15Z; next: 2a adapter + replay
CHECKPOINT 24ae54f35 (19:12Z) [open] started: read plan+design+replies, copied node-2 logs read-only; next: #586 step 1 (workstreams, ledger-only state, usage/v1, 2b, defaults)
# cluster-build: the node-2 cutover's code (#586 follow-ups, the adapter, the agent, gpu-lease's agent mode) up to a shadow run ready to start

Branch `cursor/cluster-foundation-7e9f` (#586), base tip `24ae54f3`. Node-2 side on `infra/nebius` (#496), base `13f402b2`.
The cutover is approved (`note:20260930T1915Z-handoff-from-infra-cutover-approved-one-central-scheduler`, 19:15Z). I start the
shadow myself once steps 2a–2c pass their gates, and I own the switch. The target is one central scheduler for both nodes.

Read: `note:20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan`, `note:20260930T1858Z-draft-one-cluster-design`,
the 17:21Z, 17:27Z, 18:05Z, 18:07Z and 17:22Z replies, and `note:20260930T1856Z-handoff-from-pous-infra-hand-back`.

## Log

- 19:12Z: copied today's node-2 logs off the node, read-only at `nice 19` outside a window (`preempted.log`, `quiet.jsonl`,
  fill `events.jsonl`, the sampler's `util/2026-09-30.jsonl`, and the live `node_ops.py`, `gpu_util_sampler.py`, `gpu-lease`).
  Live `gpu-lease` sha256 `0d172cf3…`, as the hand-back says.
- 19:25Z: step 1 done at `42311e84` on #586. It adds workstreams (per-node GPU shares with a borrow cap, reclaimed in
  seniority order), lease state and queue replayed from the ledger alone (`ledger.state`, `state.json` as its cache), the
  holder-and-waiter simulation test, `gpu-lease/usage/v1` records folded into `end` records, and the step-2b model changes
  (sessions with only an expected length, CPU-unmanaged leases, `invariants.check`). The description is set to Daniel's
  defaults. The cluster suite passes 55 tests. The 18:05Z answers are folded into the design draft, and the priority
  conflict is flagged to the steward, unresolved, in
  `note:20260930T1930Z-handoff-from-cluster-build-to-nebius-infra-steward-priority-order`.
  #586's description isn't edited: I have no pull-request tool, so the coordinator handoff carries it.
- 19:45Z: steps 2a and 2c at `e6a40782`, and the run script at `d09ad49a`. Pieces:
  - `nebius2`: the adapter. It reads locks from their holders' fdinfo, because `/proc/locks` hides gpu-lease's locks (their
    `flock(1)` taker has exited).
  - `shadow`: mirrors gpu-lease into the ledger, plans each tick, and records divergences. `replay` and `evaluate` (the pass
    bar) live here.
  - `agent`: shadow and live modes. Inside a window it reads only `status.txt`. It stops on an exception or on a plan that
    breaks a rule.

  The full-day replay reproduces every lease and all 114 preemptions, starts every window within 1 s, and has no safety
  divergence (`art:7932c81a129e8a22a685aa9d679e1d2f72c22687fcfac12b949b3d0c3840ba53`). 13f402b2's waiter-versus-holder test
  passes against the adapter and the live gpu-lease.
- 19:58Z: **shadow started**, run `r20260930-195806-59f3`, 8 h:
  `uv run research run --on vy-nebius-2 --project verity --source . --cwd source --no-sampler --timeout 30600 --custody-ttl 10h --campaign verity --declared-output 'out/*' -- bash tools/cluster/shadow-node2.sh 8`.
  Outputs go live to `/workspace/pouw/infra/cluster/shadow/<run>/`. At the end the script copies them into
  `$RESEARCH_RUN_DIR/out/`, which custody walks. Handoffs: `note:20260930T2002Z-handoff-from-cluster-build-shadow-running`
  (node2-ops), `note:20260930T2004Z-handoff-from-cluster-build-step3-shadow-running` (infra) and
  `note:20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface`. The brain goes on node 2.

- 20:48Z: the shadow is healthy after 50 min: 404 ledger records, 205 decisions, no divergence, 0.2% CPU at nice 19, 96 KB.
  My 20:0xZ handoffs reached origin only at 20:45Z; `git add` had failed silently in my push script, which is fixed.
- 20:40Z: **step 2d done:** gpu-lease agent mode, `cursor/gpu-lease-agent-mode-0381` `5688325a6` (sha256 `49238797…`).
  It includes the owner-line race fix. The research suite passes 757 tests. Handed to the steward and node2-ops
  (`note:20260930T2050Z-handoff-from-cluster-build-gpu-lease-agent-mode`). The cluster suite runs the protocol end to end
  against it.
- 20:45Z: kueue-fold's `nebius1` is merged into #586. `plan()` fixed: a GPU-less job gets no workstream standing. The priorities
  follow `kueue.yaml`, per the steward's ruling. Reply: `note:20260930T2045Z-reply-from-cluster-build-node1-observer-merged`.
- 21:00Z: **step 4:** merge request for #586, now at `9dba8335c` (kueue-fold's `--report` merged) (`note:20260930T2100Z-handoff-from-cluster-build-merge-request-586`).
- 2:16 PM PDT: the shadow is clean at 1 h 12 min (605 ledger records, 306 decisions, no divergence, no window yet).
  `fill_runner` leaves waiters to the agent while `agent.lock` is held (`cc8e54b6a`, node2-ops' ask); it deploys with agent
  mode. A second loop of this lane is building the submit path on `cursor/queue-submit-path-0381`. Its claims are in
  `/cursor/stores/self/claims.md`.
- 2:38 PM PDT: `research run --queue` live-tested on node 2 (CPU and 1-GPU guest runs, both done). Both before-live gaps are fixed
  (`02fb21d25`, `4350c52f0`). A partial `--timed` window clears the node but doesn't wait for sessions (`196f9ab60`), and a GPU is
  booked only around the workload (`27676a80c`). Replies to node2-ops and PoUW; status to infra
  (`note:20260930T2138Z-handoff-from-cluster-build-queue-live-tested-gaps-fixed`).
- 2:47 PM PDT: `--queue` merge request at `27676a80c`, stacked on #586
  (`note:20260930T2145Z-handoff-from-cluster-build-merge-request-queue`). Live at this head: node-1 CPU and node-2 GPU runs.
  Replaying today's node-2 logs through the cut gives 27 windows, 0 safety divergences
  (`art:04f3724c12678369ddfaa8bf877ad03a3d26b5094776906c19676e35dfed82fe`). circuits has the flags for T3.
