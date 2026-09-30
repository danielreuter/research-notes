---
id: 20260930T2126Z-handoff-from-kueue-fold-builds-move-to-node2-automatically
campaign: one-pool
lane: kueue-fold
kind: handoff
status: open
repo: verity
origin: bc-d5ffe46d-a8e4-54da-9e9f-0dc724be9bf0
---
From 2:26 PM PDT on, a dispatcher Build that Kueue holds for 2 minutes on node 1's memory or CPU quota moves to node 2 by itself (`n2_build.sh offload --loop`, tmux `n2-offload` on node 1), and its Commit returns to node 1 under the same dispatcher key; 2 moved so far (`vllm-epoch-run/cov-g019`, `cov-n001`), each logged as `"ev": "moved"` in `/workspace/jobs/dispatch/log.jsonl`.
