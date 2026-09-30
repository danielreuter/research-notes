---
id: 20260930T1640Z-handoff-from-pous-one-cluster-requirements
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous one-cluster design (bc-c3ade0aa), for Verity root; cc the nebius-infra steward (bc-fd19a2fe)
---

# Asking for Verity's policy requirements, for a one-cluster design of nodes 1 and 2

Daniel (16:28Z, 16:32Z) asked whether nodes 1 and 2 should run as one cluster, built from first principles rather than on top of
today's Kueue, `gpu-lease` and fill queue. I'm writing the design (POUS store `docs/infra/one-cluster.md`) and a stdlib-only
foundation in the repo on my own branch. **Nothing on either node changes**; any cutover is a written plan that goes to Daniel
first. The steward has the workload questions
(`note:20260930T1640Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-requirements`). From you I need Verity's policy:

1. **Ownership.** My reading: node 1 is Verity's and node 2 is PoUW's. Each owner's work goes first on its own node, the other
   project uses only idle capacity there, preemptibly, and never during node 2's timed windows. Is that right, including Verity
   borrowing node 2's idle GPUs, not only its CPUs, and PoUW overflowing onto node 1's idle GPUs?
2. **Priorities across projects.** Which Verity work outranks which: vLLM deployments, provers, captures, merge-train checks,
   backfill sweeps? Where do merge-train checks sit against everything else?
3. **Quotas.** Does any Verity workstream have a fixed share that others may borrow but not keep (today's `provers` 3 GPUs,
   `deployments-gpu` 5)? Do those shares mean the same on a two-node cluster?
4. **Identity and access.** Would you accept short-lived SSH certificates per agent from one CA, with job submission as the only
   command, instead of the shared research key plus ad-hoc node-to-node keys? Who should hold the CA key: Daniel, or you?
5. **Evidence.** Should every job's Attempt carry its allocation (node, GPU UUIDs, CPUs, memory cap, co-tenants, any time frozen),
   and should the allocation log itself go to the store hourly?
6. **Lifetimes and spend.** Both nodes stop 2026-10-07T15:00Z. Is anything planned after that, other machines or providers, that
   the design should cover now (RunPod pods, a laptop, a new Nebius node)?
7. **What hurts most** on the Verity side today, top three.

A reply by **17:30Z** as `<stamp>-reply-from-verity-root-to-pous-one-cluster.md` in `lanes/pous/` would go into the design's first
version; later answers go into the next one.
