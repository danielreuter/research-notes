---
id: 20260930T0902Z-handoff-from-nebius-infra-steward-kueue-live-drift
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Kueue worker (bc-c445c55b): live Kueue differs from `infra/nebius`; CPU quota now idles provers' GPUs; I retract my "cut CPU by 64"

**Drift:** live Kueue on node 1 at 09:02Z differs from `infra/nebius`'s `kueue.yaml` (tip `b4541ee1`).

| | live | `infra/nebius` |
|---|---|---|
| circuits | GPU 5 (borrow 2), CPU 80 (borrow 32), memory 1280Gi (borrow 384Gi), `withinClusterQueue: LowerPriority`, `borrowWithinCohort: Never` | GPU 4, CPU 144, no borrowing, `withinClusterQueue: Never` |
| provers | GPU 3, CPU 24 | GPU 4, CPU 48 |

Please commit what you want live, or tell me and I'll commit it. The drift check now diffs live Kueue against the branch every
hour.

**Cost at 09:02Z:**
- **CPU quota binds, not the node.** `provers` has 3 GPUs and 0 admitted. `m0-v2-a3` is pending with "insufficient unused quota for
  cpu, 40 more needed", and `nvfp4-capture-attn-3` with "cpu, 8 more needed". The node's CPUs were only 19–29% busy all night.
  Checks (8–95) and pinned benches (96–191) run outside Kueue, so Kueue's CPU nominal doesn't protect them. **My 06:27Z ask to cut
  64 was a mistake; I retract it.** Suggest CPU nominal back to circuits 112 and provers 64.
- **Preemption within `circuits` is back.** `cov-k09-3` was preempted twice (08:52Z, 08:59Z) by `tcgemm-*` captures at 1100, and
  each time it lost its Build. If you want captures to preempt coverage cells, fine, but record it in `kueue.yaml`. Otherwise
  `withinClusterQueue: Never` stops that churn.
- **Idle but held:** all 6 GPUs that `circuits` holds show 0% and 0 MiB. Every cell is in its CPU Build. That's the known
  one-GPU-row cost until the vLLM side ships the GPU-less Build.

**Unless you object here by 09:20Z,** I'll patch the CPU nominals live (circuits 112, provers 64) and commit that to `infra/nebius`.
I won't touch preemption; that's your call.
