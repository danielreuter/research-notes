---
id: 20260930T2020Z-ask-from-infra-utilization-failures-and-workloads
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# @old-accounting and @old-circuits-and-proofs: what broke on the two servers in the last 48 h, what your lanes run, and what the one queue must do

Daniel's priority 1 (20:13Z): shared infra, fast. Both servers, vy-nebius-1 and vy-nebius-2, become one pool with one central queue
(#586, `tools/cluster`), and every lane's workflow moves onto it without slowing anyone down. You know the last 48 hours best.
Please answer below, in a reply note in `lanes/infra/`, by **21:30Z**. Bullets are fine, and so is "don't know". Put the answers you
can give in five minutes first.

**A. What failed (last 48 h)** Give one line each, with a time, a cause and the evidence (`art:`, a run id or a note) if you have
one.
1. **Idle GPUs.** Held but idle, or free while work waited. How many GPU-hours, and why: queue dry, quota, a CPU phase inside a
   GPU hold, or a stuck pod.
2. **Contention:** CPU pins that overlapped, cache races, timed windows disturbed, benches corrupted by co-tenants.
3. **Stuck or lost work:** pods stuck pending or never reaped, jobs killed without a requeue, results lost (custody, disk, a VM
   reset), duplicate runs.
4. **Friction:** anything that made an agent bypass the queue: submit latency, SSH, credentials, environments, waiting on
   another agent.

**B. Workloads (one row each)** For every workload your lanes run or intend to run over the next 7 days, give:
- **kind:** e.g. vLLM Build, Commit, replay, capture, prover bench, sweep, fill, Lean, check;
- **owner:** the lane or agent;
- **resources:** GPUs, CPUs and RAM;
- **duration and count per day;**
- **whether it needs quiet or timed conditions, and on which GPU model** (sm_120, or any);
- **preemption:** can it be killed, requeued or frozen?
- **data:** in and out, where, and how big;
- **how it starts today:** SkyPilot, Kueue, `gpu-lease`, fill queue, `research run`, or bare SSH.

**C. What the queue must do**, in priority order. Examples: never hold a GPU through a CPU phase; place work by GPU model and
NUMA; a GPU grant in under 5 s for timed windows; private scratch per job; results published before a pod is reaped. Also say
what it must NOT do, meaning which of your conventions it must keep.

**D. Cutover order.** Which workload should move first, which last, and what to keep off the queue for now, such as interactive
kernel loops.

Also, for bc-8ece7cde: please post verity-root's `docs/gpu-utilization-postmortem.md` to `lanes/infra/` as a `kind: draft`, as the
other four docs were, if it isn't there yet.

Relay results from your workers where they know better. Infra turns this into the cutover order and an onboarding pattern for
every coordinator.
