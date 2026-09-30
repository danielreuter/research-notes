---
id: 20260930T2145Z-handoff-from-infra-586-followups-plan
campaign: verity
lane: cluster-build
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# cluster-build: the follow-ups to #586, taken from verity-top's scheduling-practice survey. Don't reopen #586; these go in follow-up PRs after it merges

Source: the scheduling-practice survey, "Copy into #586", items 1–8. Its verdict: moving data node to node isn't binding (90 GB
takes 1–2.6 min over `vy-cluster`); going through R2 is (about 20 MB/s custody, so hours). So small jobs placed by the scheduler are
right, with locality priced as a cost.

**Tonight: none of these.** Tonight is T3 only: `--queue`, the switch, the first lane job.

**By T4 (noon 1 Oct), in this order:**
1. **Sized inputs and a pin flag in `route.place`** (item 2).
   - Each input carries `size` and `movable`. A node's score is its expected wait plus `size / rate`, where the rate is the measured
     0.58–0.92 GB/s on one stream and about 1.6 GB/s on four.
   - A job waits up to its kind's delay bound for its local node.
   - Never price a move through R2.
   - The hard pins: PoUS's resident `C`; GPU 3's 513 GB of flags; sampled units, which stay beside their deployment's run.
2. **Replay RAM reserved when the Commit is admitted** (item 3): admit a Commit only if its replay's RAM fits on the same node. Phi-3
   B8 needs about 90 GB beside a 105 GB pinned pool. Cap each node's bytes of bundles not yet replayed.
3. **Pilot leases** (item 1): one lease runs same-key chunks back to back, e.g. one engine key for Commits, one model for censuses and
   70B evals, one grid for kernel fill. Proofs' shape jobs carry 50–200 shapes each; sampled units carry 5–10 deployments.
4. **Staging over `vy-cluster`, never through R2** (item 4, first half): a `stage` kind that runs once per node and model, and routing
   that prefers nodes already holding the weights. kueue-fold's `n2sync.sh` is already the mechanism; fold it into the kind.

**This week:**
- item 4's second half: content-addressed caches (weights by repo, revision and sha; Lean by `lean-deps.json` and toolchain;
  vLLM/Triton by tree hash), replication ahead of time, LRU eviction under node 2's 55%/60% watermarks;
- item 5, output memoization;
- item 6, quiet classes as reservations;
- item 8, backfill from each kind's p90 runtime, with every policy change replayed through the ledger first.

**Held until Daniel answers on the lighter design:** item 7, the posted price on leased GPU time. The per-kind and per-coordinator
metric (useful GPU-h per leased GPU-h) goes ahead regardless: it's accounting, not a price.
