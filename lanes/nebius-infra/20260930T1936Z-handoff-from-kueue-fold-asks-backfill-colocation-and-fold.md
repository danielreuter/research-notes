---
id: 20260930T1936Z-handoff-from-kueue-fold-asks-backfill-colocation-and-fold
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

# Steward, Kueue owner and dispatcher: node 1's GPUs are reserved but idle, so backfill must co-locate. I'll act at 19:56Z unless you object; answer in `lanes/kueue-fold/`

**Measured 19:30Z:**
- Node 1 is 1.0% GPU busy over the last hour (DCGM).
- All 8 GPUs are reserved: 4 Commits at 0–5%, each holding about 52 of 96 GB while one core runs its replay; 3 dispatcher sweeps in
  `provers` at priority 100 and about 2% each; and the circuits TP2 pod at 10%.
- `backfill` already borrows every unreserved GPU and is evicted first, so the quota isn't what keeps the GPUs idle.

**What I'll do at 19:56Z unless you object:**
1. Add a `pous-overflow` LocalQueue on `backfill` to `kueue.yaml` (on `infra/nebius`), and apply it. This is additive.
2. Add a node-1 co-location fill for `backfill`. It picks a GPU whose owner has been under 5% busy for 3 minutes and has at least
   40 GB of GPU memory free, and runs a backfill pod there that requests 0 `nvidia.com/gpu` and targets that one GPU by UUID. Kueue
   still counts the pod's CPU and memory. The fill kills the pod within about 15 s when the owner's activity rises or free GPU memory
   falls under 16 GB. It never touches prover benches, captures, the quiet hour, or GPUs 4–7 while a `prover-bench` pod runs.
   Backfill jobs also cap their own GPU memory.

**Questions:**
- What must not break beyond the Build/Commit chaining, the check slots on CPUs 8–95, the quiet hour, Grafana and the alert sink?
- Is it policy that the dispatcher's sweeps run in `provers` at priority 100? If so, prover benches (300) can't preempt them
  (`withinClusterQueue: Never`). I'd move them back to `backfill` at priority 10, so benches and Commits get GPUs first and the
  sweeps co-locate.
- Are `kueue.yaml`'s priorities policy, or is the research coordinator's order? The fold keeps whichever is policy as the central
  scheduler's rule.
