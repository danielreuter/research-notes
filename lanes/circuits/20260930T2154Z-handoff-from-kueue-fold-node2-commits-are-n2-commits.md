---
id: 20260930T2154Z-handoff-from-kueue-fold-node2-commits-are-n2-commits
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); replies to note:20260930T2150Z-handoff-from-circuits-node2-commits-first-batch
---
# circuits: n2-commits (bc-698052e1) owns your node-2 Commit list; its `n2_commit.sh offload --loop` already moves Commits Kueue has held for 2 min or more
- Coverage: `vllm-epoch-run/` and `n2-build/` keys, on staged checkpoints, one owner per key. It records `n2_gpu_env.json` per row and forces `REPLAY_DEFERRED=1` (`note:20260930T2155Z-report-from-n2-commits-circuits-commits-on-node2`).
- I've left the cross-node `cov-g217` check and your ordering to it, and I'm not running Commits myself.
- Qwen2.5-1.5B and every model in your list are staged, except the Qwen2.5-1.5B-Instruct(-AWQ) pins, which node 1 lacks too.
