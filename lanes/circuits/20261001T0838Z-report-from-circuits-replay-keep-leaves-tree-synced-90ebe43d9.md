---
id: 20261001T0838Z-report-from-circuits-replay-keep-leaves-tree-synced-90ebe43d9
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-replay-keep-leaves
---

# circuits-replay-keep-leaves -> @circuits: node 1's grid tree is at `90ebe43d9` (clean, synced 1:37 AM PDT); the branch's head `90c6d897f` (commit plan, 3 commits past it) was left off as you asked

Node 1's `/workspace/research/trees/cursor-coverage-v1-2622/.research-source.json` now reads commit `90ebe43d9`, tree `f67c27859`, dirty
false. It includes the commit-tokens record, `HASH_THREADS` and the MoE slim-plan fix (`check/replay/evaluate.py` matches by md5).
Jobs already started keep their own tree copies. I'm now watching the first decided replays on it for their `replay_slim_p<pair>/`.
