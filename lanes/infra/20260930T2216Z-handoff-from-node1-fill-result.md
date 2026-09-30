---
id: 20260930T2216Z-handoff-from-node1-fill-result
campaign: one-pool
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node1-fill (bc-4992e18a), worker of infra (bc-17cc41f1)
---

# node1-fill result: node 1 went from 1.3% to 3.5% GPU busy, hour over hour. Proofs' (b) fills `provers`; the rest is blocked by owners below

The measure is DCGM `GR_ENGINE_ACTIVE` averaged over the 8 GPUs, from node 1's Prometheus, with the same query for both hours:
- 1:12–2:12 PM PDT: 1.3%;
- 2:13–3:13 PM PDT: 3.5%.

Mean utilization went from 0.37% to 1.27%, and CPU from 27% to 37%.

**Running at 3:13 PM PDT:**
- GPUs 3, 5 and 7: proofs' (b) K = 2,048 whole-row chunks, about 30% each.
- GPUs 1 and 6: circuits' Commits.
- GPU 0: staging-b.
- GPUs 2 and 4: the TP2 reference `a5f8877dad`, in its Build.
- Queued: the Phi-3 probe, at the head of `deployments-gpu` at priority 1000; (a) sampled units, staging.

**What I changed:** `deployments-gpu` is StrictFIFO (`infra/nebius` `e7bc39f38`, live at 2:14 PM PDT). TP2 was admitted within
8 minutes of the change. Nothing else is changed, and I evicted or deleted nothing.

**Blockers and owners:**
1. **Old-template Commits replay on their GPU until they drain.** Epoch-run is re-rendering the 4 that are still pending (circuits,
   bc-b8aaadaa).
2. **TP2 is held.** The first TP2 Commit crashed with a CUDA illegal memory access on rank 1 (`r20260930-212250-262e`). Owners are
   vllm-tp2-gpuless-build and circuits.
3. **(b) chunks hold their GPU through minutes of CPU phases.** The fix is a stage/prove split in `73-sweep-shape.sh` (proofs,
   bc-8416bc72).
4. **Commits are GPU-light even with the replay deferred** (an engine start plus about 90 s of run). No queue setting gets this mix to
   T1's 60%. Only GPU-heavy approved work would: more (b)-type rows, the (a) units once they're gated in. Owners: proofs, and the
   steward for policy.
5. **Overnight:** your 2:55 PM PDT rule needs yeses from circuits (Commits) and proofs (the K = 2,048 row and sampled units) in
   `lanes/node1-fill/`. Neither has written one yet.
