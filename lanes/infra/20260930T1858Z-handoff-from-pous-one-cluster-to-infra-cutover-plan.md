---
id: 20260930T1858Z-handoff-from-pous-one-cluster-to-infra-cutover-plan
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous one-cluster design (bc-c3ade0aa), for the infra coordinator (bc-17cc41f1)
---

# Handoff to infra: the node 2 cutover plan, #586, and the one-cluster design are yours

From now on, infra owns [#586](https://github.com/danielreuter/verity/pull/586) (branch `cursor/cluster-foundation-7e9f`,
tip `24ae54f3`), the one-cluster design, and this cutover plan. That includes bringing the plan to Daniel for approval.
Nothing has changed on either node.

- **The design** is copied beside this note: `note:20260930T1858Z-draft-one-cluster-design`. The original is the pous store's
  `docs/infra/one-cluster.md`.
- **The plan** is below, and the pous store keeps a copy for Daniel at `docs/infra/one-cluster-cutover.md`.
- **The RTX PRO coordinator's (bc-2aa33ad8) sign-off** on the freeze-list claim is asked for in the pous store's
  `internal/pouw/infra/one-cluster-cutover-signoff.md`, which the pous coordinator relays. Collect it from there, or ask
  bc-2aa33ad8 directly.

## Still open on #586

1. **Merge.** It's a draft and not yet reviewed. It needs a recorded `check` of its tip through `research merge`. It touches
   the root `pyproject.toml` and `uv.lock`, so every suite's key moves, and `tools/research/tests/test_pythonpath.py`'s pinned
   roots.
2. **Workstream shares inside an owner** (the next planner slice):
   - `provers` owns 3 GPUs and never borrows;
   - `deployments-gpu` owns 5, borrowable but not kept;
   - the rank gains a within-share term.
3. **The cutover's model changes** (plan step 2b): a session with no hard limit but an expected length; a CPU-unmanaged lease.
4. **The cutover's code** (plan steps 2a, 2c and 2d): the node-2 adapter; the agent, in shadow and live modes; and
   `gpu-lease`'s agent mode with fallback, on `infra/nebius`.
5. **The description at Daniel's defaults:**
   - Verity's node-2 share gets GPUs (it has `max_gpus = 0` today);
   - a PoUW share on node 1;
   - `bench` and `capture` classes in Verity's order (`note:20260930T1722Z-reply-from-verity-root-to-pous-one-cluster`).

   That order conflicts with the live `kueue.yaml` (captures 1100, prover benches 300), and the steward should say which is
   policy.
6. **Node 2's GPU-to-NUMA topology** is assumed to match node 1's in the description. Read it once (`nvidia-smi topo -m`,
   outside a window).
7. **Lease state from the ledger alone** (`note:20260930T1807Z-handoff-from-pous-infra-to-pous-one-cluster-lease-state-failure-mode`):
   `state.json` becomes the one source. Add the holder-plus-waiter test to the simulation suite.
8. **Ingest `gpu-lease/usage/v1` records** into the ledger. Phase 1a shipped at `infra/nebius` `1ebbd156` and has been live on
   node 2 since 17:40Z. Its fields are `ledger.gpu_usage`'s.
9. **The node agent's jobs from the replies:**
   - a private scratch area and cache per allocation;
   - OOM victims chosen by rank, guests first;
   - a systemd slice per project;
   - project quotas instead of the `statvfs` gate.
10. **`research run` (tools/research, the research coordinator's area):**
    - SSH connection reuse, a one-round-trip submit, `logs -f` and stdin forwarding;
    - verification by git object ids;
    - the sampler skipping GPU and PSS reads during `--timed` leases, as bc-2aa33ad8 asked at 17:28Z. Node 2 has paused run
      samplers in windows since 17:25Z as a stopgap.

    Measured today: a launch takes 5.4 s and output shows at 10.8 s; a reused SSH connection costs 0.30 s a command against
    1.7 s fresh.
11. **The steward's 18:05Z workload answers**
    (`note:20260930T1805Z-reply-from-nebius-infra-steward-to-pous-one-cluster-requirements`) arrived after the design's
    requirements section was written, and aren't folded in. Two facts matter for sizing:
    - reservations don't match use (CPU requests about 4× use; memory off both ways);
    - only TCP 22 passes between the nodes.
12. **Whether a window gives a session a grace period** before evicting it is still open.

---

# Node 2 cutover to the one-cluster scheduler: plan for Daniel's approval

30 Sep 2026, 18:58Z. Owner from now on: the infra coordinator (bc-17cc41f1). Nothing changes on either node until Daniel
approves.

## What it does

`tools/cluster` ([#586](https://github.com/danielreuter/verity/pull/586)) holds the planner, the router and the hash-chained
ledger. A new **cluster agent** runs them on node 2 and becomes the only thing that decides who gets which GPU, and when.
Today `gpu-lease` makes that decision itself, by lock order and FIFO wait files.

`gpu-lease` stays a working alias:
- **Kept as they are:** its name, its path (`/usr/local/bin/gpu-lease` → `/workspace/pouw/infra/bin/gpu-lease`), its flags,
  its lock, owner and wait files in `/run/gpu-lease/`, and its memory scopes, signals and usage record.
- **The only change:** while an agent holds `/run/gpu-lease/agent.lock`, `gpu-lease` sends its request to the agent and
  takes the GPUs the agent grants. With no live agent, it uses its own logic unchanged.

**What stays where it is in this cutover:**
- CPU placement: leases aren't pinned, and the fill queue keeps CPUs 96–127 and the checks 128–191.
- Pausing CPU work in windows stays with `node_ops.py`.
- The fill runner stays as it is.

**How flags map to jobs:**

| Flag | Job |
|---|---|
| `N` | `gpus` |
| `--on` | `gpu_ids` |
| `--preemptible` | `preempt=requeue`, class `fill` |
| none of `--preemptible`, `--timed` | a session, `preempt=never` |
| `--timed`, or all 8 GPUs by one holder | `quiet=True`, class `timed` |
| `--max-min M` | `max_s = 60 × M`, enforced by `gpu-lease` as today |
| no `--max-min` | expected 30 min (today's rule), for backfill only, never enforced |
| `--mem-gb` | `memory_gib` |
| `GPU_LEASE_WHO` | the submitter |
| a guest's `GPU_LEASE_PROJECT=verity` | a guest job |

**Decisions, at Daniel's defaults:**
- **Decision 1:** GPU borrowing across nodes goes both ways, preemptible only, never during node 2's windows. Verity gets idle
  capacity only. Its node 2 share becomes GPUs on, CPUs 48–95, 256 GiB per job, 1,024 GiB in total, 6 jobs, until
  2026-10-07T12:00Z.
- **Decision 3:** Daniel holds the SSH CA key and signs every certificate.
- **Node 1's Kueue** stays with the steward.

## The freeze list stays untouched, so no timed baseline is re-measured

- **The claim, item by item:**
  - The driver, CUDA and pinned toolkits, the clocks and the power caps are all untouched.
  - `gpu-lease`'s name, flags and lock files are the same. Its internals change, as `1ebbd156` changed them today for the
    usage report.
  - The fill header and its exit codes (0, 99, 143/-15, 75, 124) are the same.
  - `/workspace/pouw/*`, `/workspace/hf`, the venvs and `/workspace/research/runs` are the same. The new files live only in
    `/workspace/pouw/infra/cluster/` and `/run/gpu-lease/agent*`.
  - The agent reads files only, never NVML, at `nice 19`, and does nothing during a window beyond one status read every 5 s.
- **Supporting evidence:** a 5 s `nvidia-smi` loop inside a timed window moved no row beyond noise, at most 0.1% on prefill
  (`r20260930-181638-b431`).
- **Sign-off needed from the RTX PRO coordinator (bc-2aa33ad8)** on this claim. The ask is in the pous
  store's `internal/pouw/infra/one-cluster-cutover-signoff.md`, relayed by the pous coordinator; the sign-off comes back there.

## Steps

1. **Approve.** Gate: Daniel approves this plan; the RTX PRO coordinator signs off on the freeze-list claim; node2-ops
   (bc-c0738ef6), which now runs node 2, agrees.
2. **Build.** On `infra/nebius` and `#586` follow-ups, with no node change:
   - **(a) The node-2 adapter:** it reads `/run/gpu-lease/*`, `fill/status.txt`, the sampler log and `node_ops`' quiet log into
     a planner snapshot.
   - **(b) The flag mapping above,** with two model changes:
     - a session may have no hard limit but an expected length;
     - a lease may be CPU-unmanaged.
   - **(c) The agent:** shadow and live modes. It is the only writer of the ledger and of `state.json`, which becomes the one
     source of lease and queue state. It checks the planner's invariants every tick and stops itself on a violation or an
     exception.
   - **(d) The `gpu-lease` agent mode,** with automatic fallback when the agent's lock is free. A waiter stays lock-held and
     self-expiring.
   - **(e) The description** at the defaults above.

   Gate:
   - the suites and a recorded `check` pass;
   - replaying today's node-2 lease and preemption logs through the adapter reproduces what happened;
   - the waiter-versus-holder test from `13f402b2` passes against the adapter.
3. **Shadow on node 2, today.** A read-only recorded run: `--no-sampler`, `nice 19`, reading only the files in 2(a) and writing
   only `/workspace/pouw/infra/cluster/shadow/`. It skips ticks while `timed True`. Every 5 s it plans, and it compares the plan
   with what `gpu-lease` did. **Pass bar for the switch,** over at least 3 h and at least 6 timed windows:
   - **no safety divergence:** the planner never grants a held GPU, starts anything inside a window, evicts a
     non-preemptible lease, puts a guest ahead of a waiting owner, or admits past 13:00Z on 7 Oct;
   - **windows start no later:** every window the planner would start within one tick (5 s) of when `gpu-lease` started it;
   - **no idling behind a waiter:** no request waits in the plan more than 10 min while enough GPUs are free;
   - **design divergences** (owner before guest, fair turns, backfill that `gpu-lease` missed) are listed and reviewed by
     node2-ops and the RTX PRO coordinator, not counted as failures;
   - **footprint:** under 1% of one core, zero NVML calls, zero exceptions;
   - **the ledger:** the shadow ledger verifies, and every window's quiet report agrees with `node_ops`' quiet log.
4. **Switch** (node2-ops, outside a window, with the RTX PRO coordinator told 15 min ahead). Deploy the agent-mode
   `gpu-lease` by rename (`install … .new && mv`), then start the agent live. Running leases keep their locks and scopes, and
   the agent adopts them from the owner files. Gate for the first hour:
   - the live ledger's invariants hold;
   - every window gets its GPUs within 5 s of asking;
   - no lease is lost;
   - one rollback drill outside a window: stop, fall back, restart.
5. **Guests and overflow.** Only after Daniel signs the certificates (below) and the steward's node-1 parts are done. Verity's
   CPU and GPU jobs enter node 2's agent through a queue-only certificate. PoUW's untimed overflow goes to node 1's Kueue.
   Gate:
   - a guest is evicted by an owner lease within 30 s;
   - no guest runs during a window, per the ledger;
   - overflow runs only through node 1's `backfill`.

## Rollback, in one step

Run `cluster agent stop` on node 2. The agent's lock drops, and `gpu-lease` returns to its built-in scheduling on its next
poll, within 15 s.
- Running leases are untouched, because their locks and scopes are `gpu-lease`'s.
- The agent also rolls back by itself on any invariant violation or exception.
- The ledger stays for the record.

## Node 1: the steward's parts, and what changes in Kueue

- **Kueue stays node 1's scheduler.** Its quotas and priorities don't change.
- **One new LocalQueue for PoUW's overflow** (for example `pous-overflow`), on the `backfill` ClusterQueue:
  - nominal quota 0, preempts nobody, evicted first, priority `backfill`;
  - CPUs pinned to 96–191, since 0–95 are reserved;
  - only work that neither ranks nor times sm_120 kernels.
  - It depends on backfill actually borrowing idle GPUs, which is the steward's fix for node 1's 2% busy (Verity's pain #1).
- **Intake:** overflow jobs arrive as lines in the dispatcher's ready file (`/workspace/jobs/dispatch/ready/pous.jsonl`),
  written by node 2's router.
- **Identity, on both nodes** (Daniel signs the certificates):
  - sshd trusts Daniel's CA (`TrustedUserCAKeys`), set on node 1 by the steward and on node 2 by node2-ops;
  - node 2's router may only append to node 1's ready directory, and node 1's dispatcher may only submit to node 2's agent,
    each through a forced command;
  - the steward keeps a break-glass principal, and every use is logged to the ledger;
  - no ports, security groups or IAM change: only TCP 22 passes between the nodes, as measured at 15:12Z.
- **Later, optional:** an exporter of Kueue workload events into the ledger format, so the failure and usage feeds cover
  both nodes.
