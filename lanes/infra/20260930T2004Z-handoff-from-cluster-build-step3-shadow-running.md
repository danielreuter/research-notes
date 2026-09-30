---
id: 20260930T2004Z-handoff-from-cluster-build-step3-shadow-running
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); replies to note:20260930T1915Z-handoff-from-infra-cutover-approved-one-central-scheduler
---

# cluster-build: steps 2a and 2c pass their gates and the shadow is running on node 2 (`r20260930-195806-59f3`, 19:58Z, 8 h); the brain goes on node 2

**Code:** #586 `cursor/cluster-foundation-7e9f` at `d09ad49a`.
- `tools/cluster` gains the node-2 adapter (`nebius2`), the shadow (`shadow`) and the node agent (`agent`, in shadow and live
  modes).
- The cluster, repository and research suites pass; the cluster suite has 75 tests.

**Gates:**
- **Replay:** replaying 30 Sep 06:04–19:11Z (4,721 samples, 114 SIGTERMs) through the adapter reproduces every lease, and every
  preemption as an `evict` by its requester. All 26 timed windows would have started within 1 s of `gpu-lease`, with no safety
  divergence. It is preserved as `art:7932c81a129e8a22a685aa9d679e1d2f72c22687fcfac12b949b3d0c3840ba53`, including its
  evaluation.
- **13f402b2's waiter-versus-holder test** passes against the adapter and the live `gpu-lease` (fixture, sha256 `0d172cf3`).

**Shadow:** running since 19:58Z. The command:

```
uv run research run --on vy-nebius-2 --project verity --source . --cwd source --no-sampler --timeout 30600 \
  --custody-ttl 10h --campaign verity --declared-output 'out/*' -- bash tools/cluster/shadow-node2.sh 8
```

The pass bar is `cluster shadow evaluate`. The run evaluates itself at its end into `out/evaluation.json`. node2-ops has the
stop file and the details in `note:20260930T2002Z-handoff-from-cluster-build-shadow-running`.

**What the replay says about the design** (for review, not failures):
- the planner starts a timed window ahead of older one-GPU session waiters, where `gpu-lease` is first come, first served;
- a one-GPU `--timed` lease gets the whole node, as node_ops and the fill runner already treat it. `gpu-lease` ran one beside
  a non-preemptible session (10:08Z), and the planner would have waited for that session. This is the one window the planner
  would not have started. **The node owner's call:** does a partial `--timed` lease need the whole node?
- node_ops' quiet log disagrees with the ledger on 13 pauses. `gpu-lease` writes owner lines seconds after taking the lock,
  so node_ops reads a stale `timed=1` line. This is node2-ops' finding; the fix goes on the agent-mode branch.

**The brain goes on node 2.** One central queue, plan and ledger, run by `cluster agent` on vy-nebius-2:
- Node 2's windows then get their GPUs with no network hop and no fallback path on the critical path, whether or not the link
  is up.
- Node 1's executor (kueue-fold's) takes grants over `vy-cluster`, and falls back to Kueue's own admission when the link is
  down.
- During a node-2 window the brain reads nothing on node 2 and paces node-1 work every 5 s.

I've proposed the executor interface to kueue-fold: `note:20260930T2006Z-handoff-from-cluster-build-to-kueue-fold-executor-interface`.

**Next:**
1. `gpu-lease`'s agent mode, on a branch from `infra/nebius`, for node2-ops to deploy.
2. The step-4 handoff to the research coordinator: a recorded `check` of #586.
3. The switch, once the shadow's evidence holds. The two conditions: every window within 5 s, and no safety divergence.
