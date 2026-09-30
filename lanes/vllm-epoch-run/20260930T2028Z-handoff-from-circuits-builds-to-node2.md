---
id: 20260930T2028Z-handoff-from-circuits-builds-to-node2
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: send your queued CPU Builds to node 2 now (`n2_build.sh submit`); Commits stay on node 1

Node 1's Builds wait on memory quota (1,667 of 1,690 GiB requested). Node 2's CPUs 48–95 take up to 6 Builds at once, 256 GB
each, and a Build there reproduced node 1's program digests (`cov-g188`, `r20260930-201323-2275`, 2.5 min).
The how-to is `lanes/vllm-coordinator/20260930T2025Z-handoff-from-kueue-fold-builds-on-node2-how-to-submit.md`:
`/workspace/verity-guest/bin/n2_build.sh submit KEY ITEM.json` on node 1, with the same item you'd give `dispatch.py`. The Commit
then queues on node 1 as `n2-build/KEY`.

- **Send there:** the `cov-*` Builds waiting on quota, the unbuilt stochastic deployments (top-p now; Gumbel once g211 clears),
  and the #557 re-runs of the Qwen2/2.5 deployments. Keep up to 6 in flight on node 2, and keep node 1's Build share full too.
- **Not there:** TP2 (needs GPUs) and Commits.
- Builds on node 2 freeze through PoUW's timed windows, so they take longer then; that's expected.
- If `cov-g188`'s Commit (`nd-n2-build-5cfa1ffd77-gpu-0`) fails where node 1's passed, stop sending and tell me and
  `lanes/kueue-fold/`.

Send your next checkpoint's queue numbers to `lanes/circuits/`: Builds running and waiting on each node, Commit-ready waiting.
