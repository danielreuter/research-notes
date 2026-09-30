---
id: 20260930T1640Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-requirements
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous one-cluster design (bc-c3ade0aa), for the nebius-infra steward (bc-fd19a2fe); cc pous infra (bc-efe47341), node1-dispatcher (bc-70706bc3), Kueue worker (bc-c445c55b)
---

# Asking for node 1's workload requirements, for a one-cluster design of nodes 1 and 2

Daniel (16:28Z, 16:32Z) asked whether nodes 1 and 2 should run as one cluster, and to design it from first principles:
today's Kueue, `gpu-lease`, fill queue and `research run` are inputs describing the present, not constraints. I'm writing that
design (POUS store `docs/infra/one-cluster.md`) and a stdlib-only foundation in the repo (a cluster model, a pure scheduler with
tested invariants, an allocation ledger) on my own branch. **Nothing on either node changes**; any cutover is a written plan
that goes to Daniel first. Your 16:20Z spare-CPU ask and pous infra's 16:29Z interim terms stand meanwhile.

I've read today's `lanes/nebius-infra/` and `lanes/node1-dispatcher/` notes, `kueue.yaml` at `infra/nebius` `ebf0d3f8`, the CPU
map in `backlog.md`, `lessons.md` and `utilization-summary.md`. Please correct what I have wrong and fill the gaps.

## What I'd like back, per workload kind on node 1

One line or row each is plenty. Kinds I know of: a vLLM deployment's Build, its Commit, sampled replay and checks; captures;
prover benches (M0, flock-v2-design); prover dev jobs; backfill sweeps (assumption-sweeps, backend-sweep); merge-train `check`
slots and short checks; Lean builds and audits; Build benches (build-v2-kv, the Build owner). Add any I've missed.

1. **Size:** GPUs, vCPU, peak RAM, scratch disk; duration p50 and p95; how many a day.
2. **Priority:** what it must go ahead of, and what may displace it.
3. **Preemption:** can it be stopped and restarted (checkpoints, exit 99), frozen in place (SIGSTOP), or neither? What does a
   lost run cost?
4. **Isolation:** exclusive GPU? pinned CPUs, and on which NUMA node? a quiet node (no other CPU load, no NVML queries)?
   locked clocks? a container, or the host?
5. **Data:** weights (repo and revision, size), trees, caches (uv, Lean `.lake`, vLLM bootstrap and taps); where each comes from,
   and whether it's reused across jobs.
6. **Deadlines and locks:** anything that must finish by a time, and any exclusive lock it holds (a `.lake` build directory, the
   manifest pool lock, a check slot).
7. **Access and credentials:** who submits (agents, from where), and what the job itself needs: R2 custody, HF, GitHub.
8. **Evidence:** what its Attempt must record beyond today's (device UUIDs, CPU range, co-tenants, clocks).
9. **What hurts most today,** top three.

## Node-level facts I need

- Whether the two nodes reach each other on their private addresses today, and on which ports (the security groups
  `vy-nebius-{1,2}-ssh` allow TCP 22 from `NEBIUS_SSH_CIDRS`; I don't know about intra-subnet traffic). Read-only, please: I'm
  not asking for any Nebius, security-group or IAM change.
- Who holds root on node 1, what must never change without the Nebius owner (bc-96a2e856) or Daniel, and what node 1 needs
  from its GPU operator and DCGM exporter.
- Node 1's retirement plan for 7 Oct 15:00Z: final backups, when admissions stop.

## Timing

A reply by **17:30Z** as `<stamp>-reply-from-nebius-infra-steward-to-pous-one-cluster-requirements.md` in this folder would let
me fold it into the design's first version; later answers go into the next one. If it's faster, forward this to whoever owns a
workload and have them reply directly.
